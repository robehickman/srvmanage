apt-get update
apt-get upgrade


# --------------------------------------------------------------------------
# Install system utils and tools needed to install other tools
# --------------------------------------------------------------------------
apt-get install -y htop git wget curl


# --------------------------------------------------------------------------
# Install mariadb
# --------------------------------------------------------------------------
apt-get install -y mariadb-server
service mysql start

# NOTE You need to set 'no engine substitution' option in config file manually

# --------------------------------------------------------------------------
# Install and setup apache2
# --------------------------------------------------------------------------
apt-get update
apt-get install -y apache2

a2enmod http2
a2enmod rewrite
a2enmod headers
a2enmod proxy_http
a2enmod proxy_fcgi
a2enmod ssl
a2enmod md
service apache2 restart

ACMECONF=$(cat << EOF
ServerAdmin mailto:robehickman@gmail.com
MDCertificateAgreement accepted
EOF
)
echo "$ACMECONF" > /etc/apache2/conf-enabled/zz_md_settings.conf


# --------------------------------------------------------------------------
# Install and setup PHP
# --------------------------------------------------------------------------
apt install -y apt-transport-https lsb-release ca-certificates wget
wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg
sh -c 'echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list' 
apt update 

apt-get install php8.3-fpm php8.3-{bcmath,bz2,intl,curl,gd,mbstring,mysqli,zip,imagick}
phpenmod mbstring


# --------------------------------------------------------------------------
# Install nodejs and rollup
# --------------------------------------------------------------------------
curl -fsSL https://deb.nodesource.com/setup_23.x -o /tmp/nodesource_setup.sh
bash /tmp/nodesource_setup.sh
apt install -y nodejs
npm install -g rollup


# --------------------------------------------------------------------------
# Used for media handling
# --------------------------------------------------------------------------
apt install timidity ffmpeg


# --------------------------------------------------------------------------
# Install cli imagemagick
# --------------------------------------------------------------------------
apt install imagemagick


# --------------------------------------------------------------------------
# Install cli abc notation converter
# --------------------------------------------------------------------------
apt install abcm2ps


# --------------------------------------------------------------------------
# Install lilypond
# --------------------------------------------------------------------------
wget https://gitlab.com/lilypond/lilypond/-/releases/v2.24.4/downloads/lilypond-2.24.4-linux-x86_64.tar.gz

tar -xvf lilypond-2.24.4-linux-x86_64.tar.gz 

mv -a lilypond-2.24.4 /opt

ln -s /opt/lilypond-2.24.4/bin/lilypond /usr/bin/lilypond
ln -s /opt/lilypond-2.24.4/bin/convert-ly /usr/bin/convert-ly

chown -R root:root /opt/lilypond-2.24.4
chown -R root:root /usr/bin/lilypond
chown -R root:root /usr/bin/convert-ly

chmod -R 755 /opt/lilypond-2.24.4
chmod -R 755 /usr/bin/lilypond
chmod -R 755 /usr/bin/convert-ly 


# --------------------------------------------------------------------------
# Install a few python packages
# --------------------------------------------------------------------------
apt inatall -y python3-pymysql
apt inatall -y python3-yaml


# --------------------------------------------------------------------------
# Install server management system
# --------------------------------------------------------------------------
git clone https://github.com/robehickman/srvmanage.git
cd srvmanage/server_scripts 
pip3 install --break-system-packages . 
cd ../..


# --------------------------------------------------------------------------
# Create directories
# --------------------------------------------------------------------------
mkdir /srv/http
mkdir /srv/repos
mkdir /srv/repos/web
mkdir /root/ssh_keys


# --------------------------------------------------------------------------
# Setup directories and links for backup system (rrbackup,
# not installed by this setup script)
# --------------------------------------------------------------------------
mkdir /root/remote_backup
mkdir /root/remote_backup/backup
mkdir /root/remote_backup/backup/mysql_backup
ln -s /etc/apache2 /root/remote_backup/backup/apache2
ln -s /etc/php /root/remote_backup/backup/php
ln -s /srv/http /root/remote_backup/backup/http
ln -s /srv/repos /root/remote_backup/backup/repos


