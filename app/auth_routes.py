# app/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Haal de naam op uit het formulier
        name = request.form.get("name")

        # Zoek gebruiker in de database
        user = User.query.filter_by(name=name).first()

        if not user:
            flash("Gebruiker niet gevonden", "error")
            return redirect(url_for("auth.login"))

        # Sessie instellen
        session["user_id"] = user.user_id
        session["role"] = user.role
        session["user_name"] = user.name

        # Route volgens rol
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        else:
            return redirect(url_for("driver.dashboard"))

    # GET: toon loginpagina
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
