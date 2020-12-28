from flask import Flask
from flask import redirect, render_template, request
from flask_login import login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'key'
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "Please login to use this functionality."

db.session.execute("UPDATE users SET is_active = 0")
db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    result = db.session.execute("SELECT * FROM users WHERE Id =" + str(user_id))
    print("user fetched")
    user = result.fetchone()
    return user

import traceback

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("errors/500.html", error = traceback.format_exc()), 500

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin/index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    result = db.session.execute("SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'")
    user = result.fetchone()
    if not user:
        return render_template("errors/403.html")
    login_user(user)
    db.session.execute("UPDATE users SET is_active = 1 WHERE Id =" + str(user.Id))
    db.session.commit()
    return redirect("/")

@app.route("/logout")
def logout():
    logout_user()
    db.session.execute("UPDATE users SET is_active = 0 WHERE Id =" + str(current_user.Id))
    db.session.commit()
    return redirect("/")


@app.route("/chat")
def chat():
    result = db.session.execute("SELECT content FROM messages")
    messages = result.fetchall()
    print(current_user.is_active)
    return render_template("chat/index.html", messages = messages, admin = current_user.is_active)

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