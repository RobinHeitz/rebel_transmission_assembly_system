import paho.mqtt.client as mqtt
from threading import Thread
import time

# CODE SNIPPET für den MQTT-Server der Seite Tingg.io
# Ist nicht vollständig bzw. die Datenbeschaffung funktioniert so nicht.



THING_ID = "4baea65e-9c1f-4791-bc5f-9f781d808f7c"
THING_KEY = "mb53pdj8nf768jxonvf1tx27i527abbw"


def publish_env_data(msg, client:mqtt.Client):
    voltage, temp_motor, temp_board, _ = msg()
    client.publish("voltage", voltage)
    client.publish("temp_motor", temp_motor)
    client.publish("temp_board", temp_board)

def publish_motor_stats(msg, client:mqtt.Client):
    current, position, tics,  _ = msg()
    client.publish("current", current)
    client.publish("position", position)
    


def publish_env_data_thread(c, client:mqtt.Client):
    while True:
        try:
            ...
            env_msg = c.motor_env_status_list.pop()
            publish_env_data(env_msg, client)
            time.sleep(2)
        
        except IndexError:
            ...

def publish_movement_reply_data_thread(c, client:mqtt.Client):
    while True:
        try:
            ...
            env_msg = c.movement_cmd_reply_list.pop()
            publish_motor_stats(env_msg, client)
            time.sleep(1)
        
        except IndexError:
            ...
    


if __name__ == "__main__":
  
    c = None

    client = mqtt.Client(THING_ID)
    client.username_pw_set("thing", THING_KEY)
    client.connect("mqtt.tingg.io") 
    Thread(target=publish_env_data_thread, args=(c, client), daemon=True).start()
    Thread(target=publish_movement_reply_data_thread, args=(c, client), daemon=True).start()
