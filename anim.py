# anim.py
from RPiKeyboardConfig.keyboard import RPiKeyboardConfig
import time
import colorsys


class KeyboardDisplay:
    """RGB image and animation display on Raspberry Pi 500 keyboard LEDs."""

    def __init__(self):
        self.kb = RPiKeyboardConfig()
        self.kb.reset_presets_and_direct_leds()
        self.kb.set_led_direct_effect()

        leds = [self.kb.get_led_info(i) for i in range(self.kb.get_number_leds())]
        self.matrix_map = {tuple(led[3]): led for led in leds}
        self.max_rows = 5  # avoid bottom spacebar row

    # ---------------------------------------------------------------------
    @staticmethod
    def rgb_to_hsv_tuple(r, g, b):
        """Convert RGB (0–255) → HSV (0–255) tuple for keyboard."""
        r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
        h, s, v = colorsys.rgb_to_hsv(r_n, g_n, b_n)
        return (int(h * 255), int(s * 255), int(v * 255))

    # ---------------------------------------------------------------------
    def show_image(self, image_rgb):
        """Display one static RGB image (list of rows of RGB tuples)."""
        rows = min(len(image_rgb), self.max_rows)
        cols = len(image_rgb[0])
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in self.matrix_map:
                    continue
                colour = image_rgb[r][c]
                if colour is None:
                    self.kb.set_led_by_matrix(matrix=[r, c], colour=(0, 255, 0))  # off
                else:
                    h, s, v = self.rgb_to_hsv_tuple(*colour)
                    self.kb.set_led_by_matrix(matrix=[r, c], colour=(h, s, v))
        self.kb.send_leds()

    # ---------------------------------------------------------------------
    def play_animation(self, frames, delay=0.1, loop=True):
        """
        Play a list of RGB frames (each frame = m×n matrix of (R,G,B) tuples or None).
        :param frames: list of image matrices
        :param delay: seconds between frames
        :param loop: whether to loop indefinitely
        """
        try:
            while True:
                for frame in frames:
                    self.show_image(frame)
                    time.sleep(delay)
                if not loop:
                    break
        except KeyboardInterrupt:
            self.clear()
            print("\nAnimation stopped and cleared.")

    # ---------------------------------------------------------------------
    def clear(self):
        """Turn off all LEDs."""
        for (r, c) in self.matrix_map:
            self.kb.set_led_by_matrix(matrix=[r, c], colour=(0, 255, 0))
        self.kb.send_leds()


# anim_demo.py
#from keyboard_display_anim import KeyboardDisplay
#import time

disp = KeyboardDisplay()

ROWS, COLS = 5, 16

# Frame 1: blue background with red diagonal
frame1 = [[(0, 0, 255) if c != r*3 else (255, 0, 0) for c in range(COLS)] for r in range(ROWS)]

# Frame 2: inverse (red background with blue diagonal)
frame2 = [[(255, 0, 0) if c != r*3 else (0, 0, 255) for c in range(COLS)] for r in range(ROWS)]

# Frame 3: green checkerboard
frame3 = [[(0, 255, 0) if (r + c) % 2 == 0 else (0, 0, 0) for c in range(COLS)] for r in range(ROWS)]

# Play animation
frames = [frame1, frame2, frame3]
disp.play_animation(frames, delay=0.3, loop=True)
