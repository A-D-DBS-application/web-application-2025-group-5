from . import db
from sqlalchemy.orm import relationship
from datetime import datetime


class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # relationships
    created_routes = relationship("Route", foreign_keys="Route.created_by_user_id")
    driven_routes = relationship("Route", foreign_keys="Route.driver_id")

    def __repr__(self):
        return f"<User {self.name}>"


class Vehicle(db.Model):
    __tablename__ = "vehicle"

    vehicle_id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), nullable=False)
    brand = db.Column(db.Text, nullable=False)
    model = db.Column(db.Text)
    capacity_kg = db.Column(db.Numeric)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    routes = relationship("Route", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle {self.license_plate}>"


class Customer(db.Model):
    __tablename__ = "customer"

    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    adress = db.Column(db.Text, nullable=False)   # Let op: DDL heeft 'adress'
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    orders = relationship("PurchaseOrders", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.name}>"


class Product(db.Model):
    __tablename__ = "product"

    product_id = db.Column(db.Integer, primary_key=True)
    available_qty = db.Column(db.Integer)
    product_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product {self.product_name}>"


class PurchaseOrders(db.Model):
    __tablename__ = "Purchase_orders"

    order_id = db.Column(db.Integer, primary_key=True)
    payment_status = db.Column(db.Text, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.customer_id"), nullable=False)
    delivery_phone = db.Column(db.String(20), nullable=False)
    delivery_window_start = db.Column(db.DateTime, nullable=False)
    delivery_window_end = db.Column(db.DateTime, nullable=False)
    total_weight_kg = db.Column(db.Numeric, nullable=False)
    order_status = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    route_links = relationship("RouteDelivery", back_populates="order")

    def __repr__(self):
        return f"<PurchaseOrder {self.order_id}>"


class OrderItem(db.Model):
    __tablename__ = "order_item"

    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("Purchase_orders.order_id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.product_id"), nullable=False)
    quantity = db.Column(db.Integer)
    price_per_unit = db.Column(db.Numeric)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    order = relationship("PurchaseOrders", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem {self.order_item_id}>"


class Route(db.Model):
    __tablename__ = "Route"

    route_id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicle.vehicle_id"), nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    route_date = db.Column(db.Date, nullable=False)
    route_status = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    driver_day_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    driver = relationship("User", foreign_keys=[driver_id], back_populates="driven_routes")
    created_by = relationship("User", foreign_keys=[created_by_user_id], back_populates="created_routes")
    vehicle = relationship("Vehicle", back_populates="routes")
    deliveries = relationship("RouteDelivery", back_populates="route")

    def __repr__(self):
        return f"<Route {self.route_id}>"


class RouteDelivery(db.Model):
    __tablename__ = "route_delivery"

    route_delivery_id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("Route.route_id"), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("Purchase_orders.order_id"), nullable=False)
    stop_sequence = db.Column(db.Integer, nullable=False)
    delivery_status = db.Column(db.Text)
    delivery_at = db.Column(db.DateTime)
    delivery_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    route = relationship("Route", back_populates="deliveries")
    order = relationship("PurchaseOrders", back_populates="route_links")

    def __repr__(self):
        return f"<RouteDelivery {self.route_delivery_id}>"
