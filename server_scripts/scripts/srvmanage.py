#!/usr/bin/python3
""" Script to manage virtual hosted websites with apache, php-fpm and mysql """

import os, sys, re, crypt, secrets, yaml, json, pymysql, fcntl
from typing import Tuple
import srvmanage_core as srvmanage

# Script can only be run by the root user
if os.geteuid() != 0:
    print('Must be root')
    quit()

# Lock for sanity check
try:
    lockfile = open('/tmp/srvmanage_lock', 'w')
    fcntl.flock(lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError: raise SystemExit('Could not lock')


# Load configuration
with open('/root/srvmanage.yaml', 'r') as fle:
    config = yaml.load(fle.read(), Loader=yaml.SafeLoader)

srvmanage.srv_ipv4        = config['srv_ipv4'] 
srvmanage.srv_ipv6        = config['srv_ipv6'] 
srvmanage.srvname         = config['srvname'] 
srvmanage.apache_confdir  = config['apache_confdir']
srvmanage.php_confdir     = config['php_confdir']
srvmanage.fpm_sock_prefix = config['fpm_sock_prefix']
srvmanage.php_version     = config['php_version']
srvmanage.webroot         = config['webroot']
srvmanage.reporoot        = config['reporoot']

srvmanage.db_host         = config['db_host']
srvmanage.db_user         = config['db_user']
srvmanage.db_pass         = config['db_pass']


####################################################################
# Handle command line interface
####################################################################
def read_site_name() -> str:
    if len(sys.argv) < 3: raise SystemExit('Please specify site name.')

    sitename = sys.argv[2]

    if not (len(sitename) < 14 and re.match('^[a-zA-Z0-9]+$', sitename) != None):
        raise SystemExit("Site name is invalid.")

    return sitename


#--------------------------------
if len(sys.argv) == 1 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print("""
usage: srvmanage.py [option] [sitename]

options:
create  - Create a website
delete  - delete a website
enable  - Enable a website
disable - Disable a website
list    - get a list of sites and credentials, either
          in flat format or json (-j)

Site name must be less than 16 characters and contain only
alphanumeric characters.
""")
    raise SystemExit()

#--------------------------------
# UI Switch
#--------------------------------
if sys.argv[1] == 'create':
    sitename = read_site_name()

    if srvmanage.db_get_site(sitename) is not None: raise SystemExit('Site allready exists')

    print('creating site...')

    password = srvmanage.create_system_user(sitename)
    srvmanage.create_apache_vhost(sitename)
    srvmanage.create_php_fpm_config(sitename)
    srvmanage.create_git_repo_for_website(sitename)

    db_name, db_password = srvmanage.create_mysql_database(sitename)

    srvmanage.db_store_new_site(sitename, 1, password, db_password)

    srvmanage.enable_apache_vhost(sitename)
    srvmanage.restart_apache2()
    srvmanage.restart_php_fpm()

    print()
    print("-------------------------------------")
    print("ssh user       " + sitename)
    print("ssh password   " + password)
    print() 
    print("db username    " + sitename)
    print("db_password    " + db_password)
    print("db_name        " + db_name)
    print("-------------------------------------")


#++++++++++++++++++++++++++++++++++
elif sys.argv[1] == 'delete':
    print('deleteing site...')

    sitename = read_site_name()
    srvmanage.disable_apache_vhost(sitename)
    srvmanage.delete_vhost(sitename)
    srvmanage.delete_mysql_database(sitename)
    srvmanage.delete_system_user(sitename)

    srvmanage.db_delete_site(sitename)

    srvmanage.restart_apache2()
    srvmanage.restart_php_fpm()

#++++++++++++++++++++++++++++++++++
elif sys.argv[1] == 'enable':
    print('enabling site...')

    sitename = read_site_name()
    srvmanage.enable_apache_vhost(sitename)
    srvmanage.restart_apache2()

    srvmanage.db_set_site_status(sitename, 1)

#++++++++++++++++++++++++++++++++++
elif sys.argv[1] == 'disable':
    print('disabling site...')

    sitename = read_site_name()
    srvmanage.disable_apache_vhost(sitename)
    srvmanage.restart_apache2()

    srvmanage.db_set_site_status(sitename, 0)

#++++++++++++++++++++++++++++++++++
elif sys.argv[1] == 'list':

    sites = srvmanage.db_get_sites()

    if len(sys.argv) > 2 and sys.argv[2] == '-j':
        print(json.dumps(sites))

    else:
        for site in sites:
            print('Name:   ' + site['name'])
            print('Status: ' + str(site['status']))
            print('DB:     ' + str(site['sqlpass']))
            print('SSH:    ' + str(site['sshpass']))
            print()

else:
    print('Unknown command')

