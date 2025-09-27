# keyboard_scroller.py
from RPiKeyboardConfig.keyboard import RPiKeyboardConfig
import time

def rgb_to_hsv_tuple(r, g, b):
    """
    Convert 8-bit RGB (0–255 each) to HSV tuple for RPiKeyboardConfig.
    
    Returns:
        (hue, saturation, value) as integers in range 0–255.
    """
    import colorsys

    # Normalise RGB to 0–1 for conversion
    r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0

    # Use Python's colorsys (returns h, s, v in range [0.0, 1.0])
    h, s, v = colorsys.rgb_to_hsv(r_n, g_n, b_n)

    # Convert back to 0–255 scale for the keyboard
    hue = int(h * 255)
    sat = int(s * 255)
    val = int(v * 255)

    return (hue, sat, val)

class KeyboardScroller:
    """Display scrolling text on the Raspberry Pi 500 keyboard RGB LEDs."""

    # --- 4×5 pixel font (complete A–Z, 0–9, space) --------------------------
    FONT = {
        "A": ["0110",
              "1001",
              "1111",
              "1001",
              "1001"],
        "B": ["1110",
              "1001",
              "1110",
              "1001",
              "1110"],
        "C": ["0111",
              "1000",
              "1000",
              "1000",
              "0111"],
        "D": ["1110",
              "1001",
              "1001",
              "1001",
              "1110"],
        "E": ["1111",
              "1000",
              "1110",
              "1000",
              "1111"],
        "F": ["1111",
              "1000",
              "1110",
              "1000",
              "1000"],
        "G": ["0111",
              "1000",
              "1011",
              "1001",
              "0111"],
        "H": ["1001",
              "1001",
              "1111",
              "1001",
              "1001"],
        "I": ["111",
              "010",
              "010",
              "010",
              "111"],
        "J": ["0011",
              "0001",
              "0001",
              "1001",
              "0110"],
        "K": ["1001",
              "1010",
              "1100",
              "1010",
              "1001"],
        "L": ["1000",
              "1000",
              "1000",
              "1000",
              "1111"],
        "M": ["10001",
              "11011",
              "10101",
              "10001",
              "10001"],
        "N": ["1001",
              "1101",
              "1011",
              "1001",
              "1001"],
        "O": ["0110",
              "1001",
              "1001",
              "1001",
              "0110"],
        "P": ["1110",
              "1001",
              "1110",
              "1000",
              "1000"],
        "Q": ["0110",
              "1001",
              "1001",
              "1011",
              "0111"],
        "R": ["1110",
              "1001",
              "1110",
              "1010",
              "1001"],
        "S": ["0111",
              "1000",
              "0110",
              "0001",
              "1110"],
        "T": ["11111",
              "00100",
              "00100",
              "00100",
              "00100"],
        "U": ["1001",
              "1001",
              "1001",
              "1001",
              "0110"],
        "V": ["1001",
              "1001",
              "1001",
              "0101",
              "0010"],
        "W": ["10001",
              "10001",
              "10101",
              "11011",
              "10001"],
        "X": ["1001",
              "0101",
              "0010",
              "0101",
              "1001"],
        "Y": ["1001",
              "0101",
              "0010",
              "0010",
              "0010"],
        "Z": ["1111",
              "0001",
              "0010",
              "0100",
              "1111"],
        "0": ["0110",
              "1001",
              "1001",
              "1001",
              "0110"],
        "1": ["0010",
              "0110",
              "0010",
              "0010",
              "0111"],
        "2": ["1110",
              "0001",
              "0110",
              "1000",
              "1111"],
        "3": ["1110",
              "0001",
              "0110",
              "0001",
              "1110"],
        "4": ["1001",
              "1001",
              "1111",
              "0001",
              "0001"],
        "5": ["1111",
              "1000",
              "1110",
              "0001",
              "1110"],
        "6": ["0110",
              "1000",
              "1110",
              "1001",
              "0110"],
        "7": ["1111",
              "0001",
              "0010",
              "0100",
              "0100"],
        "8": ["0110",
              "1001",
              "0110",
              "1001",
              "0110"],
        "9": ["0110",
              "1001",
              "0111",
              "0001",
              "1110"],
        " ": ["0000",
              "0000",
              "0000",
              "0000",
              "0000"]
    }

    def __init__(self, text="HELLO PI 500", colour=(0, 255, 255), delay=0.10):
        """
        :param text: Message to display
        :param colour: (hue, saturation, value) tuple
        :param delay: Time between scroll frames
        """
        self.text = text.upper()
        self.colour = colour
        self.delay = delay

        # Initialize keyboard
        self.kb = RPiKeyboardConfig()
        self.kb.reset_presets_and_direct_leds()
        self.kb.set_led_direct_effect()

        # Build LED matrix
        self.leds = [self.kb.get_led_info(i) for i in range(self.kb.get_number_leds())]
        self.matrix_map = {tuple(led[3]): led for led in self.leds}
        self.ROWS, self.COLS = 6, 16

        # Prepare text bitmap
        self.bitmap, self.bmp_w, self.bmp_h = self._make_bitmap(self.text)

    # -------------------------------------------------------------------------
    def _make_bitmap(self, text):
        """Return 2D bitmap for text message."""
        width = len(text) * 6
        height = 5
        bmp = [[0] * width for _ in range(height)]
        x = 0
        for ch in text:
            pattern = self.FONT.get(ch, self.FONT[" "])
            char_width = max(len(row) for row in pattern)
            for y, row in enumerate(pattern):
                for xx, bit in enumerate(row):
                    if bit == "1":
                        bmp[y][x + xx] = 1
            x += char_width + 1 
        return bmp, width, height

    # -------------------------------------------------------------------------
    def _clear(self):
        """Turn off all LEDs."""
        for (r, c) in self.matrix_map:
            self.kb.set_led_by_matrix(matrix=[r, c], colour=(0, 255, 0))

    # -------------------------------------------------------------------------
    def display(self, repeat=True):
        """Scroll the message across the keyboard."""
        try:
            while True:
                for shift in range(self.bmp_w + self.COLS):
                    self._clear()
                    for r in range(self.bmp_h):
                        for c in range(self.COLS):
                            src_x = c + shift - self.COLS
                            if 0 <= src_x < self.bmp_w and self.bitmap[r][src_x]:
                                if (r, c) in self.matrix_map:
                                    self.kb.set_led_by_matrix(matrix=[r, c], colour=self.colour)
                    self.kb.send_leds()
                    time.sleep(self.delay)
                if not repeat:
                    break
        except KeyboardInterrupt:
            self._clear()
            self.kb.send_leds()
            print("\nStopped scrolling.")




#from keyboard_scroller import KeyboardScroller

# Scroll in red, slow speed
scroller = KeyboardScroller(text="WELCOME HOME", colour= rgb_to_hsv_tuple(255, 0, 0), delay=0.12)
scroller.display()
