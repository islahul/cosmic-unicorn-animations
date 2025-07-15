import time
import machine
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY
import math
import random

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
BLUE_SKY_COLOR = (5,6,25)
BACKGROUND_COLOUR = (0, 0, 0)
HOLD_TIME_S = 2.0
STEP_TIME = 0.05

# create cosmic object and graphics surface for drawing
cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)

# Basic settings
graphics.set_font("bitmap4")
cu.set_brightness(0.8)

width = CosmicUnicorn.WIDTH
height = CosmicUnicorn.HEIGHT

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

# Create class responsible for displaying a pixel star with surrounding pixels responsible for twinkling effect
# with center white but up and side pixels with lower intensity
class Star:
    def __init__(self, x, y, twinkle_frequency=1):
        self.x = x
        self.y = y
        self.start_time = time.ticks_ms()
        # Vertical or horizontal twinkle direction
        self.twinkle_direction = -1
        # twinkle frequency in seconds
        self.twinkle_frequency = twinkle_frequency
        # Gap in animation
        self.pausing_time = twinkle_frequency/10
        

    def draw(self):
        if (time.ticks_ms() - self.start_time) < self.pausing_time * 1000:
            return
        # calculate twinkle effect
        twinkle_time = time.ticks_ms() - self.start_time
        twinkle_intensity = 0.1 + 0.1 * math.sin(twinkle_time * 2 * math.pi / (self.twinkle_frequency * 1000))
        twinkle_intensity = max(0, min(0.2, twinkle_intensity))        
        # Draw the center pixel
        graphics.set_pen(graphics.create_pen(255, 255, 255))
        graphics.pixel(self.x, self.y)
        # Draw the surrounding pixels with lower intensity
        graphics.set_pen(graphics.create_pen(int(10), int(10), int(10)))
        graphics.pixel(self.x+1, self.y - 1)
        graphics.pixel(self.x+1, self.y + 1)
        graphics.pixel(self.x - 1, self.y-1)
        graphics.pixel(self.x - 1, self.y+1)
        # Draw the surrounding pixels based on twinkle direction
        graphics.set_pen(graphics.create_pen(int(255*0.1), int(255*0.1), int(255*0.1)))
        graphics.pixel(self.x, self.y - 1)
        graphics.pixel(self.x, self.y + 1)
        graphics.pixel(self.x - 1, self.y)
        graphics.pixel(self.x + 1, self.y)
        if self.twinkle_direction == 1:
            graphics.set_pen(graphics.create_pen(int(255 * twinkle_intensity), int(255 * twinkle_intensity), int(255 * twinkle_intensity)))
            graphics.pixel(self.x, self.y - 1)
            graphics.pixel(self.x, self.y + 1)
        else:
            graphics.set_pen(graphics.create_pen(int(255 * twinkle_intensity), int(255 * twinkle_intensity), int(255 * twinkle_intensity)))
            graphics.pixel(self.x - 1, self.y)
            graphics.pixel(self.x + 1, self.y)
        # Switch twinkle direction when twinkle frequency is reached
        if twinkle_time >= self.twinkle_frequency * 1000:
            self.start_time = time.ticks_ms()
            self.twinkle_direction = -self.twinkle_direction
        
def draw_text(lines, star_count):
    # Go from light to dark text
    grey = 160 - star_count * 10
    # Draw the text
    graphics.set_pen(graphics.create_pen(grey, grey, grey))
    for i, line in enumerate(lines):
        graphics.text(line, 0, 19 + i * 6, wordwrap=-1, scale=1)

# Create a list of stars starting with 1
stars = [Star(4,4)]
star_introduction_duration_s = 5
last_star_introduction_time = time.ticks_ms()
star_text = (
    "Blue",
    "Bath",
    "Bright",
    "Brush",
    "More?",
    "Jammy",
    "Dark",
    "Toy",
    "Tricks",
    "Bed",
    "Heaven",
    "Book",
    "Late",
    "Pray",
    "Fancy",
    "Kiss",
    "Count",
    "Night",
    "Sheep",
    "Sleep"
)
star_display_text_lines = (star_text[0], star_text[1])
while True:
    # if A, B, C, or D are pressed then reset
    if pressed() is not None:
        machine.reset()

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        cu.adjust_brightness(+0.01)

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        cu.adjust_brightness(-0.01)
    # Create a star object
    # As the number of stars increases move towards black background
    # max blue 46,68,130
    graphics.set_pen(graphics.create_pen(int(BLUE_SKY_COLOR[0]*(1-len(stars)/10)), int(BLUE_SKY_COLOR[1]*(1-len(stars)/10)), int(BLUE_SKY_COLOR[2]*(1-len(stars)/10))))
    graphics.clear()
    # Draw the stars
    for star in stars:
        star.draw()
    # Introduce a new star every star_introduction_duration_s maximim 10 stars
    if len(stars) < 10 and time.ticks_ms() - last_star_introduction_time > star_introduction_duration_s * 1000:
        # Find a random non conflicting position for the new star with at least 4 pixels distance from other stars
        x = 0
        y = 0
        star_display_text_lines = star_text[len(stars)*2:len(stars)*2+2]
        while True:
            # Pick random position not based on ticks_ms
            x = random.randint(2, 28)
            y = random.randint(2, 16)
            if all([math.sqrt((x - star.x) ** 2 + (y - star.y) ** 2) > 4 for star in stars]):
                stars.append(Star(x, y, random.randint(5, 10)/10))
                last_star_introduction_time = time.ticks_ms()
                break
    
    draw_text(star_display_text_lines, len(stars))
    # update the display
    cu.update(graphics)

    # pause for a moment (important or the USB serial device will fail)
    time.sleep(0.01)

