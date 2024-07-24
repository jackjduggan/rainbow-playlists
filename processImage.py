from PIL import Image
from collections import Counter

def most_common_used_color(img):
    # Get width and height of Image
    width, height = img.size
    
    # Initialize a Counter to count colors
    color_counter = Counter()
    
    # Iterate through each pixel
    for x in range(width):
        for y in range(height):
            # r, g, b value of pixel
            color = img.getpixel((x, y))
            color_counter[color] += 1
    
    # Find the most common color and its count
    most_common_color, count = color_counter.most_common(1)[0]
    
    return most_common_color, count

# Read Image
img = Image.open('images/ab67616d00001e025881f12ca6d02eb7987dd09b.jpg')

# Convert Image into RGB
img = img.convert('RGB')

# Call function
common_color, count = most_common_used_color(img)

print(f"The most common color is: {common_color} with {count} pixels contributing to it.")
