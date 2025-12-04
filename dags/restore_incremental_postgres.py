from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

with DAG(
    dag_id="restore_incremental",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual only
    catchup=False,
    tags=["restore", "postgres", "incremental"],
) as dag:

    # Inicio
    begin = DummyOperator(
        task_id="begin"
    )

    # Terminar conexiones activas antes de restaurar
    stop_postgres = BashOperator(
        task_id="stop_postgres_connections",
        bash_command=(
            "echo \"Terminating active connections to business_metrics_new...\" && "
            "TERMINATED=$(psql -U system -d postgres -t -c "
            "\"SELECT COUNT(*) FROM pg_stat_activity "
            "WHERE datname = 'business_metrics_new' AND pid <> pg_backend_pid();\") && "
            "psql -U system -d postgres -c "
            "\"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
            "WHERE datname = 'business_metrics_new' AND pid <> pg_backend_pid();\" && "
            "echo \"✓ Terminated $TERMINATED connections at $(date)\""
        ),
        env={
            "PGHOST": "postgres",
            "PGPORT": "5432",
            "PGPASSWORD": "PgVentas2025"
        },
    )

    # Verificar que existe base backup
    verify_base_exists = BashOperator(
        task_id="verify_base_backup_exists",
        bash_command=(
            "if [ -d /opt/airflow/backups/base_backup ]; then "
            "  echo \"✓ Base backup found\"; "
            "  du -sh /opt/airflow/backups/base_backup; "
            "  exit 0; "
            "else "
            "  echo \"✗ ERROR: Base backup not found at /opt/airflow/backups/base_backup\"; "
            "  echo \"Run backup_incremental DAG first to create base backup\"; "
            "  exit 1; "
            "fi"
        ),
    )

    # Restaurar base backup
    restore_base = BashOperator(
        task_id="restore_base_backup",
        bash_command=(
            "echo \"Preparing restore from base backup...\" && "
            "rm -rf /opt/airflow/backups/restore_temp && "
            "cp -r /opt/airflow/backups/base_backup /opt/airflow/backups/restore_temp && "
            "echo \"✓ Base backup copied to restore_temp at $(date)\" && "
            "du -sh /opt/airflow/backups/restore_temp"
        ),
    )

    # Verificar WAL files disponibles
    verify_wal_exists = BashOperator(
        task_id="verify_wal_files_exist",
        bash_command=(
            "WAL_COUNT=$(ls -1 /opt/airflow/backups/wal_archive/ 2>/dev/null | grep -v '.txt' | wc -l) && "
            "if [ $WAL_COUNT -gt 0 ]; then "
            "  echo \"✓ Found $WAL_COUNT WAL files for recovery\"; "
            "  ls -lth /opt/airflow/backups/wal_archive/ | head -10; "
            "  exit 0; "
            "else "
            "  echo \"⚠ Warning: No WAL files found. Recovery will use base backup only.\"; "
            "  exit 0; "
            "fi"
        ),
    )

    # Aplicar WAL files para recuperación point-in-time
    apply_wal = BashOperator(
        task_id="apply_wal_files",
        bash_command=(
            "echo \"Creating recovery configuration...\" && "
            "echo \"restore_command = 'cp /opt/airflow/backups/wal_archive/%f %p'\" > /opt/airflow/backups/restore_temp/recovery.conf && "
            "echo \"recovery_target_timeline = 'latest'\" >> /opt/airflow/backups/restore_temp/recovery.conf && "
            "echo \"✓ WAL recovery configuration created at $(date)\" && "
            "cat /opt/airflow/backups/restore_temp/recovery.conf"
        ),
    )

    # Verificar preparación de restauración
    verify_restore = BashOperator(
        task_id="verify_restore_ready",
        bash_command=(
            "echo \"=== Restore Preparation Summary ===\" && "
            "echo \"✓ Base backup size: $(du -sh /opt/airflow/backups/restore_temp | cut -f1)\" && "
            "echo \"✓ WAL files available: $(ls -1 /opt/airflow/backups/wal_archive/ 2>/dev/null | grep -v '.txt' | wc -l)\" && "
            "echo \"✓ Recovery config: $([ -f /opt/airflow/backups/restore_temp/recovery.conf ] && echo 'EXISTS' || echo 'MISSING')\" && "
            "echo \"\" && "
            "echo \"⚠ NEXT STEPS (Manual):\" && "
            "echo \"1. Stop PostgreSQL container: docker compose stop postgres\" && "
            "echo \"2. Backup current data: mv data/ data_backup/\" && "
            "echo \"3. Replace with restore: mv backups/restore_temp data/\" && "
            "echo \"4. Start PostgreSQL: docker compose up -d postgres\" && "
            "echo \"5. PostgreSQL will apply WAL files automatically\" && "
            "echo \"\" && "
            "echo \"Restore preparation completed at $(date)\""
        ),
    )

    # Registrar metadata de restauración
    log_restore_prep = BashOperator(
        task_id="log_restore_preparation",
        bash_command=(
            "echo \"Incremental restore prepared at $(date)\" >> /opt/airflow/backups/restore_log.txt && "
            "echo \"Base backup: $(du -sh /opt/airflow/backups/restore_temp | cut -f1)\" >> /opt/airflow/backups/restore_log.txt && "
            "echo \"WAL files: $(ls -1 /opt/airflow/backups/wal_archive/ | wc -l)\" >> /opt/airflow/backups/restore_log.txt"
        ),
    )

    # Fin
    end = DummyOperator(
        task_id="end"
    )

    # Orden
    begin >> stop_postgres >> verify_base_exists >> restore_base >> verify_wal_exists >> apply_wal >> verify_restore >> log_restore_prep >> end
