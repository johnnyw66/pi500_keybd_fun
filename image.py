# image.py
from RPiKeyboardConfig.keyboard import RPiKeyboardConfig
import time

# --- Keyboard setup ----------------------------------------------------------
kb = RPiKeyboardConfig()
kb.reset_presets_and_direct_leds()
kb.set_led_direct_effect()

# Get LED info and map row/column positions
leds = [kb.get_led_info(i) for i in range(kb.get_number_leds())]
matrix_map = {tuple(led[3]): led for led in leds}

# --- Image definition --------------------------------------------------------
# Each pixel = (hue, saturation, value)
# None = LED off
# Matrix is 5 rows high (avoid row 5)
ROWS, COLS = 5, 16

# Example pattern — rainbow gradient with a diagonal
image = [
    [(0 + c*10) % 255 for c in range(COLS)] for r in range(ROWS)
]

# --- Render function ---------------------------------------------------------
def show_image(image, hue_offset=0):
    """Display a hue-based image (HSV) on keyboard LEDs."""
    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) not in matrix_map:
                continue
            hue = image[r][c]
            colour = ( (hue + hue_offset) % 255, 255, 255 )  # HSV tuple
            kb.set_led_by_matrix(matrix=[r, c], colour=colour)
    kb.send_leds()

# --- Display static image ----------------------------------------------------
show_image(image)

print("Showing static 5x16 image pattern — Ctrl+C to exit.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Clear LEDs on exit
    for (r, c) in matrix_map:
        kb.set_led_by_matrix(matrix=[r, c], colour=(0, 255, 0))
    kb.send_leds()
    print("\nCleared.")
