# In Terminal -> connectors
# pip install mysql-connector
# pip install mysql-connector-python
# pip install mysql-connector-python-rf

# import mysql.connector
# mydb = mysql.connector.connect(host="localhost", user="root",passwd="password123")
# my_cursor = mydb.cursor()
# my_cursor.execute("CREATE DATABASE our_users")
# my_cursor.execute("SHOW DATABASES")
# for db in my_cursor:
#     print(db)


import pymysql

mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="password123"
)

my_cursor = mydb.cursor()

# my_cursor.execute("CREATE DATABASE IF NOT EXISTS our_users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)

# mydb.close()

