from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

with DAG(
    dag_id="restore_differential",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual only
    catchup=False,
    tags=["restore", "postgres", "differential"],
) as dag:

    # Inicio
    begin = DummyOperator(
        task_id="begin"
    )

    # Listar backups diferenciales disponibles
    differential_backups = BashOperator(
        task_id="list_available_backups",
        bash_command=(
            "echo 'Available differential backups:' && "
            "echo '--- Dump files ---' && "
            "ls -lth /opt/airflow/backups/differential/*.dump 2>/dev/null | head -10 || "
            "echo 'No differential dump files found' && "
            "echo '--- CSV files ---' && "
            "ls -lth /opt/airflow/backups/differential/*.csv 2>/dev/null | head -10 || "
            "echo 'No CSV files found'"
        ),
    )

    # Restaurar tablas desde backups diferenciales
    restore_differential = BashOperator(
        task_id="restore_differential_dumps",
        bash_command=(
            "cd /opt/airflow/backups/differential && "
            "DUMP_COUNT=0 && "
            "for dump in diff_*.dump; do "
            "  if [ -f \"$dump\" ]; then "
            "    echo \"Restoring $dump...\"; "
            "    pg_restore -U system -d business_metrics_new --clean --if-exists \"$dump\" 2>&1 | head -5; "
            "    DUMP_COUNT=$((DUMP_COUNT + 1)); "
            "  fi; "
            "done && "
            "echo \"✓ Restored $DUMP_COUNT differential dump files at $(date)\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Restaurar datos CSV (registros nuevos)
    restore_data = BashOperator(
        task_id="restore_csv_records",
        bash_command=r"""
LATEST_CSV=$(ls -t /opt/airflow/backups/differential/venta_new_records_*.csv 2>/dev/null | head -1)
if [ ! -z "$LATEST_CSV" ]; then
  echo "Restoring CSV: $LATEST_CSV"
  
  # Crear tabla temporal
  psql -U system -d business_metrics_new << 'EOF'
CREATE TEMP TABLE venta_temp (LIKE venta INCLUDING ALL);
EOF
  
  # Cargar CSV a tabla temporal
  psql -U system -d business_metrics_new -c "COPY venta_temp FROM STDIN WITH CSV HEADER" < "$LATEST_CSV"
  
  # Insertar solo registros nuevos (que no existen)
  psql -U system -d business_metrics_new << 'EOF'
INSERT INTO venta 
SELECT * FROM venta_temp 
WHERE id_venta NOT IN (SELECT id_venta FROM venta)
ON CONFLICT (id_venta) DO NOTHING;
EOF
  
  echo "CSV data restored successfully at $(date)"
else
  echo "No CSV files found to restore"
fi
""",
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

        # Verificar datos restaurados
    verify_restored_data = BashOperator(
        task_id="verify_restored_data",
        bash_command=(
            "echo \"=== Verification Report ===\" && "
            "psql -U system -d business_metrics_new -c "
            "\"SELECT 'Total ventas: ' || COUNT(*) FROM venta;\" && "
            "psql -U system -d business_metrics_new -c "
            "\"SELECT 'Total clientes: ' || COUNT(*) FROM cliente;\" && "
            "psql -U system -d business_metrics_new -c "
            "\"SELECT 'Total productos: ' || COUNT(*) FROM producto;\" && "
            "psql -U system -d business_metrics_new -c "
            "\"SELECT 'Total vendedores: ' || COUNT(*) FROM vendedor;\" && "
            "psql -U system -d business_metrics_new -c "
            "\"SELECT 'Total detalle_vta: ' || COUNT(*) FROM detalle_vta;\" && "
            "echo \"=== Table Sizes ===\" && "
            "psql -U system -d business_metrics_new -c "
            "\"SELECT tablename, pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size "
            "FROM pg_tables WHERE schemaname='public' ORDER BY tablename;\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )



    # Verificar integridad de datos
    verify_integrity = BashOperator(
        task_id="verify_data_integrity",
        bash_command=(
            "ERROR_COUNT=0 && "
            "psql -U system -d business_metrics_new -t -c "
            "\"SELECT COUNT(*) FROM venta WHERE id_cliente NOT IN (SELECT id_cliente FROM cliente);\" | "
            "xargs -I {} sh -c 'if [ {} -gt 0 ]; then echo \"✗ Found {} orphaned venta records\"; exit 1; fi' && "
            "echo \"✓ Data integrity check PASSED at $(date)\" || "
            "echo \"✗ Data integrity check FAILED\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Registrar metadata de restauración
    log_restore = BashOperator(
        task_id="log_restore_metadata",
        bash_command=(
            "echo \"Differential restore completed at $(date)\" >> /opt/airflow/backups/restore_log.txt && "
            "echo \"Restore operation logged successfully\""
        ),
    )

    # Fin
    end = DummyOperator(
        task_id="end"
    )

    # Orden
    begin >> differential_backups >> restore_differential >> restore_data >> verify_restored_data >> verify_integrity >> log_restore >> end
