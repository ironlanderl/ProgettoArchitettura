import time
import random
import datetime
import subprocess
from typing import override
from utils import print_time
import paho.mqtt.client as mqtt
import cv2
import numpy as np

class MQTTGenericClient:
    def __init__(self, broker, port, listens_to, username = None, password = None):
        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_message = self.on_message

        self.listens_to = listens_to
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password

        if self.username and self.password:
            self.mqttc.username_pw_set(self.username, self.password)

        self.mqttc.connect(self.broker, self.port, 60)

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        if reason_code_list[0].is_failure:
            print_time(f"Broker rejected your subscription: {reason_code_list[0]}")
        else:
            print_time(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print_time(f"Connected with result code {reason_code}")
        client.subscribe(self.listens_to)

    def on_message(self, client, userdata, msg):
        print_time(f"Received unhandled message on topic: {msg.topic}")

    def start_loop(self):
        self.mqttc.loop_start()

    def stop_loop(self):
        self.mqttc.loop_stop()

class MQTTYOLOClient(MQTTGenericClient):
    def __init__(self, broker, port, listens_to, write_to, username = None, password = None):
        super().__init__(broker, port, listens_to, username, password)
        print_time("Starting YOLO client")
        from YOLO import YOLO
        self.write_to = write_to
        self.current_frame = None
        self.yolo = YOLO("yolo11n.pt")
        print_time("YOLO model loaded")

    @override
    def on_message(self, client, userdata, msg):
        image_data = msg.payload
        print_time("Immagine ricevuta")
        try:
            img_array = np.frombuffer(image_data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is not None:
                current_frame = frame
            else:
                print_time("Errore nella decodifica dell'immagine")
                current_frame = None
        except Exception as e:
            print_time(f"Errore nella decodifica dell'immagine: {e}")

        
        prediction = self.yolo.predict_on_cv2_image(current_frame)
        self.current_frame = self.yolo.overlay_detections(current_frame, prediction)
        print_time(f"Rilevati {len(prediction)} oggetti")

        labels = [obj['label'].encode() for obj in prediction]
        labels_str = b";".join(labels)
        print_time(f"Invio etichette: {labels_str.decode('utf-8')}")

        data = bytearray(labels_str)

        client.publish(self.write_to, data)

    def mainloop(self):
        self.start_loop()
        cv2.namedWindow("Received Image")

        while True:
            try:
                if self.current_frame is not None:
                    cv2.imshow("Received Image", self.current_frame)

                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
            except KeyboardInterrupt:
                break

        self.stop_loop()
        cv2.destroyAllWindows()

class MQTTRPIClient(MQTTGenericClient):
    def __init__(self, broker, port, listens_to, write_to, username = None, password = None):
        super().__init__(broker, port, listens_to, username, password)
        self.write_to = write_to

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

    @override
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
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # cap.set( cv2.CAP_PROP_FPS, 2 )
        
        start_time = time.time()

        self.start_loop()

        while True:
            try:
                current_time = time.time()
                if current_time - start_time > 5:
                    print_time("Sending Camera Image")

                    # Questo, insieme a `cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)`, serve a evitare di avere immagini vecchie nel buffer
                    # e a garantire che l'immagine inviata sia quella più recente.
                    for i in range(1):
                        _, _ = cap.read()
                    
                    ret, frame = cap.read()
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        self.mqttc.publish(self.write_to, buffer.tobytes())
                        print_time("Image sent")
                    else:
                        print_time("Failed to capture image")
                    
                    start_time = current_time
                else:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                break

        self.stop_loop()
        cap.release()