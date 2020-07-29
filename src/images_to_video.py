from os import listdir
from os.path import isfile, join
import cv2
files = [join('Childish_Gambino_-_This_Is_America_(Official_Video)', f) for f in listdir('Childish_Gambino_-_This_Is_America_(Official_Video)') if isfile(join('Childish_Gambino_-_This_Is_America_(Official_Video)', f))]

img_array = []
for file in files:
    img = cv2.imread(file)
    height, width, layers = img.shape
    size = (width, height)
    img_array.append(img)

out = cv2.VideoWriter('project.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, size)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()
