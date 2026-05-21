"""Quick verification script to confirm FOOD_COLOR value in snake_game.py"""
import re

with open('snake_game.py', 'r') as f:
    content = f.read()
    
# Find FOOD_COLOR definition
match = re.search(r'FOOD_COLOR\s*=\s*\((\d+),\s*(\d+),\s*(\d+)\)', content)
if match:
    r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
    print(f"FOOD_COLOR RGB values: ({r}, {g}, {b})")
    print(f"Expected: (100, 200, 255)")
    
    if (r, g, b) == (100, 200, 255):
        print("✓ Color is CORRECT - Light Blue")
    else:
        print(f"✗ Color is WRONG - Got ({r}, {g}, {b}) instead")
        
    # Show perceived brightness
    brightness = (r + g + b) / 3
    print(f"Average brightness: {brightness:.1f}/255 ({brightness/255*100:.1f}%)")
    
    if brightness > 200:
        print("WARNING: High brightness - may appear whitish")
    else:
        print("Brightness is reasonable for light blue")
else:
    print("ERROR: Could not find FOOD_COLOR definition")
