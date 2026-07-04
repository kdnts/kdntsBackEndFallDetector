import json
import paho.mqtt.client as mqtt
import time

from APP.firebase.firestoreService import updateLocation, createFall
from APP.config import *

lastFall = {}

mqtt_client = None

def on_connect(client, userdata, flags, rc, properties = None):
    print("MQTT connect")

    client.subscribe(TOPIC_FALL)
    client.subscribe(TOPIC_GPS)

    print("subscribed")

def on_message(client, userdata, msg):    
    payload = msg.payload.decode()

    try:
        data = json.loads(payload)

    except json.JSONDecodeError:
        print("invalid json")
        return

    deviceId = data.get("deviceId")
    msgType = data.get("type")

    if not deviceId:
        print("missing device")
        return

    if not msgType:
        print("missing type")
        return
    
    print(f"Device: {deviceId}")
    print(f"Type: {msgType}")

    if msgType == "gps":
        lat = data.get("lat")
        lng = data.get("lng")

        if lat is None:
            print("missing lat")
            return

        if lng is None:
            print("missing lng")
            return

        print("\nCalling updateLocation")
        updateLocation(deviceId, lat, lng)


    elif msgType == "fall":

        now = time.time()

        last = lastFall.get(deviceId, 0)

        if now - last <60:
            print("fall cooldown")
            return
        
        lastFall[deviceId] = now

        lat = data.get("lat")
        lng = data.get("lng")

        if lat is None:
            print("missing lat")
            return

        if lng is None:
            print("missing lng")
            return
        
        if not (-90<= lat <=90):
            print("invalid lat")
            return

        if not (-180<= lng <=180):
            print("invalid lng")
            return

        print("\nCalling createFall")
        createFall(deviceId, lat, lng)

def publishContact(deviceId, phones):
        global mqtt_client

        if mqtt_client is None:
            print("MQTT client not init")
            return False
        
        if not mqtt_client.is_connected():
            print("MQTT not connected")
            return False
        
        topic = f"devices/{deviceId}/contact"

        payload = {
            "phones": phones
        }

        try:
            mqtt_client.publish(
                topic,
                json.dumps(payload),
                qos=0,
                retain=False
            )

            print(f"[MQTT] Published contacts to {topic}")
            return True

        except Exception as e:
            print("[MQTT] publishContacts error:", e)
            return False

def start_mqtt():

    global mqtt_client

    print("start_mqtt called")
    
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

    mqtt_client.loop_forever()