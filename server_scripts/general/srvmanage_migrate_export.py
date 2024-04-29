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

srvmanage.db_host         = config['db_host']
srvmanage.db_user         = config['db_user']
srvmanage.db_pass         = config['db_pass']

data = srvmanage.db_get_sites()

sites = []
for row in data:
    sites.append({
        'site_name': row['name'],
        'enabled'  : row['status'],
        'sshpass'  : row['sshpass'],
        'dbpass'   : row['sqlpass'],
    })

os.makedirs('/root/export')

with open('/root/export/sites.json', 'w') as f:
    f.write(json.dumps(sites))

# Export databases
os.makedirs('/root/export/mysql')
srvmanage.backup_mysql_databases('/root/export/mysql/')

