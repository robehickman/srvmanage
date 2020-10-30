#!/usr/bin/python3
# Backup databases

import os, yaml, fcntl
import srvmanage_core as srvmanage

# Lock for sanity check
try:
    lockfile = open('/tmp/mysql_backup_lock', 'w')
    fcntl.flock(lockfile, fcntl.LOCK_EX)
except IOError: raise SystemExit('Could not lock')

print("-- Backing up databases -- ")


# Load configuration
with open('/root/srvmanage.yaml', 'r') as fle:
    config = yaml.load(fle.read(), Loader=yaml.SafeLoader)

srvmanage.db_host         = config['db_host']
srvmanage.db_user         = config['db_user']
srvmanage.db_pass         = config['db_pass']

srvmanage.backup_mysql_databases('/root/mysql_backup/')

