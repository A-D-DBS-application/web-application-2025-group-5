# app/admin_routes.py
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import Route, User, Vehicle, Purchase_orders
from . import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -----------------------------
#  Helper: Check admin role
# -----------------------------
def require_admin():
    if session.get("role") != "admin":
        flash("Je hebt geen toegang tot dit gedeelte.", "error")
        return False
    return True


# -----------------------------
#  Dashboard
# -----------------------------
@admin_bp.route("/dashboard")
def dashboard():
    if not require_admin():
        return redirect(url_for("auth.login"))

    today = date.today()

    # Data ophalen voor dashboard tabs
    routes = Route.query.order_by(Route.route_date.desc()).all()
    drivers = User.query.filter_by(role="driver", is_active=True).all()
    vehicles = Vehicle.query.filter_by(is_active=True).all()
    orders = Purchase_orders.query.order_by(Purchase_orders.created_at.desc()).all()

    # Statistieken
    total_orders = Purchase_orders.query.count()
    pending_orders = Purchase_orders.query.filter_by(order_status="pending").count()
    active_routes = Route.query.filter(Route.route_status != "completed").count()

    return render_template(
        "admin_dashboard.html",
        today=today,
        routes=routes,
        drivers=drivers,
        vehicles=vehicles,
        orders=orders,
        total_orders=total_orders,
        pending_orders=pending_orders,
        active_routes=active_routes,
    )


# -----------------------------
#  Nieuwe Route Aanmaken
# -----------------------------
@admin_bp.route("/routes/new", methods=["GET", "POST"])
def create_route():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        driver_id = request.form.get("driver_id")
        vehicle_id = request.form.get("vehicle_id")
        route_date = request.form.get("route_date")

        if not driver_id:
            flash("Selecteer een driver.", "error")
            return redirect(url_for("admin.create_route"))

        route = Route(
            driver_id=driver_id,
            vehicle_id=vehicle_id if vehicle_id else None,
            created_by_user_id=session["user_id"],
            route_date=route_date,
            route_status="planned",
        )

        db.session.add(route)
        db.session.commit()

        flash("Route succesvol aangemaakt!", "success")
        return redirect(url_for("admin.dashboard"))

    drivers = User.query.filter_by(role="driver", is_active=True).all()
    vehicles = Vehicle.query.filter_by(is_active=True).all()

    return render_template(
        "route_create.html",
        drivers=drivers,
        vehicles=vehicles
    )


# -----------------------------
#  Nieuwe Order Aanmaken (optioneel - als jullie modal gebruiken)
# -----------------------------
@admin_bp.route("/orders/new", methods=["GET", "POST"])
def create_order():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        delivery_address = request.form.get("delivery_address")
        delivery_phone = request.form.get("delivery_phone")
        start_time = request.form.get("delivery_window_start")
        end_time = request.form.get("delivery_window_end")
        weight = request.form.get("total_weight_kg")
        status = request.form.get("order_status")
        payment = request.form.get("payment_status")

        order = Purchase_orders(
            customer_id=customer_id,
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
            delivery_window_start=start_time,
            delivery_window_end=end_time,
            total_weight_kg=weight,
            order_status=status,
            payment_status=payment,
            created_at=date.today(),
            updated_at=date.today()
        )

        db.session.add(order)
        db.session.commit()

        flash("Nieuwe order toegevoegd!", "success")
        return redirect(url_for("admin.dashboard"))

    # Later kunnen we hier klanten ophalen:
    customers = []  # Placeholder
    return render_template("order_create.html", customers=customers)


# -----------------------------
#  Nieuw Voertuig Aanmaken
# -----------------------------
@admin_bp.route("/vehicles/new", methods=["GET", "POST"])
def create_vehicle():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        license_plate = request.form.get("license_plate")
        brand = request.form.get("brand")
        model = request.form.get("model")
        capacity = request.form.get("capacity_kg")
        is_active = request.form.get("is_active") == "on"

        vehicle = Vehicle(
            license_plate=license_plate,
            brand=brand,
            model=model,
            capacity_kg=capacity,
            is_active=is_active,
        )

        db.session.add(vehicle)
        db.session.commit()

        flash("Voertuig succesvol toegevoegd!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("vehicle_create.html")
