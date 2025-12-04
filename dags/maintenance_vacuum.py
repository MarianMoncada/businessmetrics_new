from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

with DAG(
    dag_id="maintenance_vacuum",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 2 * * 0",  # Domingos a las 2 AM
    catchup=False,
    tags=["maintenance", "postgres"],
) as dag:

    # Inicio
    begin = DummyOperator(
        task_id="begin"
    )

    # VACUUM ANALYZE completo de la base de datos
    vacuum_analyze = BashOperator(
        task_id="vacuum_analyze_db",
        bash_command=(
            "psql -U system -d business_metrics_new -c 'VACUUM ANALYZE;' && "
            "echo 'VACUUM ANALYZE completed at $(date)'"
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # VACUUM FULL ANALYZE en tabla venta (la más grande)
    vacuum_venta_table = BashOperator(
        task_id="vacuum_venta_table",
        bash_command=(
            "psql -U system -d business_metrics_new -c 'VACUUM FULL ANALYZE venta;' && "
            "echo 'VACUUM FULL ANALYZE venta completed at $(date)'"
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Verificar tuplas muertas después del VACUUM
    verify_vacuum = BashOperator(
        task_id="verify_vacuum_results",
        bash_command=r"""
psql -U system -d business_metrics_new << 'EOF'
SELECT tablename, n_dead_tup 
FROM pg_stat_user_tables 
WHERE schemaname='public' 
ORDER BY n_dead_tup DESC;
EOF
""",
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Registrar metadata del mantenimiento
        # Registrar metadata del mantenimiento
    log_maintenance = BashOperator(
        task_id="log_maintenance_metadata",
        bash_command=r"""
echo 'VACUUM maintenance completed at $(date)' >> /opt/airflow/backups/maintenance_log.txt
psql -U system -d business_metrics_new << 'EOF'
SELECT tablename, last_vacuum, last_analyze 
FROM pg_stat_user_tables 
WHERE schemaname='public';
EOF
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
    begin >> vacuum_analyze >> vacuum_venta_table >> verify_vacuum >> log_maintenance >> end
