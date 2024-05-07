import music
import time
from machine        import Pin, SoftI2C
# from aiot_dht20     import DHT20
from yolobit        import *
from mqtt           import *
from event_manager  import *

def on_receive_message_bcc_led(button):
    if button == '1':
        display.set_all('#ff0000')
    else:
        display.set_all('#000000')

def on_receive_livingroom_led (message:str):
    message = message.strip().split()
    if message[2] == "ON":
        display.set_pixel(0, int(message[1]), '#ff0000')
    elif message[2] == "OFF":
        display.set_pixel(0, int(message[1]), '#000000')

def on_receive_kitchen_led (message:str):
    message = message.strip().split()
    if message[2] == "ON":
        display.set_pixel(1, int(message[1]), '#ff0000')
    elif message[2] == "OFF":
        display.set_pixel(1, int(message[1]), '#000000')

def on_receive_bedroom_led (message:str):
    message = message.strip().split()
    if message[2] == "ON":
        display.set_pixel(2, int(message[1]), '#ff0000')
    elif message[2] == "OFF":
        display.set_pixel(2, int(message[1]), '#000000')

if __name__ =="main":
    button_a.on_pressed = None
    button_b.on_pressed = None
    button_a.on_pressed_ab = button_b.on_pressed_ab = -1


    display.scroll('HI')
    count = 0


    mqtt.connect_wifi ('kiietuan', '0913414256')
    mqtt.connect_broker(server='io.adafruit.com', port=1883, username='tuankiet0303', password='aio_faJu09BavEJu1an6bNeInk5tW648')
    # mqtt.on_receive_message('bbc-led', on_receive_message_bcc_led)
    mqtt.on_receive_message('led-slash-livingroom',on_receive_livingroom_led)
    mqtt.on_receive_message('led-slash-bedroom',on_receive_bedroom_led)
    mqtt.on_receive_message('led-slash-kitchen',on_receive_kitchen_led)

    event_manager.reset()

    while True:
        mqtt.check_message()
        event_manager.run()

