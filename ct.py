from colorthief import ColorThief
from matplotlib import pyplot as plt

ct = ColorThief("images/dp.jpg")
dominant_colour = ct.get_color(quality=1)

print(dominant_colour)

plt.imshow([[dominant_colour]])
plt.show()