import os, sys, re, crypt, secrets, yaml, json, pymysql, fcntl
from typing import Tuple

#+++++++++++++++++++++++++++++++++++++
srv_ipv4        = ''
srv_ipv6        = ''
srvname         = ''
apache_confdir  = ''
php_confdir     = ''
fpm_sock_prefix = ''
webroot         = ''
reporoot        = ''

db_host         = ''
db_user         = ''
db_pass         = ''


#+++++++++++++++++++++++++++++++++++++
def rand_passwd():
    return secrets.token_urlsafe(nbytes=20)

####################################################################
# Keep track of the sites that currently exist on the server
# in a database table
####################################################################
def db_connect() -> pymysql.connections.Connection :
    return pymysql.connect (host = db_host, user = db_user, passwd = db_pass,
                            charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)


#+++++++++++++++++++++++++++++++++++++
def db_get_site(name: str):
    conection = db_connect()
    cursor = conection.cursor()    
    cursor.execute ("use sites")
    cursor.execute("SELECT * FROM sites WHERE name='"+name+"'")
    data = cursor.fetchone()
    cursor.close()
    return data


#+++++++++++++++++++++++++++++++++++++
def db_get_sites():
    conection = db_connect()
    cursor = conection.cursor()    
    cursor.execute ("use sites")
    cursor.execute("SELECT * FROM sites")
    data = cursor.fetchall()
    cursor.close()
    return data

#+++++++++++++++++++++++++++++++++++++
def db_store_new_site(name: str, status: int, sshpass: str, sqlpass: str):
    conection = db_connect()
    cursor = conection.cursor()    
    cursor.execute ("use sites")
    cursor.execute(f"""
        insert into sites (
            name,
            status,
            sshpass,
            sqlpass
        ) values ( 
            '{name}',
            '{str(status)}',
            '{sshpass}',
            '{sqlpass}'
        ) """)

    conection.commit()
    cursor.close()


#+++++++++++++++++++++++++++++++++++++
def db_set_site_status(name: str, status: int):
    conection = db_connect()
    cursor = conection.cursor()    
    cursor.execute ("use sites")
    cursor.execute(f"update sites set status = '{str(status)}' where name='{name}'")
    conection.commit()
    cursor.close()


#+++++++++++++++++++++++++++++++++++++
def db_delete_site(name: str):
    conection = db_connect()
    cursor = conection.cursor()    
    cursor.execute ("use sites")
    cursor.execute(f"delete from sites where name='{name}'")
    conection.commit()
    cursor.close()


####################################################################
# Management of system user accounts
####################################################################
def create_system_user(sitename: str, password = None) -> str:
    if password is None:
        password = rand_passwd()

    crypt_pass = crypt.crypt(password,"22")
    os.system(f"useradd -s /bin/bash -M --home-dir {webroot}/{sitename} -p {crypt_pass} {sitename}")

    return password


#+++++++++++++++++++++++++++++++++++++
def delete_system_user(sitename: str) -> None:
    os.system(f"gpasswd -d www-data {sitename}") # remove group from www-data
    os.system(f"userdel  {sitename}")


####################################################################
# Management of virtual hosts
####################################################################
def create_apache_vhost(sitename: str, create_dirs = True) -> None:

    vhost = f"""
MDomain {sitename}.{srvname}

<VirtualHost [{srv_ipv6}]:80 {srv_ipv4}:80>
    ServerName {sitename}.{srvname}

    RewriteEngine On
    RewriteRule ^(.*)$ https://{sitename}.{srvname}$1 [L,R=301]
</VirtualHost>

<VirtualHost [{srv_ipv6}]:443 {srv_ipv4}:443>
    ServerName {sitename}.{srvname}
    DocumentRoot {webroot}/{sitename}/docs

    SSLEngine on

    ErrorLog  ${{APACHE_LOG_DIR}}/{sitename}_error.log
    CustomLog ${{APACHE_LOG_DIR}}/{sitename}_access.log combined

    ProxyPassMatch ^/(.*\.php(/.*)?)$ unix:{fpm_sock_prefix}-{sitename}.sock|fcgi://127.0.0.1:9000{webroot}/{sitename}/docs

    <Directory "{webroot}/{sitename}/docs">
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
    """.strip()

    with open(f"{apache_confdir}/{sitename}.conf",'w') as cfile:
        cfile.write(vhost)

    if create_dirs:
        # Create directories for web root
        os.mkdir(f"{webroot}/{sitename}")
        os.mkdir(f"{webroot}/{sitename}/docs")

        cfile = open(f"{webroot}/{sitename}/docs/index.html",'w')
        cfile.write('It works!')
        cfile.close()

        #copy ssh
        os.system(f"mkdir {webroot}/{sitename}/.ssh") 
        os.system(f"cp /root/ssh_keys/* {webroot}/{sitename}/.ssh/") 

        #fix permissions
        os.system(f"chown -Rf {sitename}:{sitename} {webroot}/{sitename}") 
        os.system(f"chmod -Rf 750 {webroot}/{sitename}") 
        os.system(f"usermod -a -G {sitename} www-data") 


#+++++++++++++++++++++++++++++++++++++
def create_php_fpm_config(sitename: str) -> None:

    php_conf = f"""
[{sitename}]
user   = {sitename}
group  = {sitename}
listen = {fpm_sock_prefix}-{sitename}.sock
listen.owner = www-data
listen.group = www-data
 
pm = dynamic
pm.max_children = 2
pm.start_servers = 1
pm.min_spare_servers = 1
pm.max_spare_servers = 1
 
security.limit_extensions = .php
    """.strip()

    with open(f"{php_confdir}/{sitename}.conf",'w') as cfile:
        cfile.write(php_conf)


#+++++++++++++++++++++++++++++++++++++
def create_git_repo_for_website(sitename: str) -> None:
    #set up bare git repo for access
    os.mkdir(f"{reporoot}/{sitename}")
    os.chdir(f"{reporoot}/{sitename}")
    os.system('git init --bare')

    # Initialise web root as a git repo create directories and set up git repo
    os.chdir(f"{webroot}/{sitename}")
    os.system('git init')
    os.system('git add .')
    os.system('git commit -m "Initial commit"')
    os.system(f"git remote add origin {reporoot}/{sitename}")
    os.system('git push --all origin')

#create hook script to update webroot
    hook = f"""
#!/bin/sh
cd {webroot}/{sitename}
echo 'Updating website'
env -i git reset --hard
env -i git pull origin master"""

    with open(f"{reporoot}/{sitename}/hooks/post-receive",'w') as cfile:
        cfile.write(hook)

    os.system(f"chmod +x {reporoot}/{sitename}/hooks/post-receive") 

    #fix permissions
    os.system(f"chown -Rf {sitename} {reporoot}/{sitename}") 
    os.system(f"chmod -Rf 700 {reporoot}/{sitename}") 


#+++++++++++++++++++++++++++++++++++++
def delete_vhost(sitename: str) -> None:
    os.system(f"rm -Rf {webroot}/{sitename}")
    os.system(f"rm -Rf {reporoot}/{sitename}")
    os.system(f"rm -Rf {apache_confdir}/{sitename}.conf")
    os.system(f"rm -Rf {php_confdir}/{sitename}.conf")


####################################################################
# Management of mysql databases
####################################################################
def create_mysql_database(sitename: str, db_password = None) -> Tuple[str, str]:
    if db_password is None:
        db_password = rand_passwd()

    db_name     = 'm_' + sitename

    connection = db_connect()
    cursor = connection.cursor()

    cursor.execute (f"CREATE USER '{sitename}'@'localhost' IDENTIFIED BY '{db_password}'")
    cursor.execute (f"CREATE DATABASE `m_%s`" % sitename)
    cursor.execute (f"""GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX,DROP,LOCK TABLES
        ON `m_%s`.* TO '%s'@'localhost'""" % (sitename, sitename))
    connection.commit()

    return db_name, db_password

#+++++++++++++++++++++++++++++++++++++
def delete_mysql_database(sitename: str) -> None:
    connection = db_connect()
    cursor = connection.cursor()

    try: cursor.execute (f"DROP DATABASE `m_{sitename}`")
    except pymysql.err.InternalError: pass

    try: cursor.execute (f"DROP USER '{sitename}'@'localhost'")
    except pymysql.err.InternalError: pass

    connection.commit()

#+++++++++++++++++++++++++++++++++++++
def backup_mysql_databases(target_basedir: str) -> None:
    if not target_basedir.endswith('/'):
        target_basedir += '/'

    # Make sure data dir exists
    try:
        os.makedirs(target_basedir)
    except OSError as e:
        pass

    # delete previous backup
    os.system('rm -rf ' + target_basedir + '*') 

    # ==================
    connection = db_connect()
    cursor = connection.cursor()

    cursor.execute ("show databases")
    data = cursor.fetchall()

    data = [i for i in data if i['Database'] not in ['information_schema', 'mysql', 'performance_schema']]

    for row in data:
        print('Backing up', row['Database'])
        os.system("mysqldump -u "+db_user+" -p"+db_pass+" -h localhost "+
             "--lock-tables=false --single-transaction  "+row['Database']+" > "+target_basedir+row['Database']+"_backup.sql");


####################################################################
# Apache virtual host management
####################################################################
def enable_apache_vhost(sitename):
    os.system('a2ensite '+sitename)

#+++++++++++++++++++++++++++++++++++++
def disable_apache_vhost(sitename):
    os.system('a2dissite '+sitename)

#+++++++++++++++++++++++++++++++++++++
def restart_apache2():
    os.system('service apache2 restart')

####################################################################
# PHP=fpm management
####################################################################
def restart_php_fpm():
    os.system('service php7.4-fpm restart')

