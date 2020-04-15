#!/usr/bin/python3
import os, fcntl, sys
from pathlib import Path

path = Path(sys.argv[1])
account = 'root@robehickman.com'

os.system("cd " + str(path))

#Lock to prevent two simultaneous sync attempts, as we are calling with chron
lockfile = open(str(path / 'lock'), 'w')
fcntl.flock(fd, LOCK_EX | LOCK_NB)

# Run the backup
print("-- Backup Mysql --")
os.system(f"ssh {account} 'python /root/sql_backup.py'")
os.system(f"rsync -a {account}:/root/db_backup/ ./db_backup --delete")

print("-- Backup Apache --")
os.system(f"rsync -a {account}:/etc/apache2/ ./apache_conf --delete")

print("-- Backup PHP --")
os.system(f"rsync -a {account}:/etc/php/ ./php_conf --delete")

print("-- Backup HTTP --")
os.system(f"rsync -a {account}:/srv/http/ --exclude=*.git* ./http --delete")

print("-- Committing changes to git --")
os.system("cd db_backup")
os.system("git add .")
os.system("git commit -m 'backup'")
os.system("git gc")
os.system("cd " + str(path))

os.system("date > last_run.txt")

# Unlock
fcntl.flock(fd, LOCK_UN)

