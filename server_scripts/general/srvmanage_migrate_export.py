#!/usr/bin/python

import os, sys
import sqlite3
import json
import sqlite3 as lite
import yaml
import pymysql as mysql

import srvmanage_core as srvmanage


# Load configuration
with open('/root/srvmanage.yaml', 'r') as fle:
    config = yaml.load(fle.read(), Loader=yaml.SafeLoader)

srvmanage.db_host         = db_hostconfig['db_host']
srvmanage.db_user         = config['db_user']
srvmanage.db_pass         = config['db_pass']


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
srvmanage.backup_mysql_databases('/root/export/mysql/')


