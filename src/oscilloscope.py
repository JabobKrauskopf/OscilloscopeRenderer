import cv2
import numpy as np
import pafy

url = 'https://www.youtube.com/watch?v=OqJBloDEwwY'
vPafy = pafy.new(url)
play = vPafy.getbest()

cap = cv2.VideoCapture(play.url)

while True:
    ret, frame = cap.read()
    edges = cv2.Canny(frame, 100, 200)
    emptyImage = np.zeros((len(frame), len(frame[0]), 3), dtype=np.uint8)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 10, maxLineGap=1, minLineLength=1)

    try:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(emptyImage, (x1, y1), (x2, y2), (255, 0, 0), 1)
    except TypeError:
        pass
    emptyImage = cv2.resize(emptyImage, None, fx=1, fy=1)
    cv2.imshow("frame", emptyImage)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
