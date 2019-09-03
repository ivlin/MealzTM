from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

meal_schema=["date","description","total","individual","recipient"]
names=["Allison","Dan","Justin","Ivan","Ellis","Melvin"]
create_str="CREATE TABLE IF NOT EXISTS meal (datestring VARCHAR(10), description VARCHAR(50), total REAL, individual REAL, recipient VARCHAR(10))"
insert_str="INSERT INTO meal VALUES (?, ?, ?, ?, ?)"
for name in names:
    create_str = create_str[:-1] + ", " + name + " BOOLEAN" +create_str[-1]
    insert_str = insert_str[:-1] + ", ?" + create_str[-1]

@app.route("/")
def index():
    return render_template("index.html")

def calc_balance(transactions):
    balance={}
    for name in names:
        balance[name]=0
    for transaction in transactions:
        #print transaction
        balance[transaction[meal_schema.index('recipient')]]-=transaction[meal_schema.index("total")]-transaction[meal_schema.index('individual')]
        for i in xrange(len(names)):
            if transaction[len(meal_schema)+i]:
                balance[names[i]]+=transaction[meal_schema.index('individual')]
    return balance

@app.route("/history")
def view_history():
    db = sqlite3.connect("db/mealtracker")
    cursor = db.cursor()
    cursor.execute(create_str)
    history=cursor.execute("SELECT * FROM meal").fetchall()
    return render_template("history.html",schema=meal_schema+names,history=history,names=names,balance=calc_balance(history))

@app.route("/new_entry", methods=["GET","POST"])
def new_entry():
    if request.method == "GET":
        return render_template("new_entry.html",names=names)
    elif request.method == "POST":
        db = sqlite3.connect("db/mealtracker")
        cursor = db.cursor()
        cursor.execute(create_str)
        form_vals=[]
        #print request.form
        #print request.form["individual"]
        for field in meal_schema:
            form_vals.append(request.form[field])
        for name in names:
            if name in request.form:
                form_vals.append(True)
            else:
                form_vals.append(False)
        cursor.execute(insert_str, form_vals)
        db.commit()
        return redirect(url_for("new_entry"))

if __name__=="__main__":
    app.debug = True
    try:
        os.mkdir("db")
    except Exception:
        pass
    app.run(host='0.0.0.0', port=8000, use_reloader=False)