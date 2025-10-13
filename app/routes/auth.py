from flask import Blueprint, request, render_template, redirect, url_for
from ..extensions import db, login_user, logout_user, login_required
from ..models import User
from .. import login_manager

auth_bp = Blueprint("auth_bp", __name__, template_folder="../templates")


@login_manager.user_loader
def load_user(user_email):
    return User.query.get(user_email)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("username")
        user_email = request.form.get("userEmail")
        password = request.form.get("password")

        if User.query.filter_by(user_email=user_email).first():
            return {"message": "Email already exists."}, 409

        new_user = User(user_email=user_email, user_name=user_name)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return {}, 200

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_email = request.form.get("userEmail")
        password = request.form.get("password")

        user: User = User.query.filter_by(user_email=user_email).first()

        if user and user.check_password(password):
            login_user(user)
            return {}, 200
        else:
            return {"message": "Invalid Credentials!"}, 401

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home_bp.home"))
