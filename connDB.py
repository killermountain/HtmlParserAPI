import mysql.connector


# HOST="remotemysql.com"
# USERNAME="dcRNtOADDk"
# PASSWORD="ioc5W4pQPO"
# DATABASE="dcRNtOADDk"

HOST="localhost"
PORT= "3306"
USERNAME="root"
PASSWORD=""
DATABASE="pdfdb"

class MySQLDB():

    def __init__(self):
        self.connectDB()        

    def connectDB(self):
        self.conn = mysql.connector.connect(
        host=HOST,
        port= PORT,
        user=USERNAME,
        passwd=PASSWORD,
        database=DATABASE
        )

        self.cursor = self.conn.cursor()

    def getDocInfo(self):
        # query = "SELECT MAX(id) FROM "+ table_name +";"
        query = "SELECT COUNT(`id`), MAX(`id`) FROM `documents`;"
        self.cursor.execute(query)

        for x in self.cursor:
            return (x[0], x[1])

    def getAllDocs(self):
        query = "SELECT `id`,`name`,`hospital_name`,`keywords` FROM `documents`;"

        self.cursor.execute(query)
        results = {}
        for row in self.cursor:
            results[row[0]] = row
        
        return results
        # return self.cursor.fetchall()

    def getElements(self, doc_ids):
        format_strings = ','.join(['%s']* len(doc_ids)) 
        query = """SELECT `id`, `keywords`, `content`, `item_type`, `doc_id` FROM `elements` 
            WHERE `doc_id` IN(%s) AND `item_type` IN ('Table', 'Text');""" % format_strings
        
        results = {}
        self.cursor.execute(query,tuple(doc_ids))
        for row in self.cursor:
            results[row[0]] = row

        # return self.cursor.fetchall()
        return results


    def disconnectDB(self):
            self.conn.close()

