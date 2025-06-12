import time
import random
import datetime
import paho.mqtt.client as mqtt
from utils import print_time

class MQTTGenericClient:
    def __init__(self, broker, port, listens_to, username = None, password = None):
        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_subscribe = self.on_subscribe

        self.listens_to = listens_to

        self.mqttc.connect("127.0.0.1", 1883, 60)

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        # Since we subscribed only for a single channel, reason_code_list contains
        # a single entry
        if reason_code_list[0].is_failure:
            print_time(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print_time(f"Broker granted the following QoS: {reason_code_list[0].value}")

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, reason_code, properties):
        print_time(f"Connected with result code {reason_code}")
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(self.listens_to)

class MQTTYOLOClient(MQTTGenericClient):
    def __init__(self, broker, port, listens_to, write_to, username = None, password = None):
        super().__init__(broker, port, listens_to, username, password)
        self.mqttc.on_message = self.on_message

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
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

    def mainloop(self):
        self.mqttc.loop_start()

        while True:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                break

        self.mqttc.loop_stop()


