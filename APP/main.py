import os
import threading
from fastapi import FastAPI

from .api.routes import router

app = FastAPI()
app.include_router(router)

if os.getenv("RENDER") != "true":
    # import mqtt client lazily to avoid import-time package issues
    from .mqtt.mqttClient import start_mqtt

    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()