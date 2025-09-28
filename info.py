from RPiKeyboardConfig.keyboard import RPiKeyboardConfig

kb = RPiKeyboardConfig()
names = kb.get_all_keynames()
num_leds = kb.get_number_leds()

print(f"Total LEDs: {num_leds}")
print(f"Total key name entries: {len(names)}")
print("-" * 70)

for i in range(num_leds):
    info = kb.get_led_info(i)
    x, y, z, rc = info
    row, col = rc

    # Get readable key name
    if i < len(names):
        name_entry = names[i]
        if isinstance(name_entry, dict):
            keyname = name_entry.get("name", "UNKNOWN")
        else:
            keyname = str(name_entry)
    else:
        keyname = "NO_NAME"

    print(f"LED {i:>2} | Row {row:<2} Col {col:<2} | X={x:<5} Y={y:<5} | {keyname}")

