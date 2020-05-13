apt-get update
apt-get upgrade

apt-get install -y htop git

# Install mysql
apt-get install -y mariadb-server
service mysql start

# Install and setup apache2
# need newer version for acme v2
echo "deb https://deb.debian.org/debian buster-backports main" > /etc/apt/sources.list.d/backports.list
apt-get update
apt-get -t buster-backports install apache2

a2enmod http2
a2enmod rewrite
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


# Install and setup PHP
apt install apt-transport-https lsb-release
wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg
sh -c 'echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list' 
apt update 

apt-get install php7.4-fpm php7.4-{bcmath,bz2,intl,gd,mbstring,mysqli,zip,imagick}
phpenmod mbstring

# Install nodejs and rollup
curl -sL https://deb.nodesource.com/setup_10.x -o /tmp/nodesource_setup.sh
bash /tmp/nodesource_setup.sh
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
mkdir /root/ssh_keys

