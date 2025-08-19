import time
import machine
from cosmic import CosmicUnicorn
from picographics import PicoGraphics, DISPLAY_COSMIC_UNICORN as DISPLAY

# --- Menu Display Constants ---
MENU_TOP_START_Y = 0         # y position for first option
MENU_LEFT_START_X = 0        # x position for circle
MENU_CIRCLE_RADIUS = 1       # radius of the colored circle
MENU_TEXT_OFFSET_X = 3 + MENU_CIRCLE_RADIUS  # x offset for text from left
MENU_OPTION_SPACING_Y = 8    # vertical spacing between options
MENU_CIRCLE_CENTER_OFFSET_Y = 2 + MENU_CIRCLE_RADIUS  # offset to center circle with text

# create cosmic object and graphics surface for drawing
cosmic = CosmicUnicorn()
graphics = PicoGraphics(DISPLAY)

brightness = 0.5

# Menu structure: [ (menu_name, [(option_name, effect_module_name or None)]) ]
MENU = [
    ("SEQ", [
        ("LIFT", "elevator"),
        ("ABCD", "alphabet_sequence"),
        ("TRAF", "traffic_lights"),
        ("RBOW", "rainbow"),
    ]),
    ("STDBY", [
        ("WTIME", None),
        ("FIRE", "fire"),
        ("STAR", "stars"),
        ("COMP", "supercomputer"),
    ]),
    ("QUIZ", [
        ("COLOR", None),
        ("----", None),
        ("----", None),
        ("----", None),
    ]),
    ("PARTY", [
        ("----", None),
        ("----", None),
        ("----", None),
        ("----", None),
    ]),
]

BUTTONS = [
    CosmicUnicorn.SWITCH_A,
    CosmicUnicorn.SWITCH_B,
    CosmicUnicorn.SWITCH_C,
    CosmicUnicorn.SWITCH_D,
]

# returns the index of the button that is currently pressed or None if none are
# 0: A, 1: B, 2: C, 3: D

def pressed_index():
    for i, btn in enumerate(BUTTONS):
        if cosmic.is_pressed(btn):
            return i
    return None

def wait_for_button_release():
    while pressed_index() is not None:
        time.sleep(0.05)

def show_menu(title, options):
    graphics.set_font("bitmap6")
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()
    # Define four distinct colors (red, green, blue, yellow)
    colors = [
        graphics.create_pen(255, 0, 0),    # Red
        graphics.create_pen(0, 255, 0),    # Green
        graphics.create_pen(0, 128, 255),  # Blue
        graphics.create_pen(255, 200, 0),  # Yellow
    ]
    for i, (opt, _) in enumerate(options):
        pen = colors[i % len(colors)]
        graphics.set_pen(pen)
        y = MENU_TOP_START_Y + i * MENU_OPTION_SPACING_Y
        # Draw a small circle
        graphics.circle(MENU_LEFT_START_X + MENU_CIRCLE_RADIUS, y + MENU_CIRCLE_CENTER_OFFSET_Y, MENU_CIRCLE_RADIUS)
        # Draw the option text in the same color, offset right of the circle
        graphics.text(f"{opt}", MENU_LEFT_START_X + MENU_TEXT_OFFSET_X, y, -1, 1)
    cosmic.set_brightness(brightness)
    cosmic.update(graphics)

def menu_select(title, options):
    # Show menu and wait for A/B/C/D
    while True:
        show_menu(title, options)
        # brightness up/down
        global brightness
        if cosmic.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
            brightness += 0.01
        if cosmic.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
            brightness -= 0.01
        brightness = max(min(brightness, 1.0), 0.0)
        cosmic.set_brightness(brightness)
        idx = pressed_index()
        if idx is not None and idx < len(options):
            wait_for_button_release()
            return idx
        time.sleep(0.01)

def run_effect(effect_name):
    try:
        if effect_name is None:
            import fire as effect
        else:
            effect = __import__(effect_name)
        effect.graphics = graphics
        effect.init()
        sleep = False
        was_sleep_pressed = False
        while True:
            # if A, B, C, or D are pressed then reset to menu
            if pressed_index() is not None:
                machine.reset()
            sleep_pressed = cosmic.is_pressed(CosmicUnicorn.SWITCH_SLEEP)
            if sleep_pressed and not was_sleep_pressed:
                sleep = not sleep
            was_sleep_pressed = sleep_pressed
            if sleep:
                cosmic.set_brightness(cosmic.get_brightness() - 0.01)
                if cosmic.get_brightness() > 0.0:
                    effect.draw()
                cosmic.update(graphics)
            else:
                effect.draw()
                cosmic.update(graphics)
                # brightness up/down
                global brightness
                if cosmic.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_UP):
                    brightness += 0.01
                if cosmic.is_pressed(CosmicUnicorn.SWITCH_BRIGHTNESS_DOWN):
                    brightness -= 0.01
                brightness = max(min(brightness, 1.0), 0.0)
                cosmic.set_brightness(brightness)
            time.sleep(0.001)
    except Exception as e:
        # fallback: show error and return to menu
        graphics.set_pen(graphics.create_pen(255, 0, 0))
        graphics.clear()
        graphics.text("Error!", 2, 2, -1, 1)
        graphics.text(str(e), 2, 10, -1, 1)
        cosmic.update(graphics)
        time.sleep(2)
        machine.reset()

# Main menu loop
while True:
    main_idx = menu_select("MENU", [(m[0], None) for m in MENU])
    submenu = MENU[main_idx]
    sub_idx = menu_select(submenu[0], submenu[1])
    effect_name = submenu[1][sub_idx][1]
    run_effect(effect_name)

