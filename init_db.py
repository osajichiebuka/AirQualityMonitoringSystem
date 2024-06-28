from app import app, db
from app import SensorData  # Ensure the model is imported to create the table

# Initialize the database within the application context
with app.app_context():
    db.create_all()
    print("Database initialized successfully.")
