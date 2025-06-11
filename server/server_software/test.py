import time
import random
import datetime
import paho.mqtt.client as mqtt

def print_time(msg):
    print(f"[{datetime.datetime.now()}] {msg}")

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
    client.subscribe("images/raw")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    image = msg.payload
    print_time("Immagine ricevuta")
    start_time = time.time()
    while start_time + 2 > time.time(): # simulazione di un tempo di elaborazione
        pass
    print_time("Immagine processata")

    labels = [b"red", b"green", b"blue", b"yellow"]

    chosen = random.sample(labels, random.randint(0, len(labels)))
    chosen_str = b";".join(chosen)

    data = bytearray(chosen_str)


    client.publish("results/labels", data)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe

mqttc.connect("127.0.0.1", 1883, 60)

start_time = time.time()

mqttc.loop_start()

while True:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        break

mqttc.loop_stop()
