from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

with DAG(
    dag_id="monitor_tablespaces",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 1 * * *",  # Diario a la 1 AM
    catchup=False,
    tags=["monitoring", "tablespaces"],
) as dag:

    # Inicio
    begin = DummyOperator(
        task_id="begin"
    )

    # Verificar tamaños de tablas
    table_sizes = BashOperator(
        task_id="check_table_sizes",
        bash_command=r"""
psql -U system -d business_metrics_new << 'EOF'
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size, 
       pg_total_relation_size(schemaname||'.'||tablename) / 1024 / 1024 AS size_mb 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
EOF
echo "Table sizes checked at $(date)"
""",
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Verificar uso de tablespaces
    tablespace_usage = BashOperator(
        task_id="check_tablespace_usage",
        bash_command=r"""
psql -U system -d business_metrics_new << 'EOF'
SELECT spcname, pg_size_pretty(pg_tablespace_size(spcname)) AS size 
FROM pg_tablespace;
EOF
echo "Tablespace usage checked at $(date)"
""",
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Crear tablespace ts1 si no existe
    create_tablespace = BashOperator(
        task_id="create_tablespace_if_not_exists",
        bash_command=r"""
RESULT=$(psql -U system -d business_metrics_new -t -c "SELECT COUNT(*) FROM pg_tablespace WHERE spcname='ts1';")
if [ "$RESULT" -gt 0 ]; then
  echo "Tablespace ts1 already exists"
else
  echo "Creating tablespace ts1..."
  psql -U system -d business_metrics_new << 'EOF'
CREATE TABLESPACE ts1 LOCATION '/var/lib/postgresql/tablespaces/ts1';
EOF
  echo "Tablespace ts1 created successfully"
fi
""",
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Verificar si tabla venta excede 100 MB y moverla a ts1
    move_venta_if_large = BashOperator(
        task_id="move_venta_to_tablespace_if_large",
        bash_command=r"""
VENTA_SIZE=$(psql -U system -d business_metrics_new -t -c "SELECT pg_total_relation_size('public.venta') / 1024 / 1024;")
echo "Venta table size: ${VENTA_SIZE} MB"
if [ $VENTA_SIZE -gt 100 ]; then
  echo "Venta table exceeds 100 MB. Moving to tablespace ts1..."
  psql -U system -d business_metrics_new << 'EOF'
ALTER TABLE venta SET TABLESPACE ts1;
EOF
  echo "Venta table moved to ts1 successfully at $(date)"
else
  echo "Venta table size is OK (${VENTA_SIZE} MB). No action needed."
fi
""",
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Verificar dónde están las tablas (en qué tablespace)
    verify_table_locations = BashOperator(
        task_id="verify_table_tablespace_locations",
        bash_command=r"""
psql -U system -d business_metrics_new << 'EOF'
SELECT c.relname AS table_name, 
       c.relkind AS type, 
       COALESCE(t.spcname, 'pg_default') AS tablespace 
FROM pg_class c 
LEFT JOIN pg_tablespace t ON c.reltablespace = t.oid 
WHERE c.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname='public') 
AND c.relkind IN ('r', 'i') 
ORDER BY c.relname;
EOF
""",
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Registrar metadata del monitoreo
    log_monitoring = BashOperator(
        task_id="log_monitoring_metadata",
        bash_command=r"""
echo "Tablespace monitoring completed at $(date)" >> /opt/airflow/backups/tablespace_log.txt
psql -U system -d business_metrics_new -t -c "SELECT 'Venta size: ' || pg_size_pretty(pg_total_relation_size('public.venta'));"
""",
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
    begin >> [table_sizes, tablespace_usage] >> create_tablespace >> move_venta_if_large >> verify_table_locations >> log_monitoring >> end
