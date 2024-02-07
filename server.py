from dalybms import DalyBMS
import paho.mqtt.client as mqtt
import threading
import os
import time

DELAY_SEC = os.getenv("DELAY_SEC", 5)
BROKER = os.getenv("BROKER", "localhost")
DEVICE_ADDR = os.getenv("DEVICE_ADDR", "/dev/ttyUSB0")
PUBLISH_TOPIC = os.getenv("PUBLISH_TOPIC", "dev/battery")
HEARTBEAT_TOPIC = os.getenv("HEARTBEAT_TOPIC", "sat/battery")

global_client = None
last_status = "ALIVE"


def mqtt_loop():
    global global_client

    client = mqtt.Client()

    while True:
        try:
            client.connect(os.getenv("BROKER"), 1883, 60)
            break
        except:
            time.sleep(5)

    global_client = client


def heartbeat_loop():
    while True:
        global_client.publish(HEARTBEAT_TOPIC, last_status)
        time.sleep(1)


mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()

while global_client is None:
    pass

heartbeat_loop = threading.Thread(target=heartbeat_loop)
heartbeat_loop.start()


def read_and_publish():
    global last_status

    try:
        soc = driver.get_soc()
        temps = driver.get_temperatures()
        status = driver.get_mosfet_status()

        global_client.publish(f"{PUBLISH_TOPIC}/soc", soc["soc_percent"])
        global_client.publish(f"{PUBLISH_TOPIC}/current", soc["current"])
        global_client.publish(f"{PUBLISH_TOPIC}/voltage", soc["total_voltage"])
        global_client.publish(f"{PUBLISH_TOPIC}/temperature", temps[1])
        global_client.publish(f"{PUBLISH_TOPIC}/mode", status["mode"])
        global_client.publish(f"{PUBLISH_TOPIC}/capacity", status["capacity_ah"])
        global_client.publish(
            f"{PUBLISH_TOPIC}/charging_locked", not status["charging_mosfet"]
        )
        global_client.publish(
            f"{PUBLISH_TOPIC}/discharging_locked",
            not status["discharging_mosfet"],
        )

        last_status = "ALIVE"
    except Exception as e:
        print("Error during read", e)
        last_status = "ERROR"


while True:
    try:
        driver = DalyBMS()
        driver.connect(device=DEVICE_ADDR)

        while True:
            read_and_publish()
            time.sleep(DELAY_SEC)

    except Exception as e:
        print("Error during connect", e)
        time.sleep(5)
