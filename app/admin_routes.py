# app/admin_routes.py

from datetime import date, datetime
from sqlalchemy import or_
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from .models import Route, User, Vehicle, Purchase_orders, Customer, Route_Delivery
from . import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def require_admin():
    if session.get("role") != "admin":
        flash("Je hebt geen toegang tot dit gedeelte.", "error")
        return False
    return True
# -----------------------------
#  Helper: Check admin role
# -----------------------------
@admin_bp.route("/dashboard")
def dashboard():
    if not require_admin():
        return redirect(url_for("auth.login"))

    today = date.today()

    # ===========================
    # ROUTE FILTER (op datum)
    # ===========================
    route_date_str = request.args.get("route_date")
    selected_route_date = None

    if route_date_str:
        try:
            selected_route_date = datetime.strptime(route_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_route_date = None

    # ===========================
    # ROUTES OPHALEN
    # - Filter indien datum geselecteerd
    # - Altijd oplopend sorteren (oud -> nieuw)
    # ===========================
    if selected_route_date:
        routes = (
            Route.query
            .filter(Route.route_date == selected_route_date)
            .order_by(Route.route_date.asc())
            .all()
        )
    else:
        routes = Route.query.order_by(Route.route_date.asc()).all()

    # ===========================
    # DRIVERS & VEHICLES
    # ===========================
    drivers = User.query.filter_by(role="driver", is_active=True).all()
    vehicles = Vehicle.query.filter_by(is_active=True).all()

    # ===========================
    # ORDER SEARCH
    # ===========================
    search_raw = request.args.get("q")
    search = (search_raw or "").strip()

    if search_raw is not None and search == "":
        return redirect(url_for("admin.dashboard"))

    if search:
        search_pattern = f"%{search}%"

        filters = [
            Purchase_orders.delivery_address.ilike(search_pattern),
            Purchase_orders.delivery_phone.ilike(search_pattern),
            Purchase_orders.order_status.ilike(search_pattern),
            Purchase_orders.payment_status.ilike(search_pattern),
            Customer.first_name.ilike(search_pattern),
            Customer.last_name.ilike(search_pattern),
            Customer.customer.ilike(search_pattern),
            Customer.street_number.ilike(search_pattern),
        ]

        if search.isdigit():
            num = int(search)
            filters.append(Purchase_orders.order_id == num)
            filters.append(Purchase_orders.total_weight_kg == num)
        else:
            filters.append(Purchase_orders.order_id.cast(db.Text).ilike(search_pattern))

        orders = (
            Purchase_orders.query
            .join(Customer)
            .filter(or_(*filters))
            .order_by(Purchase_orders.created_at.desc())
            .all()
        )
    else:
        orders = Purchase_orders.query.order_by(Purchase_orders.created_at.desc()).all()

    # ===========================
    # COUNTERS
    # ===========================
    total_orders = Purchase_orders.query.count()
    pending_orders = Purchase_orders.query.filter_by(order_status="pending").count()
    active_routes = Route.query.filter(Route.route_status != "completed").count()

    # ===========================
    # TEMPLATE RENDER
    # ===========================
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
        selected_route_date=selected_route_date,
    )

# -----------------------------
#  NIEUWE ROUTE AANMAKEN
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

    return render_template("route_create.html", drivers=drivers, vehicles=vehicles)


# -----------------------------
#  BESTELLINGEN TOEWIJZEN AAN ROUTE
# -----------------------------
@admin_bp.route("/routes/<int:route_id>/assign", methods=["GET", "POST"])
def assign_orders(route_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    route = Route.query.get_or_404(route_id)

    if request.method == "POST":
        order_ids = request.form.getlist("order_ids")
        if not order_ids:
            flash("Selecteer minstens één bestelling om toe te wijzen.", "error")
            return redirect(url_for("admin.assign_orders", route_id=route_id))

        current_max_seq = 0
        if route.deliveries:
            current_max_seq = max(d.sequence for d in route.deliveries)

        for idx, oid in enumerate(order_ids, start=1):
            delivery = Route_Delivery(
                route_id=route.route_id,
                order_id=int(oid),
                sequence=current_max_seq + idx,
                delivery_status="planned",
            )
            db.session.add(delivery)

        db.session.commit()
        flash("Bestellingen succesvol aan de route toegewezen!", "success")
        return redirect(url_for("admin.dashboard"))

    delivery_date_str = request.args.get("delivery_date")
    if delivery_date_str:
        try:
            selected_date = datetime.strptime(delivery_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = route.route_date
    else:
        selected_date = route.route_date

    available_orders = (
        Purchase_orders.query
        .filter(
            db.func.date(Purchase_orders.delivery_window_start) == selected_date,
            ~Purchase_orders.route_links.any()
        )
        .order_by(Purchase_orders.order_id.asc())
        .all()
    )

    return render_template(
        "route_assign.html",
        route=route,
        selected_date=selected_date,
        available_orders=available_orders,
    )


# -----------------------------
#  ROUTE VERWIJDEREN
# -----------------------------
@admin_bp.route("/routes/<int:route_id>/delete", methods=["POST"])
def delete_route(route_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    route = Route.query.get_or_404(route_id)

    Route_Delivery.query.filter_by(route_id=route.route_id).delete()
    db.session.delete(route)
    db.session.commit()

    flash("Route succesvol verwijderd.", "success")
    return redirect(url_for("admin.dashboard"))


# -----------------------------
#  KLANT ZOEKFUNCTIE (AJAX)
# -----------------------------
@admin_bp.route("/customers/search")
def search_customers():
    if not require_admin():
        return jsonify([])

    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    customers = Customer.query.filter(
        or_(
            Customer.customer.ilike(f"%{q}%"),
            Customer.first_name.ilike(f"%{q}%"),
            Customer.last_name.ilike(f"%{q}%")
        )
    ).limit(10).all()

    return jsonify([
        {
            "id": c.customer_id,
            "name": f"{(c.first_name or '').strip()} {(c.last_name or '').strip()}".strip(),
            "customer": c.customer,
            "address": f"{c.street_number}, {c.postal_code} {c.city}",
            "phone": c.phone or c.celphone
        }
        for c in customers
    ])


# -----------------------------
#  NIEUW VOERTUIG AANMAKEN
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
        fuel_type = request.form.get("fuel_type")
        color = request.form.get("color")
        is_active = request.form.get("is_active") == "on"

        vehicle = Vehicle(
            license_plate=license_plate,
            brand=brand,
            model=model,
            color=color,
            capacity_kg=capacity,
            fuel_type=fuel_type,
            is_active=is_active,
        )

        db.session.add(vehicle)
        db.session.commit()

        flash("Voertuig succesvol toegevoegd!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("vehicle_create.html")


# -----------------------------
#  NIEUW ACCOUNT AANMAKEN
# -----------------------------
@admin_bp.route("/users/new", methods=["GET", "POST"])
def create_user():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        role = request.form.get("role")

        if not name or not email or not role:
            flash("Alle verplichte velden moeten ingevuld zijn.", "error")
            return redirect(url_for("admin.create_user"))

        new_user = User(
            name=name,
            email=email,
            password_hash="",
            role=role,
            is_active=True
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Nieuw account succesvol aangemaakt!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("user_create.html")

@admin_bp.route("/orders/new", methods=["GET", "POST"])
def create_order():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        start_time = request.form.get("delivery_window_start")
        end_time = request.form.get("delivery_window_end")
        weight = request.form.get("total_weight_kg")
        status = request.form.get("order_status")
        payment = request.form.get("payment_status")

        order = Purchase_orders(
            customer_id=customer_id,
            delivery_window_start=start_time,
            delivery_window_end=end_time,
            total_weight_kg=weight,
            order_status=status,
            payment_status=payment
        )

        db.session.add(order)
        db.session.commit()

        flash("Nieuwe order toegevoegd!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("order_create.html")

