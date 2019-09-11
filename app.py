from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey
import sqlite3
import os
from utils import *

app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

psql_db = SQLAlchemy(app)


class Room(psql_db.Model):
    __tablename__="room"
    id = psql_db.Column(Integer, primary_key=True, autoincrement=True)
    name = psql_db.Column(String())
    members = psql_db.Column(Integer)

    def __init__(self, name, members):
        self.name = name
        self.members = members

    def __repr__(self):
        return "" + str(self.id) + " , " + self.name

class Meal(psql_db.Model):
    __tablename__="meal"
    id = psql_db.Column(Integer, primary_key=True)
    room = psql_db.Column(Integer, ForeignKey("room.id"))
    date = psql_db.Column(String())
    description = psql_db.Column(String())
    total = psql_db.Column(psql_db.Float)
    individual = psql_db.Column(psql_db.Float)
    supplier = psql_db.Column(String())

    def __init__(self, room, date, description, total, individual, supplier):
        self.room = room
        self.date = date
        self.description = description
        self.total = total
        self.individual = individual
        self.supplier = supplier

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self.__dict__.items()
        })

class Person(psql_db.Model):
    __tablename__="person"
    id = psql_db.Column(Integer, primary_key=True)
    room = psql_db.Column(Integer, ForeignKey("room.id"))
    name = psql_db.Column(String())
    balance = psql_db.Column(psql_db.Float)

    def __init__(self, room, name, balance):
        self.room = room
        self.name = name
        self.balance = balance

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self.__dict__.items()
        })

class Transaction(psql_db.Model):
    __tablename__="transaction"
    id = psql_db.Column(Integer, primary_key=True)
    room = psql_db.Column(Integer, ForeignKey("room.id"))
    meal = psql_db.Column(Integer)
    sender = psql_db.Column(Integer)
    receiver = psql_db.Column(Integer)
    amount = psql_db.Column(psql_db.Float)

    def __init__(self, room, meal, sender, receiver, amount):
        self.room = room
        self.meal = meal
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, {
            column: value
            for column, value in self.__dict__.items()
        })
meal_schema=["room","date","description","total","individual","supplier"]

@app.route("/")
def index():
    #rooms=get_table("room", "CREATE TABLE IF NOT EXISTS room (name VARCHAR(30), members INT)", True)
    rooms=Room.query.all()
    return render_template("index.html",rooms=rooms)

@app.route("/<room_id>/new_member",methods=["POST"])
def new_member(room_id):
    '''
    db=sqlite3.connect("db/mealtracker")
    cursor=db.cursor()
    cursor.execute("INSERT INTO people VALUES (?, ?, ?)", (request.form["new_member"],0.00, room_id))
    cursor.execute("UPDATE room SET members = members + 1 WHERE rowid = ?",(room_id))
    db.commit()
    '''
    psql_db.session.add(Person(room_id,request.form["new_member"],0.00))
    Room.query.filter_by(id=room_id).first().members += 1
    psql_db.session.commit()

    return redirect(url_for("new_entry",room_id=room_id))


@app.route("/new_room",methods=["POST"])
def new_room():
    '''
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute("INSERT INTO room VALUES (?, ?)",(request.form["roomname"], 0))
    db.commit()
    last_id=cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
    '''
    new_room = Room(request.form["roomname"], 0)
    psql_db.session.add(new_room)
    psql_db.session.commit()
    psql_db.session.refresh(new_room)

    return redirect(url_for("new_entry",room_id=new_room.id))

@app.route("/<room_id>/edit_lobby",methods=["POST"])
def edit_lobby(room_id):
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute("UPDATE room SET name = ? WHERE rowid = ?", (request.form["lobby_name"], room_id))
    db.commit()

    Room.query.filter_by(id=room_id).first().name = request.form["lobby_name"]
    psql_db.session.commit()

    return redirect(url_for("new_entry",room_id=room_id))

@app.route("/<room_id>/history")
def view_history(room_id):
    '''
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
    transaction = psql_db.session.query([Payment.meal, Sender.name, Recipient.name, Payment.amount]).join(Person, Payment.sender == Person.id).join(Person, Payment.receiver=Person.id).filter_by(Payment.room = room_id).all()
    '''
    meals = Meal.query.filter_by(room=room_id).all()
    people = Person.query.filter_by(room=room_id).all()

    transactions= Transaction.query.filter_by(room=room_id).all()

    names=[]
    name_dic={}
    for person in people:
        name_dic[person.id]=person.name
        names.append(person.name)
    transaction_dic = {}
    for meal in meals:
        transaction_dic[meal.id] = []
        for field in meal_schema:
            transaction_dic[meal.id].append(meal.__dict__.get(field))
        transaction_dic[meal.id] += [0]*len(names)
    for transaction in transactions:
        transaction_dic[transaction.meal][len(meal_schema)+names.index(transaction.sender)] = transaction.amount
    return render_template("history.html",schema=meal_schema+names,history=transaction_dic,names=names,balance=people)

@app.route("/<room_id>/new_entry", methods=["GET","POST"])
def new_entry(room_id):
    '''
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    '''
    if request.method == "GET":
        '''
        room_name=cursor.execute("SELECT name FROM room WHERE rowid = ?",(room_id)).fetchone()[0]
        '''
        room_name=Room.query.filter_by(id=room_id).first().name
        names=Person.query.filter_by(room=room_id).all()
        return render_template("new_entry.html",room_name=room_name,names=names)
    elif request.method == "POST":
        names=get_names(room_id)
        form_vals=[]
        for field in meal_schema:
            if field != "room":
                form_vals.append(request.form[field])
        '''
        cursor.execute(get_insertstring([]), [room_id]+form_vals)
        meal_id=cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
        recipient=cursor.execute("SELECT rowid FROM people WHERE room = ? AND name = ?",(room_id, request.form["supplier"])).fetchone()[0]
        for name in get_names(room_id):
            if name in request.form:
                sender=cursor.execute("SELECT rowid FROM people WHERE room = ? AND name = ?",(room_id, name)).fetchone()[0]
                cursor.execute("INSERT INTO payment VALUES (?, ?, ?, ?, ?)", (room_id, meal_id, sender, recipient, request.form["individual"]))
                cursor.execute("UPDATE people SET balance = balance + ? WHERE rowid = ?",(request.form["individual"], sender))
        cursor.execute("UPDATE people SET balance = balance - ? + ? WHERE rowid = ?",(request.form["total"],request.form["individual"], recipient))
        db.commit()
        '''
        new_meal=Meal(*([room_id]+form_vals))
        psql_db.session.add(new_meal)
        psql_db.session.commit()
        psql_db.session.refresh(new_meal)
        meal_id=new_meal.id

        for name in get_names(room_id):
            if name in request.form:
                sender=Person.query.filter_by(room=room_id, name=name).first()
                recipient=Person.query.filter_by(room=room_id, name=request.form["supplier"]).first()
                psql_db.session.add(Transaction(room_id, meal_id, sender.id, recipient.id, request.form["individual"]))
                Person.query.filter_by(balance=request.form["individual"], id=sender.id)
                psql_db.session.commit()

        recipient=Person.query.filter_by(room=room_id, name=request.form["supplier"]).first()
        Person.query.filter_by(id=recipient.id).first().balance-=float(request.form["total"])-float(request.form["individual"])
        psql_db.session.commit()

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
    '''
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute("DELETE FROM room WHERE rowid = ?",(room_id))
    cursor.execute("DELETE FROM meal WHERE room = ?",(room_id))
    cursor.execute("DELETE FROM people WHERE room = ?",(room_id))
    cursor.execute("DELETE FROM payment WHERE room = ?",(room_id))
    db.commit()
    '''
    Room.query.filter_by(id=room_id).delete()
    Meal.query.filter_by(room=room_id).delete()
    Person.query.filter_by(room=room_id).delete()
    Transaction.query.filter_by(room=room_id).delete()
    psql_db.commit()
    return redirect(url_for("index"))

@app.route("/reset_database")
def reset():
    #os.remove("db/mealtracker")
    #initialize_db()
    psql_db.drop_all()
    psql_db.create_all()
    return redirect(url_for("index"))

if __name__=="__main__":
    app.debug = True
    '''
    initialize_db()
    try:
        os.mkdir("db")
    except Exception:
        pass
    '''
    app.run(host='0.0.0.0', port=8000, use_reloader=False)
