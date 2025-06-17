import os
from MQTT import MQTTYOLOClient

def main():
    client = MQTTYOLOClient(os.environ["MQTT_ENDPOINT"], int(os.environ["MQTT_PORT"]), "images/raw", "results/labels")
    client.mainloop()


if __name__ == "__main__":
    main()
