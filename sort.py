from colorthief import ColorThief
from matplotlib import pyplot as plt
import os
import colorsys

# ct = ColorThief("images/dp.jpg")
# dominant_colour = ct.get_color(quality=1)

# print(dominant_colour)
colors = []

for file in os.listdir('images/'):
    filename = os.fsdecode(file)
    ct = ColorThief(f"images/{file}")
    dom_col = ct.get_color(quality=1)

    print(dom_col)

    h, s, v = colorsys.rgb_to_hsv(dom_col[0], dom_col[1], dom_col[2])
    colors.append((h, s, v))

print(colors)
sorted_colors = colors.sort(key=colors[(0)])
print(sorted_colors)