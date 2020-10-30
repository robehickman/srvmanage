DELETE FROM mysql.db WHERE Db='test' OR Db='test_%';
DROP USER 'root'@'localhost';
CREATE USER 'root'@'%' IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

create database sites;
use sites;
create table sites (
    name longtext,
    status integer,
    sshpass longtext,
    sqlpass longtext
);
