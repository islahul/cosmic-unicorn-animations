import time
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY

# Define color groups for the alphabet
COLOR_GROUPS = [
    ("ABCDEFG", (255, 0, 0)),        # Red
    ("HIJKLMNOP", (255, 165, 0)),    # Orange
    ("QRS", (0, 255, 0)),            # Green
    ("TUV", (0, 0, 255)),            # Blue
    ("WX", (75, 0, 130)),            # Indigo
    ("Y", (238, 130, 238)),          # Violet
    ("Z", (255, 255, 0)),            # Yellow
]

# Timing constants
LETTER_DELAY = 0.75  # 150ms between letters
SEQUENCE_DELAY = 1.25  # 250ms between sequences

cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)
graphics.set_font("bitmap8")
cu.set_brightness(0.6)

BACKGROUND = (0, 0, 0)

width = CosmicUnicorn.WIDTH
height = CosmicUnicorn.HEIGHT

def draw_letter(letter, color):
    graphics.set_pen(graphics.create_pen(*BACKGROUND))
    graphics.clear()
    graphics.set_pen(graphics.create_pen(*color))
    # Center the letter
    text_width = graphics.measure_text(letter, 2)
    x = (width - text_width) // 2
    y = 8
    graphics.text(letter, x, y, scale=2)
    cu.update(graphics)

def main():
    while True:
        for group, color in COLOR_GROUPS:
            for letter in group:
                draw_letter(letter, color)
                time.sleep(LETTER_DELAY)
            time.sleep(SEQUENCE_DELAY)

if __name__ == "__main__":
    main() 

