import time
import machine
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY
from audio import WavPlayer
import pressed_button

# Constants for colors and timing
MESSAGE_COLOUR = (255, 0, 0)
OUTLINE_COLOUR = (200, 200, 200)
BACKGROUND_COLOUR = (0, 0, 0)
HOLD_TIME_S = 2.0
STEP_TIME = 0.05

# Initialize objects
cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)
sound = WavPlayer(0, 10, 11, 9, amp_enable=22)

# Set initial settings
graphics.set_font("bitmap8")
cu.set_brightness(0.8)

# Elevator states
current_floor = 0
target_floor = 5
direction = 0

def draw_text(text, x, y):
    graphics.set_pen(graphics.create_pen(*MESSAGE_COLOUR))
    graphics.text(text, x, y, wordwrap=-1, scale=2)

def draw_outline():
    graphics.set_pen(graphics.create_pen(*OUTLINE_COLOUR))
    graphics.rectangle(0, 0, 32, 32)  # Draw the outline with a single command

def update_floor_display():
    graphics.set_pen(graphics.create_pen(*BACKGROUND_COLOUR))
    graphics.clear()
    draw_outline()
    draw_text(f'{current_floor}', x=5, y=10)
    
    if direction == 1:
        graphics.set_pen(graphics.create_pen(*MESSAGE_COLOUR))
        graphics.triangle(22, 10, 16, 20, 28, 20)

    cu.update(graphics)

last_time = time.ticks_ms()

while True:
    if pressed_button(cu):
        machine.reset()

    time_ms = time.ticks_ms()

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        cu.adjust_brightness(+0.01)

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        cu.adjust_brightness(-0.01)
    
    if current_floor < target_floor:
        direction = 1
    elif current_floor > target_floor:
        direction = -1
    else:
        direction = 0

    if current_floor != target_floor and time_ms - last_time > HOLD_TIME_S * 1000:
        current_floor += 1 if direction == 1 else -1
        sound.play_wav("doorbell.wav" if current_floor == target_floor else "buttonbeep.wav", False)
        last_time = time_ms

    if time_ms - last_time > STEP_TIME * 1000: 
        update_floor_display()

    time.sleep(0.05)