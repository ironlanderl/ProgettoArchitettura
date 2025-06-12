import os
import time
import signal
import datetime
import subprocess
import paho.mqtt.client as mqtt

signal.signal(signal.SIGINT, lambda x, y: exit(0))
signal.signal(signal.SIGTERM, lambda x, y: exit(0))


def print_time(msg):
    print(f"[{datetime.datetime.now()}] {msg}")

def is_rpi():
    proc = subprocess.run(["cat", "/proc/cpuinfo"], stdout=subprocess.PIPE)
    return "Raspberry" in proc.stdout.decode("utf-8")

# check if we are running on a raspberry pi
if is_rpi():
    from gpiozero import LED
    print_time("Running on Raspberry Pi")
else:
    print_time("Not running on Raspberry Pi. Using simulated LED")
    class LED:
        def __init__(self, pin):
            self.pin = pin

        def on(self):
            print(f"LED {self.pin} on")

        def off(self):
            print(f"LED {self.pin} off")

# RGBY
leds = [LED(4), LED(17), LED(27), LED(22)]

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print_time(f"Broker rejected your subscription: {reason_code_list[0]}")
    else:
        print_time(f"Broker granted the following QoS: {reason_code_list[0].value}")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print_time(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("results/labels")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print_time(f"Received message: {msg.topic} {str(msg.payload)}")
    labels = msg.payload.decode("utf-8").split(";")

    for led in leds:
        led.off()

    for label in labels:

        match label:
            case "red":
                leds[0].on()
            case "green":
                leds[1].on()
            case "blue":
                leds[2].on()
            case "yellow":
                leds[3].on()
            case _:
                print_time("Unknown label: " + label)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe

mqttc.connect(os.environ["endpoint"], 1883, 60)

start_time = time.time()

mqttc.loop_start()

while True:
    try:
        current_time = time.time()
        if current_time - start_time > 5:
            print_time("Sending Camera Image")
            mqttc.publish("images/raw", b"\x01\x02\x03\x04")
            start_time = current_time
        else:
            time.sleep(0.1)
    except KeyboardInterrupt:
        break

mqttc.loop_stop()
