apt-get update
apt-get upgrade

# Install mysql
apt-get install -y mariadb-server
service mysql start

# Install and setup apache2
apt-get install -y htop apache2 git
a2enmod rewrite
a2enmod proxy_http
rm -f /etc/apache2/sites-available/*
rm -f /etc/apache2/sites-enabled/*
service apache2 restart

# Install and setup PHP
apt install apt-transport-https lsb-release
wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg
sh -c 'echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list' 
apt update 

apt-get install php7.4-fpm php7.4-{bcmath,bz2,intl,gd,mbstring,mysqli,zip,imagick}
phpenmod mbstring

# Install nodejs and rollup
curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh
bash nodesource_setup.sh
apt install nodejs
npm install -g rollup

# Install a few python packages
apt-get install -y python3-pip
pip3 install pymysql
pip3 install pyyaml

# Create directories
mkdir /srv/http
mkdir /srv/repos
mkdir /srv/repos/web

