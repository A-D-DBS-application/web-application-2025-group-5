# app/models.py
from datetime import datetime
from . import db
from sqlalchemy.orm import relationship


# -----------------------------------------------------
# USERS
# -----------------------------------------------------
class Users(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text)
    name = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    street_number = db.Column(db.Text, nullable=False)
    postal_code = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    created_routes = relationship("Route", foreign_keys="Route.created_by_user_id")
    driven_routes = relationship("Route", foreign_keys="Route.driver_id")

    def __repr__(self):
        return f"<User {self.name}>"


# -----------------------------------------------------
# VEHICLE
# -----------------------------------------------------
class Vehicle(db.Model):
    __tablename__ = "vehicle"

    vehicle_id = db.Column(db.BigInteger, primary_key=True)
    license_plate = db.Column(db.String(20), nullable=False, unique=True)
    brand = db.Column(db.Text, nullable=False)
    model = db.Column(db.Text)
    color = db.Column(db.Text)
    capacity_kg = db.Column(db.Numeric(10, 0))
    fuel_type = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    routes = relationship("Route", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle {self.license_plate}>"


# -----------------------------------------------------
# CUSTOMER
# -----------------------------------------------------
class Customer(db.Model):
    __tablename__ = "customer"

    customer_id = db.Column(db.BigInteger, primary_key=True)
    customer = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    street_number = db.Column(db.Text, nullable=False)
    postal_code = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    celphone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f"<Customer {self.customer}>"


# -----------------------------------------------------
# PRODUCT
# -----------------------------------------------------
class Product(db.Model):
    __tablename__ = "product"

    product_id = db.Column(db.BigInteger, primary_key=True)
    weight_kg = db.Column(db.Numeric(10, 0))
    product_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product {self.product_name}>"


# -----------------------------------------------------
# PURCHASE ORDERS
# -----------------------------------------------------
class PurchaseOrders(db.Model):
    __tablename__ = "purchase_orders"
    delivery_hour_start = db.Column(db.Time, nullable=True)
    delivery_hour_end = db.Column(db.Time, nullable=True)
    order_id = db.Column(db.BigInteger, primary_key=True)
    payment_status = db.Column(db.Text, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.customer_id"), nullable=False)
    delivery_phone = db.Column(db.String(20), nullable=False)
    delivery_window_start = db.Column(db.DateTime, nullable=False)
    delivery_window_end = db.Column(db.DateTime, nullable=False)
    total_weight_kg = db.Column(db.Numeric(10, 0), nullable=False)
    qty_fles= db.Column(db.Integer)
    qty_vat = db.Column(db.Integer)
    qty_bib = db.Column(db.Integer)
    order_status = db.Column(db.Text, nullable=False)
    qty_vat = db.Column( db.Integer,nullable=False, default=0)
    qty_fles = db.Column(db.Integer, nullable=False, default=0)
    qty_bib = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    # ✔ jouw originele relatie (GEEN back_populates!)
    customer = relationship("Customer")

    items = relationship("OrderItem", back_populates="order")
    route_links = relationship("RouteDelivery", back_populates="order")

    def __repr__(self):
        return f"<PurchaseOrder {self.order_id}>"


# -----------------------------------------------------
# ORDER ITEM
# -----------------------------------------------------
class OrderItem(db.Model):
    __tablename__ = "order_item"

    order_item_id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey("purchase_orders.order_id"), nullable=False)
    product_id = db.Column(db.BigInteger, db.ForeignKey("product.product_id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    order = relationship("PurchaseOrders", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem {self.order_item_id}>"


# -----------------------------------------------------
# ROUTE
# -----------------------------------------------------
class Route(db.Model):
    __tablename__ = "route"

    route_id = db.Column(db.BigInteger, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    vehicle_id = db.Column(db.BigInteger, db.ForeignKey("vehicle.vehicle_id"), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    route_date = db.Column(db.Date, nullable=False)
    route_status = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    driver_day_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    driver = relationship("Users", foreign_keys=[driver_id], back_populates="driven_routes")
    created_by = relationship("Users", foreign_keys=[created_by_user_id], back_populates="created_routes")
    vehicle = relationship("Vehicle", back_populates="routes")
    deliveries = relationship("RouteDelivery", back_populates="route")

    def __repr__(self):
        return f"<Route {self.route_id}>"


# -----------------------------------------------------
# ROUTE DELIVERY
# -----------------------------------------------------
class RouteDelivery(db.Model):
    __tablename__ = "route_delivery"

    route_delivery_id = db.Column(db.BigInteger, primary_key=True)
    route_id = db.Column(db.BigInteger, db.ForeignKey("route.route_id"), nullable=False)
    order_id = db.Column(db.BigInteger, db.ForeignKey("purchase_orders.order_id"), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    delivery_status = db.Column(db.Text)
    delivery_at = db.Column(db.DateTime)
    delivery_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    route = relationship("Route", back_populates="deliveries")
    order = relationship("PurchaseOrders", back_populates="route_links")

    def __repr__(self):
        return f"<RouteDelivery {self.route_delivery_id}>"


# Backwards compatibility alias
User = Users
Purchase_orders = PurchaseOrders
Route_Delivery = RouteDelivery
