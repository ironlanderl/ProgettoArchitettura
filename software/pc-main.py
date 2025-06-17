from MQTT import MQTTYOLOClient

def main():
    client = MQTTYOLOClient("127.0.0.1", 1883, "images/raw", "results/labels")
    client.mainloop()


if __name__ == "__main__":
    main()
