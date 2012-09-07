# -*- coding: utf-8 -*-

#
# This is the configuration file for dbbench.
#

DB_DRIVER = 'psycopg2'
DB_HOST = 'localhost'
DB_USER = 'postgres'
DB_NAME = 'benchmark'
DB_TABLE = 'weblog'

#DB_DRIVER = 'MySQLdb'
#DB_HOST = 'localhost'
#DB_USER = 'root'
#DB_NAME = 'benchmark'
#DB_TABLE = 'weblog'

THREAD_COUNT = 20
SELECT_ROW_COUNT = 100
INSERT_ROW_COUNT = 100

### Don't change anything below this line

if DB_DRIVER == 'psycopg2':
    import psycopg2

    def db_connect():
        return psycopg2.connect(host=DB_HOST, user=DB_USER, database=DB_NAME)

    def db_TimestampFromTicks(*args, **kwargs):
        return psycopg2.TimestampFromTicks(*args, **kwargs)
elif DB_DRIVER == 'MySQLdb':
    import MySQLdb

    def db_connect():
        return MySQLdb.connect(host=DB_HOST, user=DB_USER, db=DB_NAME)

    def db_TimestampFromTicks(*args, **kwargs):
        return MySQLdb.TimestampFromTicks(*args, **kwargs)
