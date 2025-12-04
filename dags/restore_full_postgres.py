from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

with DAG(
    dag_id="restore_full",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual, no automático
    catchup=False,
    tags=["restore", "postgres"],
) as dag:

    # Inicio
    begin = DummyOperator(
        task_id="begin"
    )

    # Listar backups disponibles
    list_backups = BashOperator(
        task_id="list_available_backups",
        bash_command=(
            "echo \"Available backups:\" && "
            "ls -lht /opt/airflow/backups/business_metrics_new_full_*.dump 2>/dev/null | head -10 || "
            "echo \"No backup files found!\""
        ),
    )

    # Seleccionar el backup más reciente
    select_latest_backup = BashOperator(
        task_id="select_latest_backup",
        bash_command=(
            "LATEST_BACKUP=$(ls -t /opt/airflow/backups/business_metrics_new_full_*.dump 2>/dev/null | head -1) && "
            "if [ -f \"$LATEST_BACKUP\" ]; then "
            "  echo \"Selected backup: $LATEST_BACKUP\" && "
            "  echo $LATEST_BACKUP > /opt/airflow/backups/restore_target.txt; "
            "else "
            "  echo \"✗ ERROR: No backup files found!\" && "
            "  exit 1; "
            "fi"
        ),
    )

    # Hacer backup de seguridad antes de restaurar
    safety_backup = BashOperator(
        task_id="create_safety_backup",
        bash_command=(
            "TIMESTAMP=$(date +%Y%m%d_%H%M%S) && "
            "echo \"Creating safety backup before restore...\" && "
            "pg_dump -U system -d business_metrics_new "
            "-F c -f /opt/airflow/backups/safety_backup_before_restore_${TIMESTAMP}.dump && "
            "echo \"✓ Safety backup created: safety_backup_before_restore_${TIMESTAMP}.dump\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Restaurar el backup completo
    restore_full = BashOperator(
        task_id="restore_full_backup",
        bash_command=(
            "BACKUP_FILE=$(cat /opt/airflow/backups/restore_target.txt) && "
            "echo \"Restoring from: $BACKUP_FILE\" && "
            "pg_restore -U system -d business_metrics_new "
            "--clean --if-exists "
            "\"$BACKUP_FILE\" && "
            "echo \"✓ Restore completed successfully at $(date)\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Verificar integridad después de restaurar
    verify_restore = BashOperator(
        task_id="verify_restore_integrity",
        bash_command=(
            "echo \"Verifying restored database...\" && "
            "psql -U system -d business_metrics_new -c "
            "\"SELECT 'venta: ' || COUNT(*) FROM venta; "
            "SELECT 'cliente: ' || COUNT(*) FROM cliente; "
            "SELECT 'producto: ' || COUNT(*) FROM producto; "
            "SELECT 'vendedor: ' || COUNT(*) FROM vendedor;\" && "
            "echo \"✓ Database verification completed\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # VACUUM ANALYZE después de restaurar
    vacuum_after_restore = BashOperator(
        task_id="vacuum_analyze_after_restore",
        bash_command=(
            "psql -U system -d business_metrics_new -c 'VACUUM ANALYZE;' && "
            "echo \"✓ VACUUM ANALYZE completed after restore\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Registrar metadata de la restauración
    log_restore = BashOperator(
        task_id="log_restore_metadata",
        bash_command=(
            "BACKUP_FILE=$(cat /opt/airflow/backups/restore_target.txt) && "
            "echo \"Restore completed at $(date) from: $BACKUP_FILE\" >> /opt/airflow/backups/restore_log.txt && "
            "psql -U system -d business_metrics_new -c "
            "\"SELECT 'Total tables: ' || COUNT(*) FROM pg_tables WHERE schemaname='public';\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Fin
    end = DummyOperator(
        task_id="end"
    )

    # Orden
    begin >> list_backups >> select_latest_backup >> safety_backup >> restore_full >> verify_restore >> vacuum_after_restore >> log_restore >> end
