from flask import Flask, session, url_for, redirect, render_template, request, Blueprint, flash
from app.extensions import db
from app.models import Users


auth = Blueprint("auth", __name__)

@auth.route('/register', methods= ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if Users.query.filter_by(username=username).first():
            return "User has already exists"
        
        user = Users(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    
    return render_template('register.html')

@auth.route('/login', methods= ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = Users.query.filter_by(username=username).first()
 

        if user and user.check_password(password):
            session["user_id"] = user.user_id
            return redirect(url_for('home'))
        else:
            flash("Неверный логин или пароль")
    return render_template("login.html")

@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for('auth.login'))