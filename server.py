from dalybms import DalyBMS
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import threading
import os
import time

load_dotenv()
DELAY_SEC = os.getenv("DELAY_SEC", 5)
SAT_NAME = os.getenv("SAT_NAME", "Adrastea")
BROKER = os.getenv("BROKER", "localhost")
DEVICE_ADDR = os.getenv("DEVICE_ADDR", "/dev/ttyUSB0")
SYSTEM_NAME = os.getenv("SYSTEM_NAME", "Makai")

global_client = None
last_status = "ALIVE"

driver = DalyBMS()
driver.connect(device=DEVICE_ADDR)


# def on_connect(client, userdata, flags, rc):
# client.subscribe("Makai/battery/command")


# def on_message(client, userdata, msg):
#     # print(msg.payload.decode())


def mqtt_loop():
    global global_client

    client = mqtt.Client()
    # client.on_connect = on_connect
    # client.on_message = on_message

    client.connect(os.getenv("BROKER"), 1883, 60)

    global_client = client


def heartbeat_loop():
    while True:
        global_client.publish(f"{SYSTEM_NAME}/{SAT_NAME}/heartbeat", last_status)
        time.sleep(1)


mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()

while global_client is None:
    pass

heartbeat_loop = threading.Thread(target=heartbeat_loop)
heartbeat_loop.start()

while True:
    try:
        soc = driver.get_soc()
        temps = driver.get_temperatures()
        status = driver.get_mosfet_status()

        global_client.publish(f"{SYSTEM_NAME}/battery/soc", soc["soc_percent"])
        global_client.publish(f"{SYSTEM_NAME}/battery/current", soc["current"])
        global_client.publish(f"{SYSTEM_NAME}/battery/voltage", soc["total_voltage"])
        global_client.publish(f"{SYSTEM_NAME}/battery/temperature", temps[1])
        global_client.publish(f"{SYSTEM_NAME}/battery/mode", status["mode"])
        global_client.publish(f"{SYSTEM_NAME}/battery/capacity", status["capacity_ah"])
        global_client.publish(
            f"{SYSTEM_NAME}/battery/charging_locked", not status["charging_mosfet"]
        )
        global_client.publish(
            f"{SYSTEM_NAME}/battery/discharging_locked",
            not status["discharging_mosfet"],
        )

        last_status = "ALIVE"
    except Exception as e:
        last_status = "ERROR: " + str(e)
        print(e)

    time.sleep(5)
