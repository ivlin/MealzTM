from sqlalchemy import Integer, String, ForeignKey
from app import psql_db

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