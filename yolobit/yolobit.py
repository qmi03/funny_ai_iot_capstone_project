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

def update_temperature():
    aiot_dht20.read_dht20()
    mqtt.publish('bbc-temp', (aiot_dht20.dht20_temperature()))

if __name__ =="main":
    button_a.on_pressed = None
    button_b.on_pressed = None
    button_a.on_pressed_ab = button_b.on_pressed_ab = -1


    display.scroll('HI')
    count = 0

    aiot_dht20 = DHT20(SoftI2C(scl=Pin(22), sda=Pin(21)))

    mqtt.connect_wifi ('kiietuan', '0913414256')
    mqtt.connect_broker(server='io.adafruit.com', port=1883, username='tuankiet0303', password='aio_ATnv88akXoj47WX10OVkeI9iq5T6')
    mqtt.on_receive_message('bbc-led', on_receive_message_bcc_led)

    event_manager.reset()
    event_manager.add_timer_event(30000, update_temperature)

    while True:
        mqtt.check_message()
        event_manager.run()

