from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.supabase_api import users_db
from sqlalchemy.exc import IntegrityError

auth = Blueprint("auth", __name__)

@auth.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please enter username and password")
            return render_template("register.html")

        # Проверяем наличие пользователя через REST API
        params = {"username": f"eq.{username}"}
        existing = users_db.get("users", params=params)
        if existing:
            flash("User already exists")
            return render_template("register.html")

        # Хэшируем пароль
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        user_data = {"username": username, "password_hash": password_hash}
        try:
            users_db.post("users", user_data)
        except Exception as e:
            flash("Error saving user")
            return render_template("register.html")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Получаем пользователя через REST API
        params = {"username": f"eq.{username}"}
        users = users_db.get("users", params=params)
        if users:
            user = users[0]
            from werkzeug.security import check_password_hash
            if check_password_hash(user["password_hash"], password):
                session["user_id"] = user.get("user_id")
                session["username"] = user.get("username")
                return redirect(url_for('main.home'))

        flash("Invalid username or password")
        return redirect(url_for("auth.login"))
    
    return render_template("login.html")



@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for('main.home'))