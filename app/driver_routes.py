# app/driver_routes.py
from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from .models import Route, Route_Delivery
from . import db

driver_bp = Blueprint("driver", __name__, url_prefix="/driver")


# ---------------------------------------
# Helper
# ---------------------------------------
def require_driver():
    if session.get("role") != "driver":
        flash("Je hebt geen toegang tot deze pagina.", "error")
        return False
    return True


# ---------------------------------------
# Dashboard
# ---------------------------------------
@driver_bp.route("/dashboard")
def dashboard():
    if not require_driver():
        return redirect(url_for("auth.login"))

    driver_id = session.get("user_id")
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Route vandaag
    route_today = Route.query.filter_by(driver_id=driver_id, route_date=today).first()
    deliveries_today = []
    if route_today:
        deliveries_today = Route_Delivery.query.filter_by(
            route_id=route_today.route_id
        ).order_by(Route_Delivery.sequence.asc()).all()

    # Route morgen
    route_tomorrow = Route.query.filter_by(driver_id=driver_id, route_date=tomorrow).first()
    deliveries_tomorrow = []
    if route_tomorrow:
        deliveries_tomorrow = Route_Delivery.query.filter_by(
            route_id=route_tomorrow.route_id
        ).order_by(Route_Delivery.sequence.asc()).all()

    return render_template(
        "driver_dashboard.html",
        today=today,
        tomorrow=tomorrow,
        route_today=route_today,
        route_tomorrow=route_tomorrow,
        deliveries_today=deliveries_today,
        deliveries_tomorrow=deliveries_tomorrow
    )


# ---------------------------------------
# Markeer levering als GELEVERD
# ---------------------------------------
@driver_bp.route("/delivery/<int:delivery_id>/delivered", methods=["POST"])
def mark_delivered(delivery_id):
    if not require_driver():
        return redirect(url_for("auth.login"))

    delivery = Route_Delivery.query.get_or_404(delivery_id)
    order = delivery.order  # <<-- relatie nodig

    delivery.delivery_status = "delivered"
    delivery.delivery_at = datetime.utcnow()

    # UPDATE ORDER
    order.order_status = "delivered"

    db.session.commit()

    flash("Order gemarkeerd als geleverd.", "success")
    return redirect(request.referrer or url_for("driver.dashboard"))


# --------------------------------------
# Comment toevoegen
# ---------------------------------------
@driver_bp.route("/delivery/<int:delivery_id>/comment", methods=["POST"])
def save_comment(delivery_id):
    if not require_driver():
        return redirect(url_for("auth.login"))

    delivery = Route_Delivery.query.get_or_404(delivery_id)

    delivery.delivery_comment = request.form.get("comment")
    delivery.order.order_status = "delivered"  # veiligheid

    db.session.commit()

    flash("Opmerking opgeslagen!", "success")
    return redirect(request.referrer or url_for("driver.dashboard"))
