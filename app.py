from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return "Still under construction :("

import traceback

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html', error = traceback.format_exc()), 500

@app.route("/chat")
def chat():
    result = db.session.execute("SELECT content FROM messages")
    messages = result.fetchall()
    return render_template("chat/index.html", messages = messages, admin = False)

@app.route("/postMessage", methods=["POST"])
def postMessage():
    content = request.form["content"]
    sql = "INSERT INTO messages (content) VALUES ('" + content + "')"
    db.session.execute(sql)
    db.session.commit()
    return redirect("/chat")

@app.route("/deleteAllMessages")
def deleteAllMessages():
    sql = "DELETE FROM messages"
    db.session.execute(sql)
    db.session.commit()
    return redirect("/chat")