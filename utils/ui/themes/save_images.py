import os

import PIL.Image as Image


with open('resources.py', 'w') as f:
    f.write('resources = {\n')

    for file in os.listdir("../../../images"):
        if file.endswith('.png'):
            img = open(f"../../../images/{file}", 'rb')
            f.write(f"    '{file[:-4]}': {repr(img.read())},\n")

    f.write("}\n")
