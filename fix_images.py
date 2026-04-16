from PIL import Image
import os

folder = r"data\screenshots"

for f in os.listdir(folder):
    if f.endswith('.png'):
        p = os.path.join(folder, f)
        Image.open(p).save(p, 'PNG')
        print('OK: ' + f)

print('Termine !')