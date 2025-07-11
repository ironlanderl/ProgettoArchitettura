import os
from MQTT import MQTTYOLOClient

def main():
    client = MQTTYOLOClient(os.environ["MQTT_ENDPOINT"], int(os.environ["MQTT_PORT"]), "images/raw", "results/labels", "/yolomodel.pt", os.environ["MQTT_USERNAME"], os.environ["MQTT_PASSWORD"])
    client.mainloop()


if __name__ == "__main__":
    main()
