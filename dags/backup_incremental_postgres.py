from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

with DAG(
    dag_id="backup_incremental",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    tags=["backup", "postgres", "incremental"],
) as dag:

    # Inicio
    begin = DummyOperator(
        task_id="begin"
    )

    # Crea backup base si no existe
    base_backup = BashOperator(
        task_id="create_base_backup",
        bash_command=(
            "if [ ! -d /opt/airflow/backups/base_backup ]; then "
            "  echo \"Creating base backup...\"; "
            "  pg_basebackup -U system -D /opt/airflow/backups/base_backup -Fp -Xs -P && "
            "  echo \"Base backup created at $(date)\" > /opt/airflow/backups/base_backup_created.txt; "
            "else "
            "  echo \"Base backup already exists. Skipping...\"; "
            "fi"
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Archivar WAL files actuales
    archive_wal = BashOperator(
        task_id="wal_files",
        bash_command=(
            "psql -U system -d business_metrics_new -c 'SELECT pg_switch_wal();' && "
            "TIMESTAMP=$(date +%Y%m%d_%H%M%S) && "
            "echo \"WAL files archived at $(date)\" >> /opt/airflow/backups/wal_archive/wal_backup_log.txt && "
            "echo ${TIMESTAMP} > /opt/airflow/backups/wal_archive/last_backup.txt"
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Verificar archivos WAL
    verify_wal = BashOperator(
        task_id="verify_wal_archive",
        bash_command=(
            "WAL_COUNT=$(ls -1 /opt/airflow/backups/wal_archive/ 2>/dev/null | grep -v '.txt' | wc -l) && "
            "if [ $WAL_COUNT -gt 0 ]; then "
            "  echo \"✓ WAL verification PASSED. Found $WAL_COUNT WAL files.\"; "
            "  ls -lh /opt/airflow/backups/wal_archive/ | tail -10; "
            "  exit 0; "
            "else "
            "  echo \"✗ WAL verification FAILED. No WAL files found.\"; "
            "  exit 1; "
            "fi"
        ),
    )

    # Fin
    end = DummyOperator(
        task_id="end"
    )

    # Orden
    begin >> base_backup >> archive_wal >> verify_wal >> end
