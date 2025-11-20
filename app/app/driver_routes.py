from flask import Blueprint

driver_bp = Blueprint("driver", __name__)

@driver_bp.route("/driver/test")
def driver_test():
    return "Driver route werkt!"
