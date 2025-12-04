#!/bin/bash
echo "host replication system 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
psql -U system -d business_metrics_new -c "SELECT pg_reload_conf();"
