import time
import random
import datetime
import subprocess
from typing import override
from utils import print_time
import paho.mqtt.client as mqtt
import cv2

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
        # Visualizza l'immagine ricevuta
        try:
            import numpy as np
            img_array = np.frombuffer(image, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is not None:
                cv2.imshow("Received Image", frame)
                cv2.waitKey(1)  # Show the image briefly, non-blocking
            else:
                print_time("Errore nella decodifica dell'immagine")
        except Exception as e:
            print_time(f"Errore nella visualizzazione dell'immagine: {e}")

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
                # Chiudi la finestra se l'utente preme 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except KeyboardInterrupt:
                break

        self.mqttc.loop_stop()
        cv2.destroyAllWindows()

class MQTTRPIClient(MQTTGenericClient):
    def __init__(self, broker, port, listens_to, write_to, username = None, password = None):
        super().__init__(broker, port, listens_to, username, password)
        self.mqttc.on_message = self.on_message

        self.mqttc.connect("127.0.0.1", 1883, 60)

        if self.__is_rpi():
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

        self.leds = [LED(4), LED(17), LED(27), LED(22)]


    def __is_rpi(self):
        proc = subprocess.run(["cat", "/proc/cpuinfo"], stdout=subprocess.PIPE)
        return "Raspberry" in proc.stdout.decode("utf-8")


    def on_message(self, client, userdata, msg):
        print_time(f"Received message: {msg.topic} {str(msg.payload)}")
        labels = msg.payload.decode("utf-8").split(";")

        for led in self.leds:
            led.off()

        for label in labels:

            match label:
                case "red":
                    self.leds[0].on()
                case "green":
                    self.leds[1].on()
                case "blue":
                    self.leds[2].on()
                case "yellow":
                    self.leds[3].on()
                case _:
                    print_time("Unknown label: " + label)

    def mainloop(self):
        cap = cv2.VideoCapture(0)
        
        start_time = time.time()

        self.mqttc.loop_start()

        while True:
            try:
                current_time = time.time()
                if current_time - start_time > 5:
                    print_time("Sending Camera Image")
                    
                    ret, frame = cap.read()
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        self.mqttc.publish("images/raw", buffer.tobytes())
                        print_time("Image sent")
                    else:
                        print_time("Failed to capture image")
                    
                    start_time = current_time
                else:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                break

        self.mqttc.loop_stop()
        cap.release()

