#!/usr/bin/python

import os
import time
import pipes
import sys

# MySQL database details to which backup to be done. Make sure below user having enough privileges to take databases
# backup. To take multiple databases backup, create any file like /backup/dbnames.txt and put databases names one on
# each line and assigned to DB_NAME variable.

if len(sys.argv) < 4:
    raise ValueError('Command Line Argument Missing')

DB_HOST = sys.argv[2]
DB_USER = sys.argv[3]
DB_USER_PASSWORD = sys.argv[4]
# DB_NAME = '/backup/dbnameslist.txt'
DB_NAME = sys.argv[1]
BACKUP_PATH = '/dbbackup'

# Getting current DateTime to create the separate backup folder like "20180817-123433".
DATETIME = time.strftime('%Y%m%d-%H%M%S')
TODAYBACKUPPATH = BACKUP_PATH + '/' + DATETIME

# Checking if backup folder already exists or not. If not exists will create it.
try:
    os.stat(TODAYBACKUPPATH)
except:
    os.mkdir(TODAYBACKUPPATH)

# Code for checking if you want to take single database backup or assinged multiple backups in DB_NAME.
print("checking for databases names file.")
if os.path.exists(DB_NAME):
    file1 = open(DB_NAME)
    multi = 1
    print("Databases file found...")
    print("Starting backup of all dbs listed in file " + DB_NAME)
else:
    print("Databases file not found...")
    print("Starting backup of database " + DB_NAME)
    multi = 0

# Starting actual database backup process.
if multi:
    in_file = open(DB_NAME, "r")
    flength = len(in_file.readlines())
    in_file.close()
    p = 1
    dbfile = open(DB_NAME, "r")

    while p <= flength:
        db = dbfile.readline()  # reading database name from file
        db = db[:-1]  # deletes extra line
        dumpcmd = "mysqldump --single-transaction -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + pipes.quote(
            TODAYBACKUPPATH) + "/" + db + ".sql"
        os.system(dumpcmd)
        p = p + 1
    dbfile.close()
else:
    db = DB_NAME
    dumpcmd = "mysqldump --single-transaction -h " + DB_HOST + " -u " + DB_USER + " -p" + DB_USER_PASSWORD + " " + db + " > " + pipes.quote(
        TODAYBACKUPPATH) + "/" + db + ".sql"
    os.system(dumpcmd)

print("")
print("Backup script completed")
print("Your backups have been created in '" + TODAYBACKUPPATH + "' directory")