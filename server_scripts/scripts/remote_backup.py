#!/usr/bin/python3

import fcntl, subprocess, os, json, yaml
import pymysql as mysql

import srvmanage_core as srvmanage

import rrbackup.fsutil as sfs
import rrbackup.core as core
import rrbackup.pipeline as pipeline
import rrbackup.s3_interface as interface

import rrbackup

base_path = "/root/remote_backup"

#=====================
# lock
#=====================
lockfile_path = base_path + '/lockfile'
lockfile = open(lockfile_path, 'a')
try: fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError: raise SystemExit('Locked by another process')

#=====================
# Read main config file
#=====================
with open('/root/srvmanage.yaml', 'r') as fle:
    config = yaml.load(fle.read(), Loader=yaml.SafeLoader)

srvmanage.db_host         = config['db_host']
srvmanage.db_user         = config['db_user']
srvmanage.db_pass         = config['db_pass']

#=====================
# Backup mysql databases
#=====================
print("Backing up databases")
srvmanage.backup_mysql_databases('/root/remote_backup/backup/mysql_backup/')

#=====================
# run backup
#=====================

# Assemble default configuration
config = core.default_config(interface)

# Read and merge configuration file
parsed_config = json.loads(sfs.file_get_contents(base_path + '/remote_bk_conf.json'))
core.validate_config(parsed_config)
config = core.merge_config(config, parsed_config)

# Setup the interface and core
conn = interface.connect(config)
config = pipeline.preprocess_config(interface, conn, config)
core.init(interface, conn, config)

print('Running backup')
core.backup(interface, conn, config)

#=====================
# unlock
#=====================
fcntl.flock(lockfile, fcntl.LOCK_UN)
os.remove(lockfile_path)

