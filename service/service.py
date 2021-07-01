from flask import (Blueprint, request, render_template)
from network import Bluetooth

flask_service = Blueprint('service-blueprint', __name__)

@flask_service.route("/calibration", methods=['GET'])
def calibration():
    bt = Bluetooth.BluetoothManagerMeter()
    return "ok"