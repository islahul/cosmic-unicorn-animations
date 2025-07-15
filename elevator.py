import time
import machine
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY
from audio import WavPlayer

sound = WavPlayer(0, 10, 11, 9, amp_enable=22)
cosmic = CosmicUnicorn()
'''
Display scrolling wisdom, quotes or greetz.

You can adjust the brightness with LUX + and -.
'''


# returns the id of the button that is currently pressed or
# None if none are

# constants for controlling scrolling text
PADDING = 5
MESSAGE_COLOUR = (255, 0, 0)
OUTLINE_COLOUR = (200, 200, 200)
BACKGROUND_COLOUR = (0, 0, 0)
HOLD_TIME_S = 2.0
STEP_TIME = 0.05

# create cosmic object and graphics surface for drawing
cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)

# Basic settings
graphics.set_font("bitmap8")
cu.set_brightness(0.8)

width = CosmicUnicorn.WIDTH
height = CosmicUnicorn.HEIGHT

STATE_CURRENT_FLOOR = 0
STATE_TARGET_FLOOR = 5
STATE_DIRECTION = 0

def pressed():
    if cu.is_pressed(CosmicUnicorn.SWITCH_A):
        return CosmicUnicorn.SWITCH_A
    if cu.is_pressed(CosmicUnicorn.SWITCH_B):
        return CosmicUnicorn.SWITCH_B
    if cu.is_pressed(CosmicUnicorn.SWITCH_C):
        return CosmicUnicorn.SWITCH_C
    if cu.is_pressed(CosmicUnicorn.SWITCH_D):
        return CosmicUnicorn.SWITCH_D
    return None


def draw_text(text, x, y):
    graphics.set_pen(graphics.create_pen(int(MESSAGE_COLOUR[0]), int(MESSAGE_COLOUR[1]), int(MESSAGE_COLOUR[2])))
    graphics.text(text, x, y, wordwrap=-1, scale=2)



# state constants
# STATE_PRE_SCROLL = 0
# STATE_SCROLLING = 1
# STATE_POST_SCROLL = 2

# shift = 0
# state = STATE_PRE_SCROLL

# set the font

# calculate the message width so scrolling can happen
# msg_width = graphics.measure_text(MESSAGE, 1)

last_time = time.ticks_ms()

while True:
    # if A, B, C, or D are pressed then reset
    if pressed() is not None:
        machine.reset()
    time_ms = time.ticks_ms()

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        cu.adjust_brightness(+0.01)

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        cu.adjust_brightness(-0.01)
    
    if STATE_CURRENT_FLOOR < STATE_TARGET_FLOOR:
        STATE_DIRECTION = 1
    elif STATE_CURRENT_FLOOR > STATE_TARGET_FLOOR:
        STATE_DIRECTION_TEXT = -1
    else:
        STATE_DIRECTION=0

    if STATE_CURRENT_FLOOR < STATE_TARGET_FLOOR and time_ms - last_time > HOLD_TIME_S * 1000:
        STATE_CURRENT_FLOOR = STATE_CURRENT_FLOOR + 1
        if STATE_CURRENT_FLOOR == STATE_TARGET_FLOOR:
            sound.play_wav("doorbell.wav", False)
        else:
            sound.play_wav("buttonbeep.wav", False)
        last_time = time_ms

    graphics.set_pen(graphics.create_pen(int(BACKGROUND_COLOUR[0]), int(BACKGROUND_COLOUR[1]), int(BACKGROUND_COLOUR[2])))
    graphics.clear()
    graphics.set_pen(graphics.create_pen(int(OUTLINE_COLOUR[0]), int(OUTLINE_COLOUR[1]), int(OUTLINE_COLOUR[2])))

    graphics.line(0,0,31,0)
    graphics.line(31,0,31,32)
    graphics.line(31,31,0,31)
    graphics.line(0,31,0,0)
        
    if time_ms - last_time > STEP_TIME * 1000: 
        draw_text(f'{STATE_CURRENT_FLOOR}', x=5, y=10)

    if STATE_DIRECTION==1:
        graphics.set_pen(graphics.create_pen(int(MESSAGE_COLOUR[0]), int(MESSAGE_COLOUR[1]), int(MESSAGE_COLOUR[2])))
        graphics.triangle(22, 10, 16, 20, 28, 20)
    # draw_text(MESSAGE, x=PADDING - shift, y=2)

    # update the display
    cu.update(graphics)

    # pause for a moment (important or the USB serial device will fail)
    time.sleep(0.05)