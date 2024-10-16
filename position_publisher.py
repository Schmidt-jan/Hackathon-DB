from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import json

app = Flask(__name__)

# Initialize variables to store position
position_x = None
position_y = None

TAG_ID = '0004fc92-c020-45ab-a958-3f442a8a207c'

# MQTT settings
MQTT_BROKER = "172.16.1.217"  # Replace with your MQTT broker address
MQTT_PORT = 1883  # Default MQTT port
MQTT_TOPIC = f'aa/assets/{TAG_ID}/data/position'    # Replace with your topic

# Define MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global position_x, position_y
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)  # Assuming the payload is in JSON format
        position_x = data.get('position', {}).get('x')
        position_y = data.get('position', {}).get('y')
        print(f"Position updated: {position_x}, {position_y}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Start the MQTT client loop in a separate thread
def start_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

# Flask route to return position
@app.route('/position', methods=['GET'])
def get_position():
    if position_x is not None and position_y is not None:
        return jsonify({"position": [position_x, position_y]})
    else:
        return jsonify({"error": "Position not available"}), 404

if __name__ == '__main__':
    start_mqtt()  # Start MQTT in the background
    app.run(host='0.0.0.0', port=5000)  # Run Flask app
