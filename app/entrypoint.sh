#!/bin/sh

mkdir -p /run/mysqld
chown -R mysql:mysql /run/mysqld

echo "Initializating database..."
mysql_install_db --user=mysql --ldata=/var/lib/mysql
mysqld --user=mysql --console --skip-name-resolve --skip-networking=0 &

# Wait for mysql to start
while ! mysqladmin ping -h'localhost' --silent; do echo "not up" && sleep .2; done

echo "Populating database..."

mysql -u root << EOF
CREATE DATABASE challenge;
CREATE TABLE challenge.users(
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    note VARCHAR(1024)
);
CREATE USER 'user'@'%' IDENTIFIED BY '455afd90edecf3ef9e3409c4607f3d14';
GRANT ALL PRIVILEGES ON challenge.* TO 'user'@'%';
FLUSH PRIVILEGES;
EOF

gunicorn --bind 0.0.0.0:80 -w 5 app:app