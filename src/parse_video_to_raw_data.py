import cv2
import numpy as np
import pafy
import datetime
import json
import os
import re

url = 'https://www.youtube.com/watch?v=VYOjWnS4cMY'
vPafy = pafy.new(url)
video = vPafy.getbest()
title = re.sub("\s", "_", video.title)

if not os.path.exists(title):
    os.makedirs(title)

cap = cv2.VideoCapture(video.url)

startTime = datetime.datetime.now()

def find_starting_point(matrix):
    for (x,y), value in np.ndenumerate(matrix):
        if value > 0:
            return (x, y)

def depth_first_search(visited, image, point):
    visited[point[0]][point[1]] = True

frame_number = 0
while True:
    ret, frame = cap.read()
    if frame_number % 10 == 0:
        try:
            image = cv2.Canny(frame, 150, 200)
            if np.sum(image) > 0:
                visited_pixels = np.full((cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT), False)
                starting_point = find_starting_point(image)
                depth_first_search(visited_pixels, image, starting_point)
        except:
            cap.release()
            break
        cv2.imshow("frame", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            break
    frame_number += 1

print("This took " + str((datetime.datetime.now() - startTime).total_seconds()))
