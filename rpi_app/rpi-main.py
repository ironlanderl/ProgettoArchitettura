import os
from MQTT import MQTTRPIClient

def main():
    client = MQTTRPIClient(os.environ["MQTT_ENDPOINT"], int(os.environ["MQTT_PORT"]), "results/labels", "images/raw", os.environ["MQTT_USERNAME"], os.environ["MQTT_PASSWORD"])
    client.mainloop()


if __name__ == "__main__":
    main()
