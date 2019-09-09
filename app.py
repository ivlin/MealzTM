from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from utils import *

app = Flask(__name__)

meal_schema=["room","date","description","total","individual","supplier"]

@app.route("/")
def index():
    rooms=get_table("room", "CREATE TABLE IF NOT EXISTS room (name VARCHAR(30), members INT)", True)
    return render_template("index.html",rooms=rooms)

@app.route("/<room_id>/new_member",methods=["POST"])
def new_member(room_id):
    db=sqlite3.connect("db/mealtracker")
    cursor=db.cursor()
    cursor.execute("INSERT INTO people VALUES (?, ?, ?)", (request.form["new_member"],0.00, room_id))
    cursor.execute("UPDATE room SET members = members + 1 WHERE rowid = ?",(room_id))
    db.commit()
    return redirect(url_for("new_entry",room_id=room_id))


@app.route("/new_room",methods=["POST"])
def new_room():
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute("INSERT INTO room VALUES (?, ?)",(request.form["roomname"], 0))
    db.commit()
    last_id=cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
    return redirect(url_for("new_entry",room_id=last_id))

@app.route("/<room_id>/edit_lobby",methods=["POST"])
def edit_lobby(room_id):
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute("UPDATE room SET name = ? WHERE rowid = ?", (request.form["lobby_name"], room_id))
    db.commit()
    return redirect(url_for("new_entry",room_id=room_id))

@app.route("/<room_id>/history")
def view_history(room_id):
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    names=get_names(room_id)
    meals=cursor.execute("SELECT rowid,* FROM meal WHERE room = ?",[room_id]).fetchall()
    people=cursor.execute("SELECT name,balance FROM people WHERE room = ?",(room_id)).fetchall()
    transactions=cursor.execute("""SELECT payment.meal, sender.name, recipient.name, payment.amount FROM payment
                                    INNER JOIN people sender on payment.sender=sender.rowid
                                    INNER JOIN people recipient on payment.receiver=recipient.rowid
                                    WHERE payment.room = ?
                                    ORDER BY payment.room, payment.meal""", (room_id)).fetchall()
    combined_view = {}
    for meal in meals:
        combined_view[meal[0]] = list(meal[1:]) + [0]*len(names)
    for transaction in transactions:
        combined_view[transaction[0]][len(meal_schema)+names.index(transaction[1])] = transaction[3]
    people = [[person[0], round(person[1]*100)/100] for person in people]
    return render_template("history.html",schema=meal_schema+names,history=combined_view,names=names,balance=people)

@app.route("/<room_id>/new_entry", methods=["GET","POST"])
def new_entry(room_id):
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    if request.method == "GET":
        room_name=cursor.execute("SELECT name FROM room WHERE rowid = ?",(room_id)).fetchone()[0]
        return render_template("new_entry.html",room_name=room_name,names=get_names(room_id))
    elif request.method == "POST":
        names=get_names(room_id)
        form_vals=[]
        for field in meal_schema:
            if field != "room":
                form_vals.append(request.form[field])
        cursor.execute(get_insertstring([]), [room_id]+form_vals)
        meal_id=cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
        for name in get_names(room_id):
            if name in request.form:
                sender=cursor.execute("SELECT rowid FROM people WHERE room = ? AND name = ?",(room_id, name)).fetchone()[0]
                recipient=cursor.execute("SELECT rowid FROM people WHERE room = ? AND name = ?",(room_id, request.form["supplier"])).fetchone()[0]
                cursor.execute("INSERT INTO payment VALUES (?, ?, ?, ?, ?)", (room_id, meal_id, sender, recipient, request.form["individual"]))
                cursor.execute("UPDATE people SET balance = balance + ? WHERE rowid = ?",(request.form["individual"], sender))
        cursor.execute("UPDATE people SET balance = balance - ? + ? WHERE rowid = ?",(request.form["total"],request.form["individual"], recipient))
        db.commit()
        return redirect(url_for("new_entry", room_id=room_id))

@app.route("/<room_id>/clear")
def clear():
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute("UPDATE people SET balance = 0 WHERE room = ?",(room_id))
    db.commit()
    return redirect(url_for("view_history",room_id=room_id))


@app.route("/<room_id>/delete")
def delete_room(room_id):
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute("DELETE FROM room WHERE rowid = ?",(room_id))
    db.commit()
    return redirect(url_for("index"))

@app.route("/reset_database")
def reset():
    os.remove("db/mealtracker")
    initialize_db()
    return redirect(url_for("index"))

if __name__=="__main__":
    app.debug = True
    try:
        os.mkdir("db")
    except Exception:
        pass
    app.run(host='0.0.0.0', port=8000, use_reloader=False)