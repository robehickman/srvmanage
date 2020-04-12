apt-get update
apt-get upgrade

sudo apt -y install lsb-release apt-transport-https ca-certificates 
sudo wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg

apt-get install -y mariadb-server
service mysql start
mysql -u root < /vagrant/setup.sql

apt-get install -y htop apache2 git php7.4-fpm php7.4-{bcmath,bz2,intl,gd,mbstring,mysqli,zip,imagick}
phpenmod mbstring
a2enmod rewrite
a2enmod proxy_http
rm -f /etc/apache2/sites-available/*
rm -f /etc/apache2/sites-enabled/*

service apache2 restart

curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh
bash nodesource_setup.sh
apt install nodejs
npm install -g rollup

apt-get install -y python3-pip
pip3 install pymysql
pip3 install pyyaml

mkdir /srv/http
mkdir /srv/repos
mkdir /srv/repos/web

