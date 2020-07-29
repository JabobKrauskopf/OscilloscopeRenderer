import cv2
import numpy as np
import json

with open('data2.json', 'r') as f:
    data = json.loads(f.read())

for frame in data['frames']:
    lastPoint = frame[0]
    emptyImage = np.zeros((int(data['sizeY']), int(data['sizeX']), 3), dtype=np.uint8)
    for point in frame[1:]:
        cv2.line(emptyImage, (lastPoint[0], lastPoint[1]), (point[0], point[1]), (255, 0, 0), 1)
        lastPoint = point
    cv2.imshow("frame", emptyImage)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        cv2.destroyAllWindows()
        break

