#!/usr/bin/python

import os, sys
import sqlite3
import json
import sqlite3 as lite
import yaml
import pymysql as mysql


# Load configuration
with open('/root/srvmanage.yaml', 'r') as fle:
    config = yaml.load(fle.read(), Loader=yaml.SafeLoader)

db_host         = config['db_host']
db_user         = config['db_user']
db_pass         = config['db_pass']

# Export sites to JSON
sq_con = lite.connect('sites.db')

cur = sq_con.cursor()    
cur.execute("SELECT * FROM sites")

data = cur.fetchall()

sites = []
for row in data:
    sites.append({
        'site_name': row[1],
        'enabled'  : row[2],
        'sshpass'  : row[3],
        'dbpass'   : row[4],
    })

os.makedirs('/root/export')

with open('/root/export/sites.json', 'w') as f:
    f.write(json.dumps(sites))


# Export databases
os.makedirs('/root/export/mysql')

cnx = mysql.connect (host = db_host, user = db_user, passwd = db_pass)
cursor = cnx.cursor()

cursor.execute ("show databases")
data = cursor.fetchall()

data = [i for i in data if i[0] not in ['information_schema', 'mysql', 'performance_schema']]

for row in data:
    print('Backing up', row[0])
    os.system("mysqldump -u "+db_user+" -p"+db_pass+" -h localhost "+
         "--lock-tables=false --single-transaction  "+row[0]+" > /root/export/mysql/"+row[0]+"_backup.sql");





