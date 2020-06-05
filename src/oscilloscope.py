import cv2
import numpy as np
import pafy

url = 'https://youtu.be/VYOjWnS4cMY'
vPafy = pafy.new(url)
play = vPafy.getbest()

cap = cv2.VideoCapture(play.url)

while True:
    ret, frame = cap.read()
    edges = cv2.Canny(frame, 100, 200)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 40, minLineLength=1, maxLineGap=40)

    # for line in lines:
    #     for x1, y1, x2, y2 in line:
    #         cv2.line(edges, (x1, y1), (x2, y2), (255, 0, 0), 1)
    cv2.imshow("frame", edges)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
