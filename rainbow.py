import time
import machine
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY

# Setup display and device
cu = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)
graphics.set_font("bitmap6")
cu.set_brightness(0.6)

WIDTH = CosmicUnicorn.WIDTH
HEIGHT = CosmicUnicorn.HEIGHT

# Animation timing constants
LINE_ANIMATION_SPEED = 2.5     # Seconds between each line appearing
FULL_RAINBOW_DURATION = 10.0     # Seconds to show full rainbow with heart
WAIT_DURATION = 1.0            # Seconds to wait before restarting cycle
FRAME_DELAY = 0.05              # Seconds between animation frames

# Animation state
state = 0
last_switch = 0
cycle_start = 0
current_phase = 0
current_line = 0

# Rainbow colors (Red, Orange, Yellow, Green, Blue, Indigo, Violet)
RAINBOW_COLORS = [
    (255, 0, 0),      # Red
    (255, 165, 0),    # Orange
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (75, 0, 130),     # Indigo
    (238, 130, 238),  # Violet
]

# Animation phases
PHASES = [
    "COLOR_BY_COLOR",  # Show rainbow colors one at a time
    "FULL_RAINBOW",    # Show full rainbow with black heart (includes wait time)
]

def draw_rainbow_color_by_color():
    """Draw rainbow colors one at a time across the display"""
    global current_line
    
    # Clear display
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()
    
    # Calculate color blocks: 4 rows per color + 2 padding rows at top and bottom
    padding_rows = 2
    rows_per_color = 4
    total_colors = len(RAINBOW_COLORS)
    
    # Draw only the current color
    current_color = min(current_line, total_colors - 1)
    
    # Calculate start and end rows for the current color only
    start_row = padding_rows + (current_color * rows_per_color)
    end_row = start_row + rows_per_color
    
    # Draw only the current color
    r, g, b = RAINBOW_COLORS[current_color]
    graphics.set_pen(graphics.create_pen(r, g, b))
    for y in range(start_row, end_row):
        graphics.line(0, y, WIDTH, y)
    
    # Move to next color based on elapsed time
    elapsed_ms = time.ticks_diff(time.ticks_ms(), cycle_start)
    elapsed_seconds = elapsed_ms / 1000.0
    target_color = int(elapsed_seconds / LINE_ANIMATION_SPEED)  # One color per LINE_ANIMATION_SPEED seconds
    current_line = min(target_color, total_colors)


def draw_full_rainbow_with_heart():
    """Draw full rainbow background with a black heart at center"""
    # Draw rainbow background with color blocks
    padding_rows = 2
    rows_per_color = 4
    
    for y in range(HEIGHT):
        if y < padding_rows or y >= HEIGHT - padding_rows:
            # Padding rows (black)
            graphics.set_pen(graphics.create_pen(0, 0, 0))
        else:
            # Color rows
            color_index = (y - padding_rows) // rows_per_color
            if color_index < len(RAINBOW_COLORS):
                r, g, b = RAINBOW_COLORS[color_index]
                graphics.set_pen(graphics.create_pen(r, g, b))
            else:
                graphics.set_pen(graphics.create_pen(0, 0, 0))
        graphics.line(0, y, WIDTH, y)
    
    # Draw black heart at center
    heart_x = WIDTH // 2
    heart_y = HEIGHT // 2
    heart_size = 3
    
    # Create black pen for heart
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    
    # Heart shape pattern with notch at top
    heart_pattern = [
        (1, 0), (2, 0), (4, 0), (5, 0),        # Top row with center notch
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3),
        (1, 4), (2, 4), (3, 4), (4, 4), (5, 4),
        (2, 5), (3, 5), (4, 5),
        (3, 6),
    ]
    
    for dx, dy in heart_pattern:
        x = heart_x - heart_size + dx
        y = heart_y - heart_size + dy
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            graphics.pixel(x, y)

def draw_rainbow_animation():
    global state, last_switch, cycle_start, current_phase, current_line
    now = time.ticks_ms()
    
    # Check if any buttons are pressed to exit
    if (cu.is_pressed(CosmicUnicorn.SWITCH_A) or 
        cu.is_pressed(CosmicUnicorn.SWITCH_B) or 
        cu.is_pressed(CosmicUnicorn.SWITCH_C) or 
        cu.is_pressed(CosmicUnicorn.SWITCH_D)):
        machine.reset()
    
    # Initialize cycle if needed
    if cycle_start == 0:
        cycle_start = now
        current_phase = 0
        current_line = 0
    
    # Phase timing
    if current_phase == 0:  # COLOR_BY_COLOR
        if current_line >= len(RAINBOW_COLORS):  # When all colors are drawn
            current_phase = 1
            cycle_start = now
    elif current_phase == 1:  # FULL_RAINBOW
        # Phase 1 includes both rainbow display and wait time
        total_phase1_time = (FULL_RAINBOW_DURATION + WAIT_DURATION) * 1000  # Convert to milliseconds
        if time.ticks_diff(now, cycle_start) > total_phase1_time:
            current_phase = 0
            current_line = 0
            cycle_start = now
    
    # Debug output
    elapsed_ms = time.ticks_diff(now, cycle_start)
    
    # Draw based on current phase
    if current_phase == 0:
        draw_rainbow_color_by_color()
    elif current_phase == 1:
        draw_full_rainbow_with_heart()
    
    cu.update(graphics)

def init():
    global state, last_switch, cycle_start, current_phase, current_line
    state = 0
    last_switch = time.ticks_ms()
    cycle_start = 0
    current_phase = 0
    current_line = 0
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()

def draw():
    draw_rainbow_animation()

def main():
    init()
    while True:
        draw()
        time.sleep(FRAME_DELAY)

if __name__ == "__main__":
    main()
