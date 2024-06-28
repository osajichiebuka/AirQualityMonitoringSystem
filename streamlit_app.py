import streamlit as st
import requests
from streamlit_echarts import st_echarts
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import pandas as pd
import re

# Define the URLs for data and devices
DATA_URL = "http://127.0.0.1:5000/data"
DEVICES_URL = "http://127.0.0.1:5000/devices"

# Function to fetch data from the URL
def fetch_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Parse response as JSON
        else:
            return {"error": f"Error fetching data. Status code: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching data: {e}"}

# Function to fetch the list of devices
def fetch_devices(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()  # Parse response as JSON
        else:
            return {"error": f"Error fetching devices. Status code: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching devices: {e}"}

# Function to get gauge chart options for AQI with a range of 0-500
def get_aqi_gauge_options(aqi):
    options = {
        "tooltip": {
            "formatter": '{a} <br/>{b}: {c} '
        },
        "series": [
            {
                "name": "Air Quality",
                "type": "gauge",
                "min": 0,
                "max": 500,
                "detail": {"formatter": "{value}"},
                "data": [{"value": aqi, "name": "AQI"}],
                "axisLine": {
                    "lineStyle": {
                        "width": 10,
                        "color": [
                            [50/500, '#58D68D'],  # green for values 0-50
                            [100/500, '#F4D03F'], # yellow for values 51-100
                            [150/500, '#E67E22'], # orange for values 101-150
                            [1, '#E74C3C']        # red for values above 150
                        ]
                    }
                },
                "pointer": {
                    "width": 5
                },
                "title": {
                    "fontWeight": 'bolder',
                    "fontSize": 20,
                },
                "detail": {
                    "formatter": '{value}',
                    "fontSize": 20,
                },
            }
        ]
    }
    return options

# Function to get gauge chart options for dust value with custom thresholds
def get_dust_gauge_options(dust):
    options = {
        "tooltip": {
            "formatter": '{a} <br/>{b}: {c} µg/m³'
        },
        "series": [
            {
                "name": "Dust Level",
                "type": "gauge",
                "detail": {"formatter": "{value} µg/m³"},
                "data": [{"value": dust, "name": "Dust"}],
                "axisLine": {
                    "lineStyle": {
                        "width": 10,
                        "color": [
                            [25/100, '#58D68D'],   # green up to 25 µg/m³
                            [75/100, '#F4D03F'],   # yellow up to 75 µg/m³
                            [1, '#E74C3C']         # red for values above 75 µg/m³
                        ]
                    }
                },
                "pointer": {
                    "width": 5
                },
                "title": {
                    "fontWeight": 'bolder',
                    "fontSize": 20,
                },
                "detail": {
                    "formatter": '{value} µg/m³',
                    "fontSize": 20,
                },
            }
        ]
    }
    return options

# Function to display data for a selected device
def display_device_data(device_id, device_data):
    aqi = device_data['corrected_gas']  # Use corrected_gas as AQI
    dust = device_data['dust']
    gas = device_data['gas']
    humidity = device_data['humidity']
    location = device_data['location']
    temperature = device_data['temperature']
    timestamp = device_data['timestamp']
    
    st.markdown(
        f"""
        <div class="card">
            <div class="elements">
                <h3>Device ID: {device_id}</h3>
                <h4>Location: {location}</h4>
                <hr>
                <ul>
                    <li>Air Quality Index (AQI): {aqi}</li>
                    <li>Dust: {dust} µg/m³</li>
                    <li>Gas: {gas} ppm</li>
                    <li>Humidity: {humidity} %</li>
                    <li>Temperature: {temperature} °C</li>
                    <li>Timestamp: {timestamp}</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display the gauge chart for the AQI
    st.subheader("Air Quality Index (AQI):")
    st_echarts(options=get_aqi_gauge_options(aqi), height="400px")
    
    # Display the gauge chart for the dust value with custom thresholds
    st.subheader("Dust Level: ")
    st_echarts(options=get_dust_gauge_options(dust), height="400px")

# Function to display the combined line chart for a device
def display_line_chart(device_data):
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(device_data)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Melt the DataFrame to have a long format for Plotly
    df_melted = df.melt(id_vars=['timestamp'], 
                        value_vars=['corrected_gas', 'dust', 'gas', 'humidity', 'temperature'],
                        var_name='Element',
                        value_name='Value')
    
    # Rename 'corrected_gas' to 'AQI' for the plot
    df_melted['Element'] = df_melted['Element'].replace({'corrected_gas': 'AQI'})
    
    # Create a line chart with Plotly
    fig = px.line(df_melted, x='timestamp', y='Value', color='Element', 
                  title='Combined Element Values Over Time',
                  labels={'timestamp': 'Timestamp', 'Value': 'Value', 'Element': 'Element'})
    
    # Show the line chart
    st.plotly_chart(fig, use_container_width=True)

# Main Streamlit app function
def main():
    # Automatically refresh the app every 10 minutes (600 seconds)
    st_autorefresh(interval=600 * 1000, key="data_refresh")
    
    st.title("Air Quality Monitoring System")
    
    # Use Streamlit session state to cache data
    if 'devices' not in st.session_state:
        st.session_state.devices = fetch_devices(DEVICES_URL)
        
    if 'last_fetched_data' not in st.session_state:
        st.session_state.last_fetched_data = {}

    devices = st.session_state.devices

    if "error" in devices:
        st.error(devices["error"])
        return
    
    if not devices:
        st.warning("No devices found.")
        return
    
    # Create a dictionary for easy lookup by device ID
    device_lookup = {device['device_id']: device for device in devices}
    
    # Display the list of devices in the sidebar
    device_ids = [device['device_id'] for device in devices]
    selected_device = st.sidebar.radio("Select a device:", device_ids)
    
    # Fetch data from the specified URL
    new_data = fetch_data(DATA_URL)
    
    if "error" in new_data:
        st.error(new_data["error"])
        data_to_display = st.session_state.last_fetched_data
    else:
        # If new data is fetched successfully, update the cache
        if not st.session_state.last_fetched_data or new_data != st.session_state.last_fetched_data:
            st.session_state.last_fetched_data = new_data
        data_to_display = st.session_state.last_fetched_data
    
    # Filter data for the selected device
    if data_to_display:
        sorted_data = sorted(data_to_display, key=lambda x: int(re.findall(r'\d+', x['device_id'])[0]))
        device_data = [entry for entry in sorted_data if entry['device_id'] == selected_device]
        
        if device_data:
            # Display device data
            display_device_data(selected_device, device_data[-1])  # Show the latest data entry
            
            # Display line chart
            st.subheader(f"Line Chart for Data Over Time - Device ID: {selected_device}")
            display_line_chart(device_data)
        else:
            st.warning(f"No data found for device ID: {selected_device}")

if __name__ == "__main__":
    main()
