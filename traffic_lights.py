import time
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY

# Setup display and device
cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)
graphics.set_font("bitmap6")
cu.set_brightness(0.6)

WIDTH = CosmicUnicorn.WIDTH
HEIGHT = CosmicUnicorn.HEIGHT

# Traffic light state
state = 0
last_switch = 0

# Durations in ms for each light
DURATIONS = [4000, 4000, 2000]  # Red, Green, Yellow

# Colors
RED = (255, 0, 0)
YELLOW = (255, 200, 0)
GREEN = (0, 255, 0)
GREY = (40, 40, 40)

# Layout for 32x32 LED matrix (fit all lights within bounds)
RADIUS = 4
LIGHT_SPACING = 2  # vertical space between lights
BODY_WIDTH = RADIUS * 2 + 5
BODY_HEIGHT = 3 * (RADIUS * 2) + 2 * LIGHT_SPACING + 4
LIGHT_X = WIDTH // 2
BODY_TOP = (HEIGHT - BODY_HEIGHT) // 2

# Compute y positions for each light (evenly spaced)
LIGHT_Y = [
    BODY_TOP + RADIUS + 2,  # Red (top)
    BODY_TOP + (BODY_HEIGHT // 2),  # Yellow (middle)
    BODY_TOP + BODY_HEIGHT - RADIUS - 2,  # Green (bottom)
]

def draw_traffic_light():
    global state, last_switch
    now = time.ticks_ms()
    # Switch state if needed
    if time.ticks_diff(now, last_switch) > DURATIONS[state]:
        state = (state + 1) % 3
        last_switch = now
    # Draw background
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()
    # Draw traffic light body (centered)
    graphics.set_pen(graphics.create_pen(60, 60, 60))
    graphics.rectangle(
        LIGHT_X - BODY_WIDTH // 2,
        BODY_TOP,
        BODY_WIDTH,
        BODY_HEIGHT,
    )
    # Draw lights
    for i, color in enumerate([RED, YELLOW, GREEN]):
        if state == i:
            pen = graphics.create_pen(*color)
        else:
            pen = graphics.create_pen(*GREY)
        graphics.set_pen(pen)
        graphics.circle(LIGHT_X, LIGHT_Y[i], RADIUS)
    cu.update(graphics)

def init():
    global state, last_switch
    state = 0
    last_switch = time.ticks_ms()
    graphics.set_font("bitmap6")
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()

def draw():
    draw_traffic_light()

def main():
    init()
    while True:
        draw()
        time.sleep(0.01)

if __name__ == "__main__":
    main()
