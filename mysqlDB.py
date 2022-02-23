# from fastapi import Query
import mysql.connector

db = mysql.connector.connect(
    
    # host="remotemysql.com",
    # user="dcRNtOADDk",
    # passwd="ioc5W4pQPO",
    # database="dcRNtOADDk"

    host="localhost",
    port= "3306",
    user="root",
    passwd="",
    database="pdfdb"
)

# https://www.youtube.com/watch?v=_fu2z-6SbSU

mycursor = db.cursor()

# create_db = "CREATE DATABASE mysqlTestDB"

# create_documents_table = "CREATE TABLE documents ( `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT , `name` VARCHAR(100) NOT NULL , `hospital_name` VARCHAR(50) NOT NULL, `registrationNum` VARCHAR(15) NULL DEFAULT NULL , `status` VARCHAR(30) NULL DEFAULT NULL , `keywords` MEDIUMTEXT NOT NULL);"

# create_elements_table = "CREATE TABLE elements (id int PRIMARY KEY AUTO_INCREMENT, sequence_number smallint UNSIGNED, keywords text, content text, table_id int, doc_id int);"
# create_elements_table += "ALTER TABLE `elements` ADD INDEX(`table_id`, `doc_id`);"


# create_tables_table = "CREATE TABLE tables ( `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT , `content` JSON NOT NULL, `keywords` TEXT NOT NULL, `element_id` INT NOT NULL, `doc_id` INT NOT NULL);"
# create_tables_table += "ALTER TABLE `tables` ADD INDEX(`element_id`, `doc_id`);"

# create_images_table = "CREATE TABLE images ( `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT , `image_url` VARCHAR(100) NOT NULL, `element_id` INT NOT NULL, `doc_id` INT NOT NULL);"
# create_images_table += "ALTER TABLE `images` ADD INDEX(`element_id`, `doc_id`);"



def insertDoc(filename, hospital_name, keywords, reg_num=None, status=None):
    # print("inserting doc...")
    query = """INSERT INTO `documents` (`name`, `hospital_name`, `registrationNum`, `status`, `keywords`) 
    VALUES (%s, %s, %s, %s, %s);"""

    mycursor.execute(query,(filename, hospital_name, reg_num, status, keywords))
    db.commit()
    # print("Doc inserted.")

def insertElement(sequence_number, keywords, content, item_type, doc_id):
    
    query = """INSERT INTO `elements` (`sequence_number`, `keywords`, `content`, `item_type`, `doc_id`) 
        VALUES (%s, %s, %s, %s, %s);"""
    
    mycursor.execute(query,(sequence_number, keywords, content, item_type, doc_id))
    db.commit()

def insertElementsList(elem_list):
    # print("elements inserting")
    query = """INSERT INTO `elements` (`sequence_number`, `keywords`, `content`, `item_type`, `doc_id`) 
        VALUES (%s, %s, %s, %s, %s);"""
    
    mycursor.executemany(query, elem_list)
    
    db.commit()
    # print("elements inserted")

def insertTable(content, keywords, element_id):
    query = """INSERT INTO `tables` (`content`, `keywords`, `element_id`) 
        VALUES (%s, %s, %s);"""
    
    mycursor.execute(query,(content, keywords, element_id))
    db.commit()

def getLastInsertID(table_name):
    query = "SELECT MAX(id) FROM "+ table_name +";"
    mycursor.execute(query)

    for x in mycursor:
        return x[0]

def selectQuery():
    select_all = "SELECT * FROM elements"
    mycursor.execute(select_all)
    # records = mycursor.fetchall()
    print("No. of rows:", mycursor.rowcount)
    
    for x in mycursor:
        print(x)

def getAllDocs():
    query = "SELECT `id`,`name`,`hospital_name`,`keywords` FROM `documents`;"

    mycursor.execute(query)
    return mycursor.fetchall()

def searchQuery(key):
    query = "SELECT `id`,`name`,`hospital_name`,`keywords` FROM `documents` WHERE `keywords` LIKE '%{0}%';".format(key)

    mycursor.execute(query)
    return mycursor.fetchall()

# insertQuery(filename, hospital_name, doc_keywords)
# getAllDocs()

# key = "risk assessment"
# res = searchQuery(key)
# print(len(res))

# sentence = 'Cats, rats, bats, and hats.'
# print('occurrence of letter ats:', sentence.count('ats'))

