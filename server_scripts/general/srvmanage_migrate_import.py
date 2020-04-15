#!/usr/bin/python3

import os, sys, re
import subprocess as sub
import random
import string
import pymysql
import json
import crypt
import yaml
from typing import Tuple

import srvmanage

# Load configuration
with open('/root/srvmanage.yaml', 'r') as fle:
    config = yaml.load(fle.read(), Loader=yaml.SafeLoader)

srvmanage.srv_ipv4        = config['srv_ipv4'] 
srvmanage.srv_ipv6        = config['srv_ipv6'] 
srvmanage.srvname         = config['srvname'] 
srvmanage.apache_confdir  = config['apache_confdir']
srvmanage.php_confdir     = config['php_confdir']
srvmanage.fpm_sock_prefix = config['fpm_sock_prefix']
srvmanage.webroot         = config['webroot']
srvmanage.reporoot        = config['reporoot']

srvmanage.db_host         = config['db_host']
srvmanage.db_user         = config['db_user']
srvmanage.db_pass         = config['db_pass']


####################################################################
def import_mysql_database(sitename: str, db_password: str) -> Tuple[str, str]:
    with open('/root/mysql.cnf', 'w') as f:
        f.write(f"""
[client]
user={sitename}
password={db_password}
database=m_{sitename}
        """.strip())

    os.system(f"mysql --defaults-extra-file=/root/mysql.cnf < /root/export/mysql/m_{sitename}_backup.sql")
    os.remove('/root/mysql.cnf')


####################################################################
with open('/root/export/sites.json', 'r') as f:
    sites = json.loads(f.read())

for site in sites:
    print(site)

    # Create system user
    srvmanage.create_system_user(site['site_name'], site['sshpass'])

    # Create database
    srvmanage.create_mysql_database(site['site_name'], site['dbpass'])

    # Import database
    srvmanage.import_mysql_database(site['site_name'], site['dbpass'])

    # create apache vhost
    srvmanage.create_apache_vhost(site['site_name'], False)

    # create php fpm confif
    srvmanage.create_php_fpm_config(site['site_name'])

    # enable vhost if needed
    if site['enabled'] == 1:
        srvmanage.enable_apache_vhost(site['site_name'])

    # store the site in the db
    srvmanage.db_store_new_site(site['site_name'], site['enabled'], site['sshpass'], site['dbpass'])

    # Fix permissions, these files need to be copied manually
    sitename = site['site_name']
    os.system('chown -Rf '+sitename+':'+sitename+' '+webroot+'/'+sitename)
    os.system('chmod -Rf 750 '+webroot+'/'+sitename)

    os.system('chown -Rf '+sitename+' '+reporoot+'/'+sitename)
    os.system('chmod -Rf 700 '+reporoot+'/'+sitename)

    os.system('usermod -a -G '+sitename+' www-data')

