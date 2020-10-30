#!/usr/bin/python3
import os, fcntl, sys
from pathlib import Path

path    = Path(sys.argv[1])
account = Path(sys.argv[2])

os.system("cd " + str(path))

#Lock to prevent two simultaneous sync attempts, as we are calling with cron
lockfile = open(str(path / 'lock'), 'w')
fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)

# Run the backup
print("-- Backup Mysql --")
os.system(f"ssh {account} backup_mysql.py")
os.system(f"mkdir -p {path / 'db_backup'}")
os.system(f"rsync -a {account}:/root/mysql_backup/ {path / 'db_backup' / 'mysql'} --delete")

print("-- Backup Apache --")
os.system(f"rsync -a {account}:/etc/apache2/ {path / 'apache_conf'} --delete")

print("-- Backup PHP --")
os.system(f"rsync -a {account}:/etc/php/ {path / 'php_conf'} --delete")

print("-- Backup HTTP --")
os.system(f"rsync -a {account}:/srv/http/ --exclude=*.git* {path / 'http'} --delete --exclude=.git*")

print("-- Committing changes to git --")

if not os. path. isdir(path / '.git'):
    os.system(f"git -C {path} init")

# TODO put everything in git for safety
os.system(f"git -C {path} add .")
os.system(f"git -C {path} commit -m 'backup'")
#os.system(f"git -C {path} gc")

os.system(f"date > {path / 'last_run.txt'}")

# Unlock
fcntl.flock(lockfile, fcntl.LOCK_UN)

