from app import app, db
from app import SensorData
from datetime import datetime
import random


def populate_db():
    with app.app_context():
        # Create the database and the database table
        db.create_all()

        # Clear existing data
        db.session.query(SensorData).delete()

        # Prepopulate the database with 30 entries
        for i in range(1, 31):
            device_id = f"device_{i}"
            location = f'location_{random.choice(["office", "lab", "room", "factory"])}'
            dust = round(random.uniform(10, 100), 2)
            gas = round(random.uniform(50, 300), 2)
            corrected_gas = round(random.uniform(30, 200), 2)
            temperature = round(random.uniform(20, 35), 2)
            humidity = round(random.uniform(30, 80), 2)
            timestamp = datetime.utcnow()

            new_entry = SensorData(
                device_id=device_id,
                location=location,
                dust=dust,
                gas=gas,
                corrected_gas=corrected_gas,
                temperature=temperature,
                humidity=humidity,
                timestamp=timestamp,
            )
            db.session.add(new_entry)

        # Commit the changes
        db.session.commit()
        print("Database populated with test data.")


if __name__ == "__main__":
    populate_db()
