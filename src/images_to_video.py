from os import listdir
from os.path import isfile, join
import cv2
import re

files = sorted([join('Stella_Gets_the_Zoomies!', f) for f in listdir('Stella_Gets_the_Zoomies!') if isfile(join('Stella_Gets_the_Zoomies!', f))], key=lambda x: int(re.match(r"[^\d]*(?P<number>\d+)\.jpg", x).group('number')))
print(files)

img_array = []
for file in files:
    img = cv2.imread(file)
    height, width, layers = img.shape
    size = (width, height)
    img_array.append(img)

out = cv2.VideoWriter('Stella_Gets_the_Zoomies!', cv2.VideoWriter_fourcc(*'MP4V'), 10, size)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()
