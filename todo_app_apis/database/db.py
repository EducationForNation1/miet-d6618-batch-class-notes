import mysql.connector

def connectDB():
    connection = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "root",
        database = "todo_db"
    )

    if connection:
        print("Database Connected")
        return connection
    else:
        print("Database Not Connected")


    

    