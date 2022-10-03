import sqlite3

def connect_db():  # ensure the db is always connected
        return sqlite3.connect("finances.db")


SEARCH = "SELECT * FROM months;"

def search(connection):  # search and returns values that satisfy the search conditions
    with connection:
        answers = connection.execute(SEARCH)
    
        for i in answers:
            print(i)


connection = connect_db()

search(connection) # occurs each time the code is run
