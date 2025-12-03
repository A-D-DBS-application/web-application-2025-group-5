# app/admin_routes.py

from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from sqlalchemy import or_
from .models import Route, User, Vehicle, Purchase_orders, Customer, Route_Delivery
from . import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -------------------------------------------
#  Protect admin routes
# -------------------------------------------
def require_admin():
    if session.get("role") != "admin":
        flash("Je hebt geen toegang tot dit gedeelte.", "error")
        return False
    return True


# -------------------------------------------
#  DASHBOARD MET DATUMFILTER + ZOEKFUNCTIE
# -------------------------------------------
@admin_bp.route("/dashboard")
def dashboard():
    if not require_admin():
        return redirect(url_for("auth.login"))

    today = date.today()

    # -------------------------------------------
    # ROUTE DATUMFILTER
    # -------------------------------------------
    selected_route_date = request.args.get("route_date")
    routes_query = Route.query.order_by(Route.route_date.desc())

    date_obj = None
    if selected_route_date:
        try:
            date_obj = datetime.strptime(selected_route_date, "%Y-%m-%d").date()
            routes_query = routes_query.filter(Route.route_date == date_obj)
        except ValueError:
            pass

    routes = routes_query.all()

    drivers = User.query.filter_by(role="driver", is_active=True).all()
    vehicles = Vehicle.query.filter_by(is_active=True).all()

    # -------------------------------------------
    # ORDER ZOEKFILTER
    # -------------------------------------------
    search_raw = request.args.get("q")
    search = (search_raw or "").strip()

    if search_raw is not None and search == "":
        return redirect(url_for("admin.dashboard"))

    if search:
        pattern = f"%{search}%"

        filters = [
            Purchase_orders.delivery_address.ilike(pattern),
            Purchase_orders.delivery_phone.ilike(pattern),
            Purchase_orders.order_status.ilike(pattern),
            Purchase_orders.payment_status.ilike(pattern),
            Customer.first_name.ilike(pattern),
            Customer.last_name.ilike(pattern),
            Customer.customer.ilike(pattern),
            Customer.street_number.ilike(pattern),
        ]

        if search.isdigit():
            num = int(search)
            filters += [
                Purchase_orders.order_id == num,
                Purchase_orders.total_weight_kg == num,
            ]
        else:
            filters.append(Purchase_orders.order_id.cast(db.Text).ilike(pattern))

        orders = (
            Purchase_orders.query
            .join(Customer)
            .filter(or_(*filters))
            .order_by(Purchase_orders.created_at.desc())
            .all()
        )
    else:
        orders = Purchase_orders.query.order_by(Purchase_orders.created_at.desc()).all()

    # -------------------------------------------
    # RENDER DASHBOARD
    # -------------------------------------------
    return render_template(
        "admin_dashboard.html",
        today=today,
        routes=routes,
        drivers=drivers,
        vehicles=vehicles,
        orders=orders,
        total_orders=Purchase_orders.query.count(),
        pending_orders=Purchase_orders.query.filter_by(order_status="pending").count(),
        active_routes=Route.query.filter(Route.route_status != "completed").count(),
        selected_route_date=date_obj,   # <-- BELANGRIJK!
    )


# -------------------------------------------
#  ROUTE AANMAKEN
# -------------------------------------------
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
            vehicle_id=vehicle_id or None,
            created_by_user_id=session["user_id"],
            route_date=route_date,
            route_status="planned",
        )

        db.session.add(route)
        db.session.commit()

        flash("Route succesvol aangemaakt!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template(
        "route_create.html",
        drivers=User.query.filter_by(role="driver", is_active=True).all(),
        vehicles=Vehicle.query.filter_by(is_active=True).all(),
    )


# -------------------------------------------
#  ORDER AANMAKEN
# -------------------------------------------
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

        qty_vat = int(request.form.get("qty_vat") or 0)
        qty_fles = int(request.form.get("qty_fles") or 0)
        qty_bib = int(request.form.get("qty_bib") or 0)

        total_weight = qty_vat * 65 + qty_fles * 1.5 + qty_bib * 4

        order = Purchase_orders(
            customer_id=customer_id,
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
            delivery_window_start=start_time,
            delivery_window_end=end_time,
            total_weight_kg=total_weight,
            order_status=request.form.get("order_status"),
            payment_status=request.form.get("payment_status"),
            created_at=date.today(),
            updated_at=date.today(),
        )

        db.session.add(order)
        db.session.commit()

        flash("Nieuwe order toegevoegd!", "success")
        return redirect(url_for("admin.dashboard"))
    default_date = date.today().strftime("%Y-%m-%d")
    return render_template("order_create.html", default_date=default_date)


# -------------------------------------------
#  ORDERS TOEWIJZEN AAN ROUTE
# -------------------------------------------
@admin_bp.route("/routes/<int:route_id>/assign", methods=["GET", "POST"])
def assign_orders(route_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    route = Route.query.get_or_404(route_id)

    if request.method == "POST":
        order_ids = request.form.getlist("order_ids")

        if not order_ids:
            flash("Selecteer minstens één bestelling.", "error")
            return redirect(url_for("admin.assign_orders", route_id=route_id))

        current_max = max([d.sequence for d in route.deliveries], default=0)

        for idx, oid in enumerate(order_ids, start=1):
            delivery = Route_Delivery(
                route_id=route.route_id,
                order_id=int(oid),
                sequence=current_max + idx,
                delivery_status="planned",
            )
            db.session.add(delivery)

        db.session.commit()
        flash("Bestellingen toegewezen!", "success")
        return redirect(url_for("admin.dashboard"))

    delivery_date = request.args.get("delivery_date")

    if delivery_date:
        try:
            selected_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
        except ValueError:
            selected_date = route.route_date
    else:
        selected_date = route.route_date

    available_orders = (
        Purchase_orders.query
        .filter(
            db.func.date(Purchase_orders.delivery_window_end) == selected_date,
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


# -------------------------------------------
#  ROUTE VERWIJDEREN
# -------------------------------------------
@admin_bp.route("/routes/<int:route_id>/delete", methods=["POST"])
def delete_route(route_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    Route_Delivery.query.filter_by(route_id=route_id).delete()
    Route.query.filter_by(route_id=route_id).delete()

    db.session.commit()
    flash("Route verwijderd.", "success")
    return redirect(url_for("admin.dashboard"))


# -------------------------------------------
#  KLANT ZOEKFUNCTIE (AJAX)
# -------------------------------------------
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
            Customer.last_name.ilike(f"%{q}%"),
        )
    ).limit(10).all()

    return jsonify([
        {
            "id": c.customer_id,
            "name": f"{(c.first_name or '').strip()} {(c.last_name or '').strip()}".strip(),
            "customer": c.customer,
            "address": f"{c.street_number}, {c.postal_code} {c.city}",
            "phone": c.phone or c.celphone,
        }
        for c in customers
    ])


# -------------------------------------------
#  NIEUW VOERTUIG
# -------------------------------------------
@admin_bp.route("/vehicles/new", methods=["GET", "POST"])
def create_vehicle():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        vehicle = Vehicle(
            license_plate=request.form.get("license_plate"),
            brand=request.form.get("brand"),
            model=request.form.get("model"),
            color=request.form.get("color"),
            capacity_kg=request.form.get("capacity_kg"),
            fuel_type=request.form.get("fuel_type"),
            is_active=(request.form.get("is_active") == "on"),
        )

        db.session.add(vehicle)
        db.session.commit()

        flash("Voertuig toegevoegd!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("vehicle_create.html")


# -------------------------------------------
#  NIEUWE USER
# -------------------------------------------
@admin_bp.route("/users/new", methods=["GET", "POST"])
def create_user():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        role = request.form.get("role")

        if not name or not email or not role:
            flash("Alle velden verplicht.", "error")
            return redirect(url_for("admin.create_user"))

        user = User(
            name=name,
            email=email,
            password_hash="",
            role=role,
            is_active=True,
        )

        db.session.add(user)
        db.session.commit()

        flash("Gebruiker aangemaakt!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("user_create.html")
