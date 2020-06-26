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
    emptyImage = np.zeros((len(frame), len(frame[0]), 3), dtype=np.uint8)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 10, maxLineGap=15, minLineLength=20)
    # try:
    #     lines = np.random.choice(lines, int(len(lines / 2)))
    # except TypeError:
    #     pass

    try:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(emptyImage, (x1, y1), (x2, y2), (255, 0, 0), 1)
    except TypeError:
        pass
    cv2.imshow("frame", emptyImage)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()