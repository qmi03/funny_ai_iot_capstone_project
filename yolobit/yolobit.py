import music
import time
from machine        import Pin, SoftI2C
from aiot_dht20     import DHT20
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
    if message[1] == "ALL":
        if message[2] == "ON":
            for i in range(5):
                display.set_pixel(0, i, '#ff0000')
        elif message[2] == "OFF":
            for i in range(5):
                display.set_pixel(0, i, '#000000')
    else:
        if message[2] == "ON":
            display.set_pixel(0, int(message[1]), '#ff0000')
        elif message[2] == "OFF":
            display.set_pixel(0, int(message[1]), '#000000')

def on_receive_kitchen_led (message:str):
    message = message.strip().split()
    if message[1] == "ALL":
        if message[2] == "ON":
            for i in range(5):
                display.set_pixel(1, i, '#ff0000')
        elif message[2] == "OFF":
            for i in range(5):
                display.set_pixel(1, i, '#000000')
    else:
        if message[2] == "ON":
            display.set_pixel(1, int(message[1]), '#ff0000')
        elif message[2] == "OFF":
            display.set_pixel(1, int(message[1]), '#000000')
            
def on_receive_bedroom_led (message:str):
    message = message.strip().split()
    if message[1] == "ALL":
        if message[2] == "ON":
            for i in range(5):
                display.set_pixel(2, i, '#ff0000')
        elif message[2] == "OFF":
            for i in range(5):
                display.set_pixel(2, i, '#000000')
    else:
        if message[2] == "ON":
            display.set_pixel(2, int(message[1]), '#ff0000')
        elif message[2] == "OFF":
            display.set_pixel(2, int(message[1]), '#000000')

def update_temperature_humidity():
    aiot_dht20.read_dht20()
    temperature = aiot_dht20.dht20_temperature()
    if (float(temperature) >= 30):
        pin0.write_analog(round(translate(70, 0, 100, 0, 1023)))
    else:
        pin0.write_analog(round(translate(0, 0, 100, 0, 1023)))
    mqtt.publish('sensor-temperature', (aiot_dht20.dht20_temperature()))
    mqtt.publish('sensor-moisture', (aiot_dht20.dht20_humidity()))
    
button_a.on_pressed = None
button_b.on_pressed = None
button_a.on_pressed_ab = button_b.on_pressed_ab = -1


display.scroll('HI')
count = 0
aiot_dht20 = DHT20(SoftI2C(scl=Pin(22), sda=Pin(21)))
