from flask import Blueprint, render_template, request, redirect, session
from .models import User
from . import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get("name")
        user = User.query.filter_by(name=name).first()
        if user:
            session["user_id"] = user.user_id
            session["role"] = user.role
            if user.role == "admin":
                return redirect("/admin/dashboard")
            else:
                return redirect("/driver/routes")
        return "User not found"

    return render_template("login.html")
