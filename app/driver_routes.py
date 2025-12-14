from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from .models import Route, RouteDelivery, User
from . import db
from app.admin_routes import update_route_status_if_completed


driver_bp = Blueprint("driver", __name__, url_prefix="/driver")


# -----------------------------------------------------
# ROLE CHECK
# -----------------------------------------------------
def require_driver_role():
    """
    Driver-rol vereist.
    Admin + driver = OK
    """
    return current_user.is_authenticated and current_user.has_role("driver")


# -----------------------------------------------------
# DASHBOARD
# -----------------------------------------------------
@driver_bp.route("/dashboard")
@login_required
def dashboard():

    # -------------------------------------------------
    # VIEW MODE (admin / driver)
    # -------------------------------------------------
    view_mode = request.args.get("view", "driver")

    if current_user.has_role("admin") and current_user.has_role("driver"):
        view_mode = view_mode
    else:
        view_mode = "driver"

    # -------------------------------------------------
    # DRIVER SELECTIE
    # -------------------------------------------------
    if view_mode == "admin" and current_user.has_role("admin"):
        all_drivers = User.query.filter(User.roles.contains("driver")).all()

        selected_driver_id = request.args.get("driver_id", type=int)
        if not selected_driver_id and all_drivers:
            selected_driver_id = all_drivers[0].user_id

        driver_id = selected_driver_id
    else:
        if not require_driver_role():
            flash("Je hebt geen toegang tot deze pagina.", "error")
            return redirect(url_for("auth.login"))

        driver_id = current_user.user_id
        selected_driver_id = driver_id
        all_drivers = None

    # -------------------------------------------------
    # DATUM SELECTIE (ADMIN DAG FILTER)
    # -------------------------------------------------
    selected_date_str = request.args.get("date")

    if view_mode == "admin" and selected_date_str:
        try:
            selected_date = datetime.strptime(
                selected_date_str, "%Y-%m-%d"
            ).date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    today = selected_date
    tomorrow = today + timedelta(days=1)

    # -------------------------------------------------
    # HELPER: ROUTE + DELIVERIES
    # -------------------------------------------------
    def get_route_with_deliveries(driver_id, route_date):
        route = Route.query.filter_by(
            driver_id=driver_id,
            route_date=route_date
        ).first()

        deliveries = []
        if route:
            deliveries = (
                RouteDelivery.query
                .filter_by(route_id=route.route_id)
                .order_by(RouteDelivery.sequence.asc())
                .all()
            )

        return route, deliveries

    # -------------------------------------------------
    # ROUTES OPHALEN
    # -------------------------------------------------
    route_today, deliveries_today = get_route_with_deliveries(
        driver_id=driver_id,
        route_date=today
    )

    route_tomorrow, deliveries_tomorrow = get_route_with_deliveries(
        driver_id=driver_id,
        route_date=tomorrow
    )

    # -------------------------------------------------
    # RENDER
    # -------------------------------------------------
    return render_template(
        "driver_dashboard.html",
        view_mode=view_mode,
        today=today,
        tomorrow=tomorrow,
        route_today=route_today,
        route_tomorrow=route_tomorrow,
        deliveries_today=deliveries_today,
        deliveries_tomorrow=deliveries_tomorrow,
        all_drivers=all_drivers,
        selected_driver_id=selected_driver_id,
    )

# -----------------------------------------------------
# MARK DELIVERY AS COMPLETED
# -----------------------------------------------------
@driver_bp.route("/delivery/<int:delivery_id>/update", methods=["POST"])
@login_required
def update_delivery_status(delivery_id):

    if not require_driver_role():
        flash("Alleen drivers kunnen leveringen aanpassen.", "error")
        return redirect(url_for("driver.dashboard"))

    delivery = RouteDelivery.query.get_or_404(delivery_id)

    # Toegang
    if (
        not current_user.has_role("admin")
        and delivery.route.driver_id != current_user.user_id
    ):
        flash("Je mag alleen jouw eigen leveringen aanpassen.", "error")
        return redirect(url_for("driver.dashboard"))

    action = request.form.get("action")
    comment = (request.form.get("delivery_comment") or "").strip()

    # Niet geleverd → comment verplicht
    if action == "not_delivered" and not comment:
        flash("Geef een reden op waarom deze levering niet kon gebeuren.", "error")
        return redirect(request.referrer or url_for("driver.dashboard"))

    if action == "delivered":
        delivery.delivery_status = "delivered"
        delivery.delivery_at = datetime.utcnow()
        delivery.order.order_status = "delivered"

    elif action == "not_delivered":
        delivery.delivery_status = "not_delivered"

    delivery.delivery_comment = comment
    db.session.commit()
    update_route_status_if_completed(delivery.route_id)

    flash("Leveringsstatus bijgewerkt.", "success")
    return redirect(request.referrer or url_for("driver.dashboard"))
