from flask import Blueprint, render_template, request, redirect, session
from .models import Route, User, Vehicle
from . import db

admin_bp = Blueprint("admin", __name__)
@admin_bp.route('/admin/dashboard')
def dashboard():
    routes = Route.query.all()
    drivers = User.query.filter_by(role='driver').all()
    vehicles = Vehicle.query.all()
    return render_template(
        "admin_dashboard.html", routes=routes, drivers=drivers, vehicles=vehicles
    )

@admin_bp.route('/admin/routes/new', methods=['GET', 'POST'])
def create_route():
    if request.method == 'POST':
        driver = request.form['driver_id']
        vehicle = request.form['vehicle_id']
        date = request.form['route_date']

        route = Route(
            driver_id=driver,
            vehicle_id=vehicle,
            created_by_user_id=session["user_id"],
            route_date=date,
            route_status="planned"
        )

        db.session.add(route)
        db.session.commit()

        return redirect('/admin/dashboard')

    drivers = User.query.filter_by(role='driver').all()
    vehicles = Vehicle.query.all()

    return render_template("route_create.html", drivers=drivers, vehicles=vehicles)
