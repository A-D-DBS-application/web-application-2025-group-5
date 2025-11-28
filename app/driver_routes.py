# app/driver_routes.py
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from .models import Route, Route_Delivery, Purchase_orders
from . import db

driver_bp = Blueprint("driver", __name__, url_prefix="/driver")


# -----------------------------
#  Helper: Check driver role
# -----------------------------
def require_driver():
    if session.get("role") != "driver":
        flash("Je hebt geen toegang tot deze pagina.", "error")
        return False
    return True


# -----------------------------
#  Dashboard (route van vandaag)
# -----------------------------
@driver_bp.route("/dashboard")
def dashboard():
    if not require_driver():
        return redirect(url_for("auth.login"))

    driver_id = session.get("user_id")
    today = date.today()

    # Vandaag + morgen berekenen
    from datetime import timedelta
    tomorrow = today + timedelta(days=1)

    # -------------------------
    # Route van vandaag ophalen
    # -------------------------
    route_today = Route.query.filter_by(
        driver_id=driver_id,
        route_date=today
    ).first()

    deliveries_today = []
    if route_today:
        deliveries_today = (
            Route_Delivery.query
            .filter_by(route_id=route_today.route_id)
            .order_by(Route_Delivery.sequence.asc())
            .all()
        )

    # -------------------------
    # Route van morgen ophalen
    # -------------------------
    route_tomorrow = Route.query.filter_by(
        driver_id=driver_id,
        route_date=tomorrow
    ).first()

    deliveries_tomorrow = []
    if route_tomorrow:
        deliveries_tomorrow = (
            Route_Delivery.query
            .filter_by(route_id=route_tomorrow.route_id)
            .order_by(Route_Delivery.sequence.asc())
            .all()
        )

    return render_template(
        "driver_dashboard.html",
        today=today,
        tomorrow=tomorrow,
        route_today=route_today,
        route_tomorrow=route_tomorrow,
        deliveries_today=deliveries_today,
        deliveries_tomorrow=deliveries_tomorrow
    )



# -----------------------------
#  Levering voltooien (future feature)
# -----------------------------
@driver_bp.route("/delivery/<int:route_delivery_id>/complete", methods=["POST"])
def complete_delivery(route_delivery_id):
    if not require_driver():
        return redirect(url_for("auth.login"))

    delivery = Route_Delivery.query.get(route_delivery_id)
    if not delivery:
        flash("Levering niet gevonden.", "error")
        return redirect(url_for("driver.dashboard"))

    delivery.delivery_status = "delivered"
    delivery.delivery_comment = request.form.get("comment", "")
    delivery.delivery_at = date.today()

    db.session.commit()

    flash("Levering gemarkeerd als voltooid.", "success")
    return redirect(url_for("driver.dashboard"))


# -----------------------------
#  Levering mislukt (future feature)
# -----------------------------
@driver_bp.route("/delivery/<int:route_delivery_id>/failed", methods=["POST"])
def fail_delivery(route_delivery_id):
    if not require_driver():
        return redirect(url_for("auth.login"))

    delivery = Route_Delivery.query.get(route_delivery_id)
    if not delivery:
        flash("Levering niet gevonden.", "error")
        return redirect(url_for("driver.dashboard"))

    delivery.delivery_status = "failed"
    delivery.delivery_comment = request.form.get("comment", "")
    delivery.delivery_at = date.today()

    db.session.commit()

    flash("Levering gemarkeerd als mislukt.", "warning")
    return redirect(url_for("driver.dashboard"))
