# heart.py
from RPiKeyboardConfig.keyboard import RPiKeyboardConfig
import time
import colorsys

heart = [
    [None, (255,0,0), None, (255,0,0), None],
    [(255,0,0), None, (255,0,0), None, (255,0,0)],
    [(255,0,0)] * 5,
    [None, (255,0,0), (255,0,0), (255,0,0), None],
    [None, None, (255,0,0), None, None],
]


class KeyboardDisplay:
    """Simple RGB image display on the Raspberry Pi 500 keyboard LEDs."""

    def __init__(self):
        self.kb = RPiKeyboardConfig()
        self.kb.reset_presets_and_direct_leds()
        self.kb.set_led_direct_effect()

        leds = [self.kb.get_led_info(i) for i in range(self.kb.get_number_leds())]
        self.matrix_map = {tuple(led[3]): led for led in leds}

    # ---------------------------------------------------------------------
    @staticmethod
    def rgb_to_hsv_tuple(r, g, b):
        """Convert 8-bit RGB → HSV tuple (0–255 each) for keyboard."""
        r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
        h, s, v = colorsys.rgb_to_hsv(r_n, g_n, b_n)
        return (int(h * 255), int(s * 255), int(v * 255))

    # ---------------------------------------------------------------------
    def show_image(self, image_rgb):
        """
        Display an m×n RGB image (list of lists of (R,G,B) or None).
        Bottom row (row 5) is ignored due to the space bar.
        """
        rows = min(len(image_rgb), 5)  # only use top 5 rows
        cols = len(image_rgb[0])

        for r in range(rows):
            for c in range(cols):
                if (r, c) not in self.matrix_map:
                    continue
                colour = image_rgb[r][c]
                if colour is None:
                    # Off
                    self.kb.set_led_by_matrix(matrix=[r, c], colour=(0, 255, 0))
                else:
                    h, s, v = self.rgb_to_hsv_tuple(*colour)
                    self.kb.set_led_by_matrix(matrix=[r, c], colour=(h, s, v))
        self.kb.send_leds()

    # ---------------------------------------------------------------------
    def clear(self):
        """Turn off all LEDs."""
        for (r, c) in self.matrix_map:
            self.kb.set_led_by_matrix(matrix=[r, c], colour=(0, 255, 0))
        self.kb.send_leds()


# -------------------------------------------------------------------------
# Example usage
if __name__ == "__main__":
    kb_disp = KeyboardDisplay()

    # Define a simple 5×16 RGB image (gradient + red diagonal)
    ROWS, COLS = 5, 16
    image = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            if r == c // 3:  # diagonal accent
                row.append((255, 0, 0))        # red
            else:
                row.append((0, c * 15, 255))   # blue gradient
        image.append(row)

    #kb_disp.show_image(image)
    #print("Showing static RGB image (5×16) — Ctrl+C to exit.")
    #time.sleep(10)
    kb_disp.show_image(heart)
	

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        kb_disp.clear()
        print("\nKeyboard cleared.")
