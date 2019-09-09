import sqlite3

def initialize_db():
    db=sqlite3.connect("db/mealtracker")
    cursor=db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS room (name VARCHAR(30), members INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS meal (room INT, datestring VARCHAR(10), description VARCHAR(50), total REAL, individual REAL, recipient VARCHAR(10))")
    cursor.execute("CREATE TABLE IF NOT EXISTS people (name VARCHAR(30), balance REAL, room INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS payment (room INT, meal INT, sender INT, receiver INT, amount REAL)")
    db.commit()
    return

def get_names(room_id):
    db=sqlite3.connect("db/mealtracker")
    cursor=db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS people (name VARCHAR(30), balance REAL, room INT)")
    names=cursor.execute("SELECT name FROM people WHERE room = ?",(room_id)).fetchall()
    return [name[0] for name in names]

def get_createstring(names):
    create_str="CREATE TABLE IF NOT EXISTS meal (room INT, datestring VARCHAR(10), description VARCHAR(50), total REAL, individual REAL, recipient VARCHAR(10))"
    return create_str

def get_insertstring(names):
    insert_str="INSERT INTO meal VALUES (?, ?, ?, ?, ?, ?)"
    return insert_str

def get_table(tablename, createstring, include_id=False):
    db=sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute(createstring)
    if include_id:
        return cursor.execute("SELECT rowid,* FROM "+tablename).fetchall()
    return cursor.execute("SELECT * FROM "+tablename).fetchall()