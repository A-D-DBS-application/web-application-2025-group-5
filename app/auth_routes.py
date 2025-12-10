from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from .models import User

auth_bp = Blueprint("auth", __name__)


# --------------------------------------------
# LOGIN
# --------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # Reeds ingelogd → redirect volgens rol
        if current_user.has_role("admin"):
            return redirect(url_for("admin.dashboard"))
        elif current_user.has_role("driver"):
            return redirect(url_for("driver.dashboard"))

    if request.method == "POST":
        name = request.form.get("name")

        user = User.query.filter_by(name=name).first()
        if not user:
            flash("Gebruiker niet gevonden.", "error")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("Je account is gedeactiveerd.", "error")
            return redirect(url_for("auth.login"))

        # Log de gebruiker in met flask_login
        login_user(user)   # ⬅ GEEN session[] meer gebruiken!

        # Redirect volgens rol
        if user.has_role("admin"):
            return redirect(url_for("admin.dashboard"))
        elif user.has_role("driver"):
            return redirect(url_for("driver.dashboard"))
        else:
            flash("Geen geldige rol aan deze gebruiker gekoppeld!", "error")
            logout_user()
            return redirect(url_for("auth.login"))

    return render_template("login.html")


# --------------------------------------------
# LOGOUT
# --------------------------------------------
@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
