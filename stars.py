import time
import machine
import math
import random
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY
import pressed_button

# Constants for the display
BLUE_SKY_COLOR = (5, 6, 25)
STAR_CENTER_COLOR = (255, 255, 255)
STAR_SURROUNDING_COLOR = (10, 10, 10)
STAR_TWINKLE_COLOR = (255, 255, 255)
TWINKLE_INTENSITY_MULTIPLIER = 0.1
STAR_INTRO_MS = 5000
TEXT_STARTING_COLOR = (160, 160, 160)
TEXT_DARKENING_RATE = 10

# Initialize CosmicUnicorn and graphics
cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)
graphics.set_font("bitmap4")
cu.set_brightness(0.8)

# Star class for twinkling effect
class Star:
    def __init__(self, x, y, twinkle_frequency=1):
        self.x = x
        self.y = y
        self.start_time = time.ticks_ms()
        self.twinkle_direction = -1
        self.pausing_time = twinkle_frequency / 10

    def draw(self):
        current_time = time.ticks_ms()
        elapsed_time = current_time - self.start_time

        if elapsed_time < self.pausing_time * 1000:
            return

        twinkle_intensity = TWINKLE_INTENSITY_MULTIPLIER + TWINKLE_INTENSITY_MULTIPLIER * math.sin(elapsed_time * 2 * math.pi / (self.pausing_time * 10000))
        twinkle_intensity = max(0, min(TWINKLE_INTENSITY_MULTIPLIER*2, twinkle_intensity))

        # Draw center pixel
        graphics.set_pen(graphics.create_pen(*STAR_CENTER_COLOR))
        graphics.pixel(self.x, self.y)

        # Draw surrounding pixels with lower intensity
        graphics.set_pen(graphics.create_pen(*STAR_SURROUNDING_COLOR))
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            graphics.pixel(self.x + dx, self.y + dy)

        # Draw twinkle effect
        twinkle_color = tuple(*(int(c * twinkle_intensity) for c in STAR_TWINKLE_COLOR))
        graphics.set_pen(graphics.create_pen(*twinkle_color))
        if self.twinkle_direction == 1:
            for dy in [-1, 1]:
                graphics.pixel(self.x, self.y + dy)
        else:
            for dx in [-1, 1]:
                graphics.pixel(self.x + dx, self.y)

        if elapsed_time >= self.pausing_time * 10000:
            self.start_time = current_time
            self.twinkle_direction *= -1

# Draw text with fading effect
def draw_text(lines, star_count):
    text_color = tuple(int(color - star_count * 10) for color in TEXT_STARTING_COLOR)
    graphics.set_pen(graphics.create_pen(*text_color))
    for i, line in enumerate(lines):
        graphics.text(line, 0, 19 + i * 6, wordwrap=-1, scale=1)

# Star initialization
stars = [Star(random.randint(2, 28), random.randint(2, 16))]
last_star_introduction_time = time.ticks_ms()

# Text below the stars indicating the part of the book
star_text = [
    "Blue", "Bath", "Bright", "Brush", "More?", "Jammy", "Dark", "Toy",
    "Tricks", "Bed", "Heaven", "Book", "Late", "Pray", "Fancy", "Kiss",
    "Count", "Night", "Sheep", "Sleep"
]

# Main loop
while True:
    if pressed_button(cu):
        machine.reset()

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
        cu.adjust_brightness(+0.01)

    if cu.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
        cu.adjust_brightness(-0.01)

    # Update background color as stars increase
    star_count = len(stars)
    bg_color = [int(BLUE_SKY_COLOR[i] * (1 - star_count / 10)) for i in range(3)]
    graphics.set_pen(graphics.create_pen(*bg_color))
    graphics.clear()

    # Draw stars
    for star in stars:
        star.draw()

    # Introduce a new star periodically
    if star_count < 10 and time.ticks_ms() - last_star_introduction_time > STAR_INTRO_MS:
        while True:
            x, y = random.randint(2, 28), random.randint(2, 16)
            if all(math.sqrt((x - s.x) ** 2 + (y - s.y) ** 2) > 4 for s in stars):
                stars.append(Star(x, y, random.uniform(0.5, 1.0)))
                last_star_introduction_time = time.ticks_ms()
                break

    # Update the text based on the number of stars
    star_display_text_lines = star_text[star_count * 2:star_count * 2 + 2]
    draw_text(star_display_text_lines, star_count)

    cu.update(graphics)
    time.sleep(0.01)