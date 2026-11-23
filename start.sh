#!/bin/bash
mkdir -p /run/mysqld && chown mysql:mysql /run/mysqld
mysqld_safe --bind-address=127.0.0.1 &

for i in $(seq 1 30); do
  mysqladmin ping --silent 2>/dev/null && break
  sleep 1
done

mysql -e "CREATE DATABASE IF NOT EXISTS murad CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS 'murad'@'127.0.0.1' IDENTIFIED BY 'murad'; CREATE USER IF NOT EXISTS 'murad'@'localhost' IDENTIFIED BY 'murad'; GRANT ALL ON murad.* TO 'murad'@'127.0.0.1'; GRANT ALL ON murad.* TO 'murad'@'localhost'; FLUSH PRIVILEGES;"

sed -i "s/Listen 80/Listen ${PORT:-80}/" /etc/apache2/ports.conf
sed -i "s/:80>/:${PORT:-80}>/" /etc/apache2/sites-enabled/000-default.conf
exec apache2-foreground