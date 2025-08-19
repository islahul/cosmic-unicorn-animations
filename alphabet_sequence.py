import time
import machine
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY

# Define color groups for each letter
COLOR_GROUPS = [
    ("ABCDEFG", (255, 0, 0)),        # Red
    ("HIJKLMNOP", (255, 165, 0)),    # Orange
    ("QRS", (0, 255, 0)),            # Green
    ("TUV", (0, 0, 255)),            # Blue
    ("WX", (75, 0, 130)),            # Indigo
    ("Y", (238, 130, 238)),          # Violet
    ("Z", (255, 255, 0)),            # Yellow
]

# Timing – the elevator script used short waits to keep the animation snappy.
LETTER_DELAY = 0.75          # 750 ms between letter changes
SEQUENCE_DELAY = 1.25        # 1250 ms between colour blocks

# Create the CosmicUnicorn object and a graphics surface.
cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)
graphics.set_font("sans")

# Use the same brightness level that works fine in the elevator demo.
cu.set_brightness(0.8)

# Surface dimensions – the display is 32×32.
width = CosmicUnicorn.WIDTH
height = CosmicUnicorn.HEIGHT
FONT_SCALE = 1

# Animation state
current_group = 0
current_letter = 0
last_update = 0
frame_delay = LETTER_DELAY

# Helper to draw a single centred letter.
def draw_letter(letter: str, colour: tuple[int, int, int]):
    # Background is just a full‑screen clear with the background pen.
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()

    # Choose a different pen for the letter itself.
    letter_pen = graphics.create_pen(*colour)
    graphics.set_pen(letter_pen)

    # How wide is the letter at the chosen scale?
    text_width = graphics.measure_text(letter, FONT_SCALE)
    x = (width - text_width) // 2

    # For vector fonts like "sans", at scale=1:
    y = 16

    graphics.text(letter, x, y, scale=FONT_SCALE)
    cu.update(graphics)

# Main animation loop.
while True:
    # Check if any buttons are pressed to exit
    if (cu.is_pressed(CosmicUnicorn.SWITCH_A) or 
        cu.is_pressed(CosmicUnicorn.SWITCH_B) or 
        cu.is_pressed(CosmicUnicorn.SWITCH_C) or 
        cu.is_pressed(CosmicUnicorn.SWITCH_D)):
        machine.reset()
    
    current_time = time.ticks_ms()
    
    # Check if it's time to update the display
    if time.ticks_diff(current_time, last_update) >= (frame_delay * 1000):
        # Get current group and letter
        group, colour = COLOR_GROUPS[current_group]
        letter = group[current_letter]
        
        # Draw the current letter
        draw_letter(letter, colour)
        
        # Move to next letter
        current_letter += 1
        
        # If we've shown all letters in this group
        if current_letter >= len(group):
            current_letter = 0
            current_group += 1
            
            # If we've shown all groups, start over
            if current_group >= len(COLOR_GROUPS):
                current_group = 0
            
            # Use sequence delay between groups
            frame_delay = SEQUENCE_DELAY
        else:
            # Use letter delay between letters
            frame_delay = LETTER_DELAY
        
        last_update = current_time
    
    # Small delay to prevent overwhelming the system
    time.sleep(0.01)
        