dbbench is a small tool to run simple multi-threaded benchmarks on PostgreSQL or MySQL / MariaDB.

## Setup a test environment
I'm creating an empty partition on LVM to serve as the storage area for our databases.

    lvcreate -l100%FREE -n default data
    mkfs.xfs -f /dev/mapper/data-default
    mkdir -p /mnt/data
    echo '/dev/mapper/data-default /mnt/data xfs defaults,noatime,barrier=0 0 0' >> /etc/fstab
    mount /mnt/data

    service postgresql-9.2 stop
    service mysql stop
    mv /var/lib/pgsql /var/lib/mysql /mnt/data
    ln -s /mnt/data/pgsql /var/lib/pgsql
    ln -s /mnt/data/mysql /var/lib/mysql

## Install psycopg2 and MySQLdb
    yum -y upgrade
    # We have to uninstall nfs-utils because it's currently incompatible with the PostgreSQL-9.2 packages
    yum -y erase nfs-utils
    yum -y install gcc make python-devel python-setuptools zlib-devel openssl-devel perl-Time-HiRes perl-DBI

    # Install the version of MySQL / MariaDB and PostgreSQL that you'd like to test now.
    # Get PostgreSQL 9.2 here: http://yum.postgresql.org/9.2/redhat/rhel-6-x86_64/repoview/
    # Get MariaDB 5.5 here: http://downloads.mariadb.org/mariadb/5.5.25/#file_type=rpm&bits=64
    # Get MySQL here: http://dev.mysql.com/downloads/mysql/#downloads

    # Install psycopg2 (for PostgreSQL 9.2 in this case)
    wget http://www.psycopg.org/psycopg/tarballs/PSYCOPG-2-4/psycopg2-2.4.5.tar.gz
    tar xvfz psycopg2-2.4.5.tar.gz
    cd psycopg2-2.4.5
    sed -i 's:#pg_config=:pg_config=/usr/pgsql-9.2/bin/pg_config:g' setup.cfg
    python setup.py install

    # Install mysql-python
    pip install MySQL-python

## Create a test database for PostgreSQL

    psql -Upostgres

        DROP DATABASE IF EXISTS benchmark;
        CREATE DATABASE benchmark WITH OWNER=postgres;
        GRANT ALL ON DATABASE benchmark TO postgres WITH GRANT OPTION;

        CREATE TABLE weblog (
            id SERIAL,
            vhost VARCHAR(200),
            rhost INET,
            logname VARCHAR(30),
            username VARCHAR(30),
            timestamp TIMESTAMP,
            request VARCHAR(200),
            status SMALLINT,
            response_size BIGINT
        );
        CREATE UNIQUE INDEX weblog_id_idx ON weblog(id);

## Create a test database for MariaDB

    mysql -uroot -hlocalhost

        DROP DATABASE IF EXISTS benchmark;
        CREATE DATABASE benchmark;
        USE benchmark;

        CREATE TABLE weblog (
            id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            vhost VARCHAR(200),
            rhost VARCHAR(45),
            logname VARCHAR(30),
            username VARCHAR(30),
            timestamp TIMESTAMP,
            request VARCHAR(200),
            status smallint,
            response_size bigint
        ) ENGINE=InnoDB CHARACTER SET utf8 COLLATE utf8_bin;

## Start the tool
    # Tune your database configuration!
    # I supply my own test configuration in the conf/ subdirectory.
    vi /etc/my.cnf
    vi /var/lib/pgsql/9.2/data/postgresql.conf

    # Configure some settings
    vi settings.py

    # Start either MySQL / MariaDB or PostgreSQL
    service postgresql-9.2 start
    service mysql stop
    # or:
    service postgresql-9.2 stop
    service mysql start

    # Let inserter run for some time in order to generate enough test data.
    ./inserter.py

    # Start selector only when inserter did insert enough rows!
    ./selector.py

## Some interesting queries to run manually during the benchmark
    # Add a NULL column
    #  - PostgreSQL: Very fast, doesn't block INSERTs visibly
    #  - MySQL: Very slow, blocks INSERTs during the whole operation
    #
    ALTER TABLE weblog ADD COLUMN test1 VARCHAR(200) NULL;

    # Add a NOT NULL column
    #  - PostgreSQL: Very slow, blocks INSERTs and SELECTs during the whole operation
    #  - MySQL: Very slow, blocks INSERTs during the whole operation
    #
    # Note that this is quite an unusual query to run on an already existing DB...
    #
    ALTER TABLE weblog ADD COLUMN test2 VARCHAR(200) NOT NULL DEFAULT 'Hello World';

    # Drop two columns
    #  - PostgreSQL: Very fast, doesn't block INSERTs visibly
    #  - MySQL: Very slow, blocks INSERTs during the whole operation
    #
    ALTER TABLE weblog DROP COLUMN test1;
    ALTER TABLE weblog DROP COLUMN test2;
