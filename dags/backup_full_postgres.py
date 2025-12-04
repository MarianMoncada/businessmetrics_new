from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

with DAG(
    dag_id="backup_full",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["backup", "postgres"],
) as dag:

    # Inicio
    begin = DummyOperator(
        task_id="begin"
    )

    # Backup completo
    backup_full = BashOperator(
        task_id="backup_full",
        bash_command=(
            "TIMESTAMP=$(date +%Y%m%d_%H%M%S) && "
            "pg_dump -U system -d business_metrics_new "
            "-F c -f /opt/airflow/backups/business_metrics_new_full_${TIMESTAMP}.dump && "
            "echo ${TIMESTAMP} > /opt/airflow/backups/last_full_backup.txt && "
            "echo \"Full backup completed at $(date)\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Registrar metadata del backup
    log_backup = BashOperator(
        task_id="log_backup_metadata",
        bash_command=(
            "echo \"Full backup completed at $(date)\" >> /opt/airflow/backups/backup_log.txt && "
            "ls -lh /opt/airflow/backups/*.dump | tail -3"
        ),
    )

    # Verificar que el archivo de backup se creó
    verify_backup = BashOperator(
        task_id="verify_backup_file",
        bash_command=(
            "LATEST_BACKUP=$(ls -t /opt/airflow/backups/business_metrics_new_full_*.dump 2>/dev/null | head -1) && "
            "if [ -f \"$LATEST_BACKUP\" ]; then "
            "  BACKUP_SIZE=$(stat -f%z \"$LATEST_BACKUP\" 2>/dev/null || stat -c%s \"$LATEST_BACKUP\" 2>/dev/null) && "
            "  if [ $BACKUP_SIZE -gt 1000 ]; then "
            "    echo \"✓ Backup verification PASSED. File: $LATEST_BACKUP, Size: $BACKUP_SIZE bytes\"; "
            "    exit 0; "
            "  else "
            "    echo \"✗ Backup file is too small (${BACKUP_SIZE} bytes). Backup may be corrupted.\"; "
            "    exit 1; "
            "  fi; "
            "else "
            "  echo \"✗ Backup verification FAILED. No backup file found.\"; "
            "  exit 1; "
            "fi"
        ),
    )

    # Limpiar backups antiguos (mantener últimos 7 días)
    cleanup_old_backups = BashOperator(
        task_id="cleanup_old_backups",
        bash_command=(
            "find /opt/airflow/backups/ -name 'business_metrics_new_full_*.dump' -type f -mtime +7 -delete && "
            "echo \"Old backups cleaned up. Remaining backups:\" && "
            "ls -lh /opt/airflow/backups/business_metrics_new_full_*.dump 2>/dev/null | wc -l"
        ),
    )

    # Fin
    end = DummyOperator(
        task_id="end"
    )

    # Orden 
    begin >> backup_full >> log_backup >> verify_backup >> cleanup_old_backups >> end
