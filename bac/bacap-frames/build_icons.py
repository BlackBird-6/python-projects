'''
Builds all possible item icons (can be optimized)
'''

import os
import time
from PIL import Image

start = time.time()

# Mandatory directory switch
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set up the enchantment glint
glint = Image.open("images/glint.png").convert("RGBA")
glint_half_strength = glint.copy()
glint_data = glint_half_strength.load()
for x in range(glint_half_strength.width):
    for y in range(glint_half_strength.height):
        r, g, b, a = glint_data[x, y]
        glint_data[x, y] = (r, g, b, int(a/2)) # Halve alpha value

for frame_name in os.listdir("images/frames"):
    print(f"Building images for {frame_name}")
    frame_name = frame_name.replace(".png", "")

    if not os.path.exists(f"images/{frame_name}"):
        os.mkdir(f"images/{frame_name}")

    frame = Image.open(f"images/frames/{frame_name}.png").convert("RGBA")

    for item_name in os.listdir("images/mc_textures"):
        item_name = item_name.replace(".png", "")
        item = Image.open(f"images/mc_textures/{item_name}.png").convert("RGBA")

        # Make normal version
        new_frame = frame.copy()
        new_frame.paste(item, (20, 20), item)
        new_frame.save(f"images/{frame_name}/{item_name}.png")


        # Make enchanted version
        ench_item = item.copy()
        ench_item.alpha_composite(glint_half_strength,(0,0),(0,0))

        img_pixels = []
        for r, g, b, a in ench_item.getdata():
            if a < 255:
                img_pixels.append((r, g, b, 0))
            else:
                img_pixels.append((r, g, b, 255))

        ench_item = Image.new("RGBA", (64, 64))
        ench_item.putdata(img_pixels)

        # Enchanted item and normal item take the exact same set of pixels so no new copy is necessary
        new_frame.paste(ench_item, (20, 20), ench_item)
        new_frame.save(f"images/{frame_name}/{item_name}_ench.png")

print("DONE")
print(f"Runtime: {time.time() - start} seconds")
