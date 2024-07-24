from colorthief import ColorThief
from matplotlib import pyplot as plt
import os
import colorsys

def rgb_to_hsv(rgb):
    return colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)

def hsv_to_rgb(hsv):
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)

# List to hold the dominant colors in HSV format
colors_hsv = []

# Directory containing images
image_dir = 'images/'

# Extract dominant colors from images and convert to HSV
for file in os.listdir(image_dir):
    filename = os.fsdecode(file)
    ct = ColorThief(os.path.join(image_dir, filename))
    dom_col = ct.get_color(quality=1)

    print(f"Dominant color (RGB) of {filename}: {dom_col}")

    # Convert RGB to HSV
    h, s, v = rgb_to_hsv(dom_col)
    colors_hsv.append((h, s, v))

print("HSV colors before sorting:", colors_hsv)

# Sort the colors by the hue value
colors_hsv_sorted = sorted(colors_hsv, key=lambda x: x[0])

# Convert sorted HSV colors back to RGB
sorted_colors_rgb = [hsv_to_rgb(hsv) for hsv in colors_hsv_sorted]

print("Sorted colors (RGB):", sorted_colors_rgb)

# Plot the sorted colors
plt.figure(figsize=(10, 2))
for i, color in enumerate(sorted_colors_rgb):
    plt.fill_between([i, i + 1], 0, 1, color=[c / 255.0 for c in color])

plt.axis('off')
plt.show()
