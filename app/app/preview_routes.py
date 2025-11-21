from datetime import date
from flask import Blueprint, render_template

preview_bp = Blueprint("preview", __name__, url_prefix="/preview")


@preview_bp.route("/login")
def preview_login():
    return render_template("login.html")


@preview_bp.route("/admin/dashboard")
def preview_admin_dashboard():
    # Provide minimal placeholders so template can render
    today = date.today()
    return render_template(
        "admin_dashboard.html",
        today=today,
        routes=[],
        drivers=[],
        vehicles=[],
        orders=[],
        total_orders=0,
        pending_orders=0,
        active_routes=0,
    )


@preview_bp.route("/admin/routes/new")
def preview_route_create():
    return render_template("route_create.html", drivers=[], vehicles=[])


@preview_bp.route("/admin/orders/new")
def preview_order_create():
    return render_template("order_create.html", customers=[])


@preview_bp.route("/admin/vehicles/new")
def preview_vehicle_create():
    return render_template("vehicle_create.html")


@preview_bp.route("/driver/dashboard")
def preview_driver_dashboard():
    today = date.today()
    return render_template("driver_dashboard.html", today=today, route=None, deliveries=[])
