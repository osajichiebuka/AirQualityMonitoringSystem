from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sensor_data.db"
db = SQLAlchemy(app)


class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    dust = db.Column(db.Float, nullable=False)
    gas = db.Column(db.Float, nullable=False)
    corrected_gas = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json
    new_data = SensorData(
        device_id=data["device_id"],
        location=data["location"],
        dust=data["dust"],
        gas=data["gas"],
        corrected_gas=data["corrected_gas"],
        temperature=data["temperature"],
        humidity=data["humidity"],
    )
    db.session.add(new_data)
    db.session.commit()
    return jsonify({"message": "Data received"}), 200


@app.route("/data", methods=["GET"])
def get_all_data():
    data = SensorData.query.all()
    if not data:
        return jsonify({"message": "No data found"}), 404

    result = []
    for entry in data:
        result.append(
            {
                "device_id": entry.device_id,
                "location": entry.location,
                "dust": entry.dust,
                "gas": entry.gas,
                "corrected_gas": entry.corrected_gas,
                "temperature": entry.temperature,
                "humidity": entry.humidity,
                "timestamp": entry.timestamp,
            }
        )
    return jsonify(result), 200


@app.route("/data/<string:device_id>", methods=["GET"])
def get_data(device_id):
    data = SensorData.query.filter_by(device_id=device_id).all()
    if not data:
        return jsonify({"message": "No data found for the device"}), 404

    result = []
    for entry in data:
        result.append(
            {
                "dust": entry.dust,
                "gas": entry.gas,
                "corrected_gas": entry.corrected_gas,
                "temperature": entry.temperature,
                "humidity": entry.humidity,
                "timestamp": entry.timestamp,
            }
        )
    return jsonify(result), 200


@app.route("/analyze/<string:device_id>", methods=["GET"])
def analyze_data(device_id):
    data = SensorData.query.filter_by(device_id=device_id).all()
    if not data:
        return jsonify({"message": "No data found for the device"}), 404

    total_dust = total_gas = total_corrected_gas = total_temp = total_humidity = 0
    count = len(data)

    for entry in data:
        total_dust += entry.dust
        total_gas += entry.gas
        total_corrected_gas += entry.corrected_gas
        total_temp += entry.temperature
        total_humidity += entry.humidity

    avg_dust = total_dust / count
    avg_gas = total_gas / count
    avg_corrected_gas = total_corrected_gas / count
    avg_temp = total_temp / count
    avg_humidity = total_humidity / count

    recommendations = []
    if avg_gas > 100:
        recommendations.append("High gas levels detected. Ensure good ventilation.")
    if avg_temp > 30:
        recommendations.append("High temperature detected. Consider cooling solutions.")
    if avg_dust > 50:
        recommendations.append("High dust levels detected. Consider air purification.")

    analysis = {
        "average_dust": avg_dust,
        "average_gas": avg_gas,
        "average_corrected_gas": avg_corrected_gas,
        "average_temperature": avg_temp,
        "average_humidity": avg_humidity,
        "recommendations": recommendations,
    }

    return jsonify(analysis), 200


@app.route("/devices", methods=["GET"])
def get_devices():
    devices = (
        db.session.query(SensorData.device_id, db.func.max(SensorData.location))
        .group_by(SensorData.device_id)
        .all()
    )
    result = [{"device_id": device[0], "location": device[1]} for device in devices]
    return jsonify(result), 200
