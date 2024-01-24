from dalybms import DalyBMS
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import threading
import os
import time

load_dotenv()
global_client = None


driver = DalyBMS()
driver.connect(device=os.getenv("DEVICE_ADDR"))

# get_soc {'total_voltage': 13.2, 'current': 2.7, 'soc_percent': 75.9}
# get_status {'cells': 4, 'temperature_sensors': 1, 'charger_running': False, 'load_running': False, 'states': {'DI1': False, 'DI2': True}, 'cycles': 127}


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # client.subscribe("Makai/battery/command")


# def on_message(client, userdata, msg):
#     # print(msg.payload.decode())


def mqtt_loop():
    global global_client

    client = mqtt.Client()
    client.on_connect = on_connect
    # client.on_message = on_message

    client.connect(os.getenv("BROKER"), 1883, 60)

    global_client = client
    # client.loop_forever()


mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.start()

while global_client is None:
    pass

while True:
    soc = driver.get_soc()

    global_client.publish("Makai/battery/soc", soc["soc_percent"])
    global_client.publish("Makai/battery/current", soc["current"])
    global_client.publish("Makai/battery/voltage", soc["total_voltage"])

    time.sleep(5)
