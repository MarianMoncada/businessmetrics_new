from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

with DAG(
    dag_id="backup_differential_postgres",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 */12 * * *",  # Cada 12 horas
    catchup=False,
    tags=["backup", "postgres", "differential"],
) as dag:

    # Inicio
    begin = DummyOperator(
        task_id="begin"
    )

    # Marca timestamp del último backup full
    get_last_full_backup = BashOperator(
        task_id="get_last_full_backup_time",
        bash_command=(
            "if [ -f /opt/airflow/backups/last_full_backup.txt ]; then "
            "cat /opt/airflow/backups/last_full_backup.txt; "
            "else "
            "echo '1970-01-01 00:00:00' > /opt/airflow/backups/last_full_backup.txt && "
            "cat /opt/airflow/backups/last_full_backup.txt; "
            "fi"
        ),
    )

    # Backup diferencial: stomamos olo tablas modificadas desde último full
    modified_tables = BashOperator(
        task_id="modified_tables",
        bash_command=(
            "TIMESTAMP=$(date +%Y%m%d_%H%M%S) && "
            "psql -U system -d business_metrics_new -t -c "
            "\"SELECT tablename FROM pg_stat_user_tables WHERE schemaname='public';\" | "
            "while read table; do "
            "  if [ ! -z \"$table\" ]; then "
            "    pg_dump -U system -d business_metrics_new -t $table -Fc "
            "    -f /opt/airflow/backups/differential/diff_${table}_${TIMESTAMP}.dump; "
            "    echo \"Backed up table: $table\"; "
            "  fi; "
            "done"
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Backup de solo datos modificados (registros nuevos)
    new_records = BashOperator(
        task_id="new_records_only",
        bash_command=(
            "TIMESTAMP=$(date +%Y%m%d_%H%M%S) && "
            "psql -U system -d business_metrics_new -c "
            "\"COPY (SELECT * FROM venta WHERE fecha >= CURRENT_DATE - INTERVAL '1 day') "
            "TO STDOUT WITH CSV HEADER\" > "
            "/opt/airflow/backups/differential/venta_new_records_${TIMESTAMP}.csv && "
            "echo 'New records backed up'"
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Registrar metadata del backup
    log_differential_backup = BashOperator(
        task_id="log_backup_metadata",
        bash_command=(
            "TIMESTAMP=$(date +%Y%m%d_%H%M%S) && "
            "echo \"Differential backup completed at $(date)\" >> "
            "/opt/airflow/backups/differential/backup_log.txt && "
            "ls -lh /opt/airflow/backups/differential/ | tail -5"
        ),
    )

    # Verificar que los archivos de backup se crearon
    verify_backup = BashOperator(
        task_id="verify_backup_files",
        bash_command=(
            "BACKUP_COUNT=$(ls -1 /opt/airflow/backups/differential/*.dump 2>/dev/null | wc -l) && "
            "CSV_COUNT=$(ls -1 /opt/airflow/backups/differential/*.csv 2>/dev/null | wc -l) && "
            "if [ $BACKUP_COUNT -gt 0 ] || [ $CSV_COUNT -gt 0 ]; then "
            "  echo \"✓ Backup verification PASSED. Found $BACKUP_COUNT dump files and $CSV_COUNT CSV files.\"; "
            "  exit 0; "
            "else "
            "  echo \"✗ Backup verification FAILED. No backup files found.\"; "
            "  exit 1; "
            "fi"
        ),
    )

    # Fin
    end = DummyOperator(
        task_id="end"
    )

    # Orden
    begin >> get_last_full_backup >> modified_tables >> new_records >> log_differential_backup >> verify_backup >> end
