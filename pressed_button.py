from cosmic import CosmicUnicorn

def pressed_button(cu):
    for button in [CosmicUnicorn.SWITCH_A, CosmicUnicorn.SWITCH_B, CosmicUnicorn.SWITCH_C, CosmicUnicorn.SWITCH_D]:
        if cu.is_pressed(button):
            return button
    return None