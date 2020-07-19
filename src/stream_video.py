import cv2
import numpy as np
import pafy
import datetime
import math

url = 'https://youtu.be/VYOjWnS4cMY'
vPafy = pafy.new(url)
play = vPafy.getbest()

cap = cv2.VideoCapture(play.url)

start_time = datetime.datetime.now()

points = []
angles = []

while True:
    ret, frame = cap.read()
    try:
        edges = cv2.Canny(frame, 100, 200)
        emptyImage = np.zeros((len(frame), len(frame[0]), 3), dtype=np.uint8)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 1, maxLineGap=1, minLineLength=10)

        try:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    points.append([(x1, y1), (x2, y2)])
                    angles.append(math.atan(y2 - y1, x2 - x1) * 180 / np.pi)
                    cv2.line(emptyImage, (x1, y1), (x2, y2), (255, 0, 0), 1)
        except TypeError:
            pass
        cv2.imshow("frame", emptyImage)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            break
    except TypeError:
        cap.release()
        cv2.destroyAllWindows()
        break

print("This took " + str((datetime.datetime.now() - start_time).total_seconds()))

print(points)
print(angles)
