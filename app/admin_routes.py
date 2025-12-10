from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from sqlalchemy import or_
from flask_login import current_user, login_required
from .models import Route, User, Vehicle, PurchaseOrders, Customer, RouteDelivery
from . import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

WAREHOUSE_ADDRESS = "Industrieweg 202, 9030 Gent"


# -------------------------------------------
#  Protect admin routes (multi-role versie)
# -------------------------------------------
def require_admin():
    if not current_user.is_authenticated or not current_user.has_role("admin"):
        flash("Je hebt geen toegang tot dit gedeelte.", "error")
        return False
    return True


# -------------------------------------------
#  DASHBOARD
# -------------------------------------------
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not require_admin():
        return redirect(url_for("auth.login"))

    today = date.today()

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

    # ✓ Drivers (personen met rol 'driver')
    drivers = User.query.filter(User.roles.contains("driver"), User.is_active == True).all()

    vehicles = Vehicle.query.filter_by(is_active=True).all()

    # Alle users ophalen voor USERS-tab
    users = User.query.order_by(User.name.asc()).all()


    # -------------- ORDER SEARCH --------------
    search_raw = request.args.get("q")
    search = (search_raw or "").strip()

    if search_raw is not None and search == "":
        return redirect(url_for("admin.dashboard"))

    if search:
        pattern = f"%{search}%"
        filters = [
            PurchaseOrders.delivery_address.ilike(pattern),
            PurchaseOrders.delivery_phone.ilike(pattern),
            PurchaseOrders.order_status.ilike(pattern),
            PurchaseOrders.payment_status.ilike(pattern),
            Customer.first_name.ilike(pattern),
            Customer.last_name.ilike(pattern),
            Customer.customer.ilike(pattern),
            Customer.street_number.ilike(pattern),
        ]

        if search.isdigit():
            num = int(search)
            filters += [
                PurchaseOrders.order_id == num,
                PurchaseOrders.total_weight_kg == num,
            ]
        else:
            filters.append(PurchaseOrders.order_id.cast(db.Text).ilike(pattern))

        orders = (
            PurchaseOrders.query
            .join(Customer)
            .filter(or_(*filters))
            .order_by(PurchaseOrders.created_at.desc())
            .all()
        )
    else:
        orders = PurchaseOrders.query.order_by(PurchaseOrders.created_at.desc()).all()
    
    all_users = User.query.order_by(User.created_at.desc()).all()

    return render_template(
        "admin_dashboard.html",
        today=today,
        routes=routes,
        drivers=drivers,
        vehicles=vehicles,
        users=users,
        orders=orders,
        total_orders=PurchaseOrders.query.count(),
        pending_orders=PurchaseOrders.query.filter_by(order_status="pending").count(),
        active_routes=Route.query.filter(Route.route_status != "completed").count(),
        selected_route_date=date_obj,
        all_users=all_users,
    )


# -------------------------------------------
#  ROUTE AANMAKEN
# -------------------------------------------
@admin_bp.route("/routes/new", methods=["GET", "POST"])
@login_required
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
            created_by_user_id=current_user.user_id,
            route_date=route_date,
            route_status="planned",
        )

        db.session.add(route)
        db.session.commit()

        flash("Route succesvol aangemaakt!", "success")
        return redirect(url_for("admin.dashboard"))

    drivers = User.query.filter(User.roles.contains("driver"), User.is_active == True).all()

    return render_template(
        "route_create.html",
        drivers=drivers,
        vehicles=Vehicle.query.filter_by(is_active=True).all(),
    )


# -------------------------------------------
#  ORDER AANMAKEN
# -------------------------------------------
@admin_bp.route("/orders/new", methods=["GET", "POST"])
@login_required
def create_order():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        customer_id = request.form.get("customer_id")
        delivery_address = request.form.get("delivery_address")
        delivery_phone = request.form.get("delivery_phone")
        start_date = request.form.get("delivery_window_start")
        end_date = request.form.get("delivery_window_end")

        hour_start = request.form.get("delivery_hour_start") or "08:00"
        hour_end = request.form.get("delivery_hour_end") or "17:00"
        hour_start_obj = datetime.strptime(hour_start, "%H:%M").time()
        hour_end_obj = datetime.strptime(hour_end, "%H:%M").time()

        qty_vat = int(request.form.get("qty_vat") or 0)
        qty_fles = int(request.form.get("qty_fles") or 0)
        qty_bib = int(request.form.get("qty_bib") or 0)

        total_weight = qty_vat * 65 + qty_fles * 1.5 + qty_bib * 4

        order = PurchaseOrders(
            customer_id=customer_id,
            delivery_address=delivery_address,
            delivery_phone=delivery_phone,
            delivery_window_start=start_date,
            delivery_window_end=end_date,
            delivery_hour_start=hour_start_obj,
            delivery_hour_end=hour_end_obj,
            total_weight_kg=total_weight,
            order_status=request.form.get("order_status", "confirmed"),
            payment_status=request.form.get("payment_status"),
            qty_vat=qty_vat,
            qty_fles=qty_fles,
            qty_bib=qty_bib,
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
#  ORDERS TOEWIJZEN + ROUTE OPTIMALISATIE
# -------------------------------------------
@admin_bp.route("/routes/<int:route_id>/assign", methods=["GET", "POST"])
@login_required
def assign_orders(route_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    from app.utils.route_utils import get_distance_matrix, optimize_route
    from app.utils.mapbox_utils import geocode_address

    route = Route.query.get_or_404(route_id)

    # POST ------------------------------
    if request.method == "POST":
        order_ids = request.form.getlist("order_ids")

        if not order_ids:
            flash("Selecteer minstens één bestelling.", "error")
            return redirect(url_for("admin.assign_orders", route_id=route_id))

        orders = [PurchaseOrders.query.get(int(oid)) for oid in order_ids]

        warehouse_coords = geocode_address(WAREHOUSE_ADDRESS)
        if not warehouse_coords:
            flash("Magazijnadres kon niet gevonden worden.", "error")
            return redirect(url_for("admin.assign_orders", route_id=route_id))

        coords = [warehouse_coords]
        for o in orders:
            c = geocode_address(o.delivery_address)
            if not c:
                flash(f"Adres niet gevonden: {o.delivery_address}", "error")
                return redirect(url_for("admin.assign_orders", route_id=route_id))
            coords.append(c)

        distance_matrix = get_distance_matrix(coords)
        if not distance_matrix:
            flash("Kon distance matrix niet berekenen.", "error")
            return redirect(url_for("admin.assign_orders", route_id=route_id))

        optimal_route_indices = optimize_route(distance_matrix)

        RouteDelivery.query.filter_by(route_id=route.route_id).delete()

        seq = 1
        for idx in optimal_route_indices:
            if idx == 0:
                continue
            order_obj = orders[idx - 1]
            db.session.add(RouteDelivery(
                route_id=route.route_id,
                order_id=order_obj.order_id,
                sequence=seq,
                delivery_status="planned",
            ))
            seq += 1

        db.session.commit()

        flash("Route geoptimaliseerd!", "success")
        return redirect(url_for("admin.dashboard"))

    # GET ------------------------------

    delivery_date = request.args.get("delivery_date")
    if delivery_date:
        try:
            selected_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
        except:
            selected_date = route.route_date
    else:
        selected_date = route.route_date

    assigned_orders = (
        PurchaseOrders.query
        .join(RouteDelivery, PurchaseOrders.order_id == RouteDelivery.order_id)
        .filter(RouteDelivery.route_id == route.route_id)
        .all()
    )

    current_weight = sum(float(o.total_weight_kg or 0) for o in assigned_orders)

    available_orders = (
        PurchaseOrders.query
        .filter(
            db.func.date(PurchaseOrders.delivery_window_end) == selected_date,
            ~PurchaseOrders.route_links.any()
        )
        .order_by(PurchaseOrders.order_id.asc())
        .all()
    )

    return render_template(
        "route_assign.html",
        route=route,
        selected_date=selected_date,
        assigned_orders=assigned_orders,
        available_orders=available_orders,
        current_weight=current_weight,
        capacity=float(route.vehicle.capacity_kg),
    )


# -------------------------------------------
# UPDATE ORDER
# -------------------------------------------
@admin_bp.route("/orders/<int:order_id>/edit", methods=["GET", "POST"])
@login_required
def edit_order(order_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    order = PurchaseOrders.query.get_or_404(order_id)

    if request.method == "POST":
        order.total_weight_kg = request.form.get("total_weight_kg")
        order.qty_vat = request.form.get("qty_vat")
        order.qty_fles = request.form.get("qty_fles")
        order.qty_bib = request.form.get("qty_bib")

        delivery_date = request.form.get("delivery_date")
        if delivery_date:
            order.delivery_window_end = datetime.strptime(delivery_date, "%Y-%m-%d")

        order.order_status = request.form.get("order_status")
        order.payment_status = request.form.get("payment_status")

        db.session.commit()
        flash("Order bijgewerkt!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("order_edit.html", order=order)


# -------------------------------------------
# DELETE ORDER
# -------------------------------------------
@admin_bp.route("/orders/<int:order_id>/delete", methods=["POST"])
@login_required
def delete_order(order_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    RouteDelivery.query.filter_by(order_id=order_id).delete()

    order = PurchaseOrders.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()

    flash("Order verwijderd.", "success")
    return redirect(url_for("admin.dashboard"))


# -------------------------------------------
# DELETE ROUTE
# -------------------------------------------
@admin_bp.route("/routes/<int:route_id>/delete", methods=["POST"])
@login_required
def delete_route(route_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    RouteDelivery.query.filter_by(route_id=route_id).delete()
    Route.query.filter_by(route_id=route_id).delete()

    db.session.commit()
    flash("Route verwijderd.", "success")
    return redirect(url_for("admin.dashboard"))


# -------------------------------------------
# CUSTOMER SEARCH (AJAX)
# -------------------------------------------
@admin_bp.route("/customers/search")
@login_required
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
# VOERTUIG AANMAKEN
# -------------------------------------------
@admin_bp.route("/vehicles/new", methods=["GET", "POST"])
@login_required
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
# USER AANMAKEN (multi-role)
# -------------------------------------------
@admin_bp.route("/users/new", methods=["GET", "POST"])
@login_required
def create_user():
    if not require_admin():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        selected_roles = request.form.getlist("roles")

        if not name or not email or not selected_roles:
            flash("Naam, email en minstens één rol verplicht.", "error")
            return redirect(url_for("admin.create_user"))

        roles_str = ",".join(selected_roles)

        # FIXED ❗ Removed invalid db.Column() assignments
        user = User(
            name=name.strip(),
            email=email.strip(),
            password_hash="",
            roles=roles_str,
            is_active=True,
            street_number="", 
            postal_code="", 
            city="", 
        )

        db.session.add(user)
        db.session.commit()

        flash("Gebruiker aangemaakt!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("user_create.html", user_roles=["admin", "driver"])


# -------------------------------------------
# USER ACTIEF / INACTIEF ZETTEN
# -------------------------------------------
@admin_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
def toggle_user_active(user_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    if user.user_id == current_user.user_id:
        flash("Je kunt je eigen account niet deactiveren.", "error")
        return redirect(url_for("admin.dashboard"))

    user.is_active = not user.is_active
    db.session.commit()

    flash(f"Gebruiker {'geactiveerd' if user.is_active else 'gedeactiveerd'}!", "success")
    return redirect(url_for("admin.dashboard"))


# -------------------------------------------
# USER BEWERKEN
# -------------------------------------------
@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.name = request.form.get("name") or user.name
        user.email = request.form.get("email") or user.email

        selected_roles = request.form.getlist("roles")
        user.roles = ",".join(selected_roles) if selected_roles else ""

        user.is_active = ("is_active" in request.form)

        db.session.commit()
        flash("Gebruiker bijgewerkt!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("user_edit.html", user=user)


# -------------------------------------------
# USER VERWIJDEREN
# -------------------------------------------
@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    if not require_admin():
        return redirect(url_for("auth.login"))

    if current_user.user_id == user_id:
        flash("Je kunt je eigen account niet verwijderen.", "error")
        return redirect(url_for("admin.dashboard"))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash("Gebruiker verwijderd.", "success")
    return redirect(url_for("admin.dashboard"))

