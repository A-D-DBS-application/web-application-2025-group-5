# app/driver_routes.py

from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Route, RouteDelivery, User
from . import db

driver_bp = Blueprint("driver", __name__, url_prefix="/driver")


# -----------------------------------------------------
# ROLE CHECK (voor echte drivers, niet admin)
# -----------------------------------------------------
def require_driver_role():
    """Alleen echte drivers mogen acties uitvoeren (leveren / commentaren)."""
    return current_user.is_authenticated and current_user.has_role("driver")


# -----------------------------------------------------
# DASHBOARD
# -----------------------------------------------------
@driver_bp.route("/dashboard")
@login_required
def dashboard():

    # =====================================================================
    # ADMIN BEKIJK-MODUS
    # =====================================================================
    if current_user.has_role("admin"):
        # Admin kan kiezen welke driver hij wil bekijken
        selected_driver_id = request.args.get("driver_id", type=int)

        # Alle drivers ophalen
        all_drivers = User.query.filter(User.roles.contains("driver")).all()

        # Default: eerste driver in lijst
        if not selected_driver_id and all_drivers:
            selected_driver_id = all_drivers[0].user_id

        driver_id = selected_driver_id

    # =====================================================================
    # DEFAULT DRIVER-MODUS
    # =====================================================================
    else:
        if not require_driver_role():
            flash("Je hebt geen toegang tot deze pagina.", "error")
            return redirect(url_for("auth.login"))

        driver_id = current_user.user_id
        all_drivers = None
        selected_driver_id = None

    # =====================================================================
    # ROUTES OPHALEN
    # =====================================================================
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Route van vandaag
    route_today = Route.query.filter_by(driver_id=driver_id, route_date=today).first()
    deliveries_today = (
        RouteDelivery.query.filter_by(route_id=route_today.route_id)
        .order_by(RouteDelivery.sequence.asc())
        .all()
        if route_today else []
    )

    # Route van morgen
    route_tomorrow = Route.query.filter_by(driver_id=driver_id, route_date=tomorrow).first()
    deliveries_tomorrow = (
        RouteDelivery.query.filter_by(route_id=route_tomorrow.route_id)
        .order_by(RouteDelivery.sequence.asc())
        .all()
        if route_tomorrow else []
    )

    return render_template(
        "driver_dashboard.html",
        today=today,
        tomorrow=tomorrow,
        route_today=route_today,
        route_tomorrow=route_tomorrow,
        deliveries_today=deliveries_today,
        deliveries_tomorrow=deliveries_tomorrow,
        all_drivers=all_drivers,
        selected_driver_id=selected_driver_id
    )


# -----------------------------------------------------
# MARK DELIVERY AS COMPLETED  (ONLY REAL DRIVERS)
# -----------------------------------------------------
@driver_bp.route("/delivery/<int:delivery_id>/delivered", methods=["POST"])
@login_required
def mark_delivered(delivery_id):

    # Admin mag GEEN leveringen markeren
    if not require_driver_role():
        flash("Alleen drivers kunnen bestellingen afleveren.", "error")
        return redirect(url_for("driver.dashboard"))

    delivery = RouteDelivery.query.get_or_404(delivery_id)

    # Controle: route moet van ingelogde driver zijn
    if delivery.route.driver_id != current_user.user_id:
        flash("Je mag alleen jouw eigen leveringen bevestigen.", "error")
        return redirect(url_for("driver.dashboard"))

    # Update status
    delivery.delivery_status = "delivered"
    delivery.delivery_at = datetime.utcnow()
    delivery.order.order_status = "delivered"

    db.session.commit()
    flash("Order gemarkeerd als geleverd.", "success")
    return redirect(request.referrer or url_for("driver.dashboard"))


# -----------------------------------------------------
# SAVE COMMENT  (ONLY REAL DRIVERS)
# -----------------------------------------------------
@driver_bp.route("/delivery/<int:delivery_id>/comment", methods=["POST"])
@login_required
def save_comment(delivery_id):

    if not require_driver_role():
        flash("Alleen drivers kunnen opmerkingen toevoegen.", "error")
        return redirect(url_for("driver.dashboard"))

    delivery = RouteDelivery.query.get_or_404(delivery_id)

    # Controle eigenaar route
    if delivery.route.driver_id != current_user.user_id:
        flash("Je mag alleen opmerkingen plaatsen bij jouw eigen orders.", "error")
        return redirect(url_for("driver.dashboard"))

    comment = request.form.get("comment")
    delivery.delivery_comment = comment
    delivery.order.order_status = "delivered"

    db.session.commit()

    flash("Opmerking opgeslagen!", "success")
    return redirect(request.referrer or url_for("driver.dashboard"))
