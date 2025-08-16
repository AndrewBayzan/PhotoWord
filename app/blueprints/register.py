from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.extensions import db
from app.models import Users
from sqlalchemy.exc import IntegrityError

auth = Blueprint("auth", __name__)

@auth.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Введите имя пользователя и пароль")
            return render_template("register.html")

        if Users.query.filter_by(username=username).first():
            flash("Пользователь уже существует")
            return render_template("register.html")

        user = Users(username=username)
        user.set_password(password)
        db.session.add(user)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Ошибка сохранения пользователя")
            return render_template("register.html")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = Users.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.user_id
            session["username"] = user.username
            return redirect(url_for('main.home'))

        flash("Неверный логин или пароль")
        return redirect(url_for("auth.login"))
    
    return render_template("login.html")



@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for('main.home'))