import json
import paho.mqtt.client as mqtt
import time

from ..firebase.firestoreService import updateLocation, createFall
from ..config import *

lastFall = {}

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

def start_mqtt():
    print("start_mqtt called")
    
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_forever()