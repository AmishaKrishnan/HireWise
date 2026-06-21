import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="AmiKrish@123",
        database="hirewise"
    )