import csv
import paho.mqtt.client as mqtt
import time
import json

TAG_ID = '0004fc92-c020-45ab-a958-3f442a8a207c'

# MQTT Broker settings
BROKER = '172.16.1.217'  # e.g., 'mqtt.eclipse.org'
PORT = 1883                       # Default MQTT port
TOPIC = f'aa/assets/{TAG_ID}/data/position'              # Replace with your MQTT topic
CSV_FILE = 'output.csv'           # Name of the CSV file to write to

# Callback when a message is received
def on_message(client, userdata, message):
    payload = message.payload.decode()  # Decode the byte payload
    print(f"Message received: {payload}")
    
    json_payload = json.loads(payload)
    timestamp = json_payload['timestamp']
    
    x = json_payload['position']['x']
    y = json_payload['position']['y']

    # Write the message to the CSV file
    with open(CSV_FILE, mode='a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([timestamp, x, y])
        
        

# Set up the MQTT client
client = mqtt.Client()

# Assign the message callback function
client.on_message = on_message

# Connect to the MQTT broker
client.connect(BROKER, PORT, keepalive=60)

# Subscribe to the topic
client.subscribe(TOPIC)

# Start the MQTT loop
client.loop_start()

try:
    print("Listening for messages...")
    while True:
        time.sleep(1)  # Keep the script running

except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.loop_stop()
    client.disconnect()
