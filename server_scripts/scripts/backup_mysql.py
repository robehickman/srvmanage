#!/usr/bin/python3
# Backup databases

import os, yaml, fcntl
import pymysql as mysql

# Lock for sanity check
try:
    lockfile = open('/tmp/mysql_backup_lock', 'w')
    fcntl.flock(lockfile, fcntl.LOCK_EX)
except IOError: raise SystemExit('Could not lock')

print("-- Backing up databases -- ")


# Load configuration
with open('/root/srvmanage.yaml', 'r') as fle:
    config = yaml.load(fle.read(), Loader=yaml.SafeLoader)

db_host         = config['db_host']
db_user         = config['db_user']
db_pass         = config['db_pass']

# Make sure data dir exists
try:
    os.makedirs('/root/mysql_backup')
except OSError as e:
    pass

# delete previous backup
os.system('rm -rf /root/mysql_backup/*') 

# ==================
cnx = mysql.connect (host = db_host, user = db_user, passwd = db_pass)
cursor = cnx.cursor()

cursor.execute ("show databases")
data = cursor.fetchall()

data = [i for i in data if i[0] not in ['information_schema', 'mysql', 'performance_schema']]

for row in data:
    print('Backing up', row[0])
    os.system("mysqldump -u "+db_user+" -p"+db_pass+" -h localhost "+
         "--lock-tables=false --single-transaction  "+row[0]+" > /root/mysql_backup/"+row[0]+"_backup.sql");


