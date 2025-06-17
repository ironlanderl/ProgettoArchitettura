import os
from MQTT import MQTTRPIClient

def main():
    client = MQTTRPIClient(os.environ["MQTT_ENDPOINT"], int(os.environ["MQTT_PORT"]), "images/raw", "results/labels")
    client.mainloop()


if __name__ == "__main__":
    main()
