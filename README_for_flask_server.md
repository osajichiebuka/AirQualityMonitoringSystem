# Flask Sensor Data Application

This is a Flask application that collects sensor data and provides endpoints to retrieve, analyze, and manage the data. The application can be run locally or in a Docker container.

## Prerequisites

- Docker
- Docker Compose (optional, but recommended for managing multi-container applications)

## Setup

### Running Locally

1. **Clone the repository:**

    ```sh
    git clone <repository-url>
    cd project
    ```

2. **Create and activate a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Initialize the database:**

    ```sh
    python init_db.py
    ```

5. **Populate the database with test data:**

    ```sh
    python test_populate.py
    ```

6. **Run the Flask application:**

    ```sh
    python run.py
    ```

    The application should now be running on `http://127.0.0.1:5000`.

### Running with Docker

1. **Clone the repository:**

    ```sh
    git clone <repository-url>
    cd project
    ```

2. **Build the Docker image:**

    ```sh
    docker build -t flask-sensor-app .
    ```

3. **Run the Docker container:**

    ```sh
    docker run -p 5000:5000 flask-sensor-app
    ```

    The application should now be running on `http://localhost:5000`.

4. **Initialize and populate the database with test data:**

    To initialize and populate the database with test data in Docker, follow these steps:

    1. **Run the container in interactive mode:**

        ```sh
        docker run -it --entrypoint /bin/sh flask-sensor-app
        ```

    2. **Inside the container, initialize the database:**

        ```sh
        python init_db.py
        ```

    3. **Populate the database with test data:**

        ```sh
        python test_populate.py
        ```

    4. **Exit the container:**

        ```sh
        exit
        ```

5. **Run the Docker container normally:**

    ```sh
    docker run -p 5000:5000 flask-sensor-app
    ```

## Endpoints

- **POST /data**: Send data to the server.
    ```sh
    curl -X POST http://127.0.0.1:5000/data -H "Content-Type: application/json" -d '{"device_id": "device1", "location": "office", "dust": 12.3, "gas": 45.6, "corrected_gas": 78.9, "temperature": 23.4, "humidity": 56.7}'
    ```

- **GET /data**: Retrieve all data.
    ```sh
    curl http://127.0.0.1:5000/data
    ```

- **GET /data/<device_id>**: Retrieve data for a specific device.
    ```sh
    curl http://127.0.0.1:5000/data/device1
    ```

- **GET /analyze/<device_id>**: Analyze data for a specific device.
    ```sh
    curl http://127.0.0.1:5000/analyze/device1
    ```

- **GET /devices**: Retrieve all device IDs and their locations.
    ```sh
    curl http://127.0.0.1:5000/devices
    ```

## License

This project is licensed under the MIT License.
