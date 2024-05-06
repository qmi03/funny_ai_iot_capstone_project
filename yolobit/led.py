from yolobit import *
button_a.on_pressed = None
button_b.on_pressed = None
button_a.on_pressed_ab = button_b.on_pressed_ab = -1

def turn_off_all():
    for i in range(5):
        for j in range (5):
            display.set_pixel(i, j, '#000000')

if True:
    turn_off_all()
    display.set_pixel(3, 2, '#ff0000')
    display.set_pixel(3, 3, '#ff0000')

while True:
    pass   
