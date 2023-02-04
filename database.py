import mysql.connector
import os
import shutil

mydb = mysql.connector.connect(host="localhost",user="root",password="mysql")
global cursor 
cursor = mydb.cursor()

def convert_data(file_name):
    with open(file_name, 'rb') as file:
        binary_data = file.read()
    return binary_data

def cf2b(filename):
    with open(filename,'rb') as file:
        binarydata=file.read()
    return binarydata

def cb2f(binarydata,filename):
    with open(filename,'wb') as file:
        file.write(binarydata)

def checkdatabase():
    mydb = mysql.connector.connect(host="localhost",user="root",password="mysql")
    cursor =  mydb.cursor()
    cursor.execute("SHOW DATABASES")
    flag=0
    for x in cursor:
        if x=="studybuddy":
            flag=1
            break
    if flag==0:
        cursor.execute("CREATE DATABASE if not exists studybuddy;")
        

def checktables():
    connection = mysql.connector.connect(host="localhost",user="root",password="mysql")
    mycursor =  connection.cursor()
    mycursor.execute("use studybuddy;")
    mycursor.execute("show tables;")
    tablelist = mycursor.fetchall()
    fl1=0
    fl2=0
    for x in tablelist:
        if x[0]=='login':
            fl1=1
        if x[0]=='file':
            fl2=1
    if fl1==0:
        mycursor.execute("create table login(username varchar(255) not null,email_id varchar(255) not null,password CHAR(97) not null,college varchar(255) not null,college_state varchar(255),PRIMARY KEY(username ,email_id));")
    if fl2==0:
        mycursor.execute("create table files(upload_id int primary key AUTO_INCREMENT,email_id varchar(255),username varchar(255),topic varchar(255),file LONGBLOB,filename varchar(255)) AUTO_INCREMENT=100;")


def insertfile(email_id, name, topic):
    connection = mysql.connector.connect(host='localhost',database='studybuddy',user='root',password='mysql')
    cursor = connection.cursor()
    query = "select username from login where email_id=\'"+email_id+"\';"
    cursor.execute(query)
    u = cursor.fetchone()
    blob = convert_data(os.path.dirname(__file__)+"\\static\\uploaded_files\\"+email_id+"\\"+name)
    query = """ INSERT INTO Files(email_id,username,topic,file,filename) VALUES(%s,%s,%s,%s,%s)"""
    cursor.execute(query,(email_id,u[0],topic,blob,name))
    connection.commit()

#def search(topic,college):

def uploadata(upload_id):
    connection = mysql.connector.connect(host='localhost',database='studybuddy',user='root',password='mysql')
    cursor = connection.cursor()
    query = "select file,filename from Files where upload_id='"+upload_id+"';"
    cursor.execute(query)
    return cursor.fetchone()

def view(upload_id):
    connection = mysql.connector.connect(host='localhost',database='studybuddy',user='root',password='mysql')
    cursor = connection.cursor()
    query = "select file,filename,email_id from Files where upload_id='"+upload_id+"';"
    cursor.execute(query)
    return cursor.fetchone()

def states():
    connection = mysql.connector.connect(host='localhost',database='studybuddy',user='root',password='mysql')
    cursor = connection.cursor()
    query = "select DISTINCT college_state from login;"
    cursor.execute(query)
    return cursor.fetchall()

def search(filename,topic,c):
    connection = mysql.connector.connect(host='localhost',database='studybuddy',user='root',password='mysql')
    cursor = connection.cursor()
    l =[]
    if filename=="":
        if topic=="":
            if c=="":
                query = "select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id;"
                cursor.execute(query)
            else:
                query = "select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id where college like \'%"+c+"%\';"
                cursor.execute(query)
        else:
            if c=="":
                query = "select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id where topic like \'%"+topic+"%\';"
                cursor.execute(query)
            else:
                query = "select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id where college like \'%"+c+"%\' and topic like \'%"+topic+"%\';"
                cursor.execute(query)
    else:
        if topic=="":
            if c=="":
                query = "select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id where filename like \'%"+filename+"%\';"
                cursor.execute(query)
            else:
                query = "select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id where filename like \'%"+filename+"%\' and college like \'%"+c+"%\';"
                cursor.execute(query)
        else:
            if c=="":
                query = "select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id where filename like \'%"+filename+"%\' and topic like \'%"+topic+"%\';"
                cursor.execute(query)
            else:
                query = "select login.username,files.filename,files.file,files.upload_id from login inner join files on login.email_id=files.email_id where filename like \'%"+filename+"%\' and college like \'%"+c+"%\' and topic like \'%"+topic+"%\';"
                cursor.execute(query)

    return cursor.fetchall()

# checkdatabase()
# checktables()
# from argon2 import PasswordHasher
# mydb = mysql.connector.connect(host="localhost",user="root",password="mysql")
# mycursor = mydb.cursor()
# ph = PasswordHasher()
# mycursor.execute("use studybuddy;")
# checktables()
# mycursor.execute("select * from login")
# password = ph.hash("565656")
# for x in mycursor:
#     print(x[2])
#     print(type(x[2]))
#     if ph.verify(str(x[2]),"565656"):
#         print("***")
# #insertfile("ms139@snu.edu.in", r"C:\Users\Aravo\OneDrive\Desktop\Screenshot 2022-10-14 232333.png","Crypto")
#insertfile("ms139@snu.edu.in", r"C:\Users\Aravo\OneDrive\Desktop\Midsem des.pdf","Cryptography")
