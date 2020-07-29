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

parsedJson = {'title': title, 'length': 0, 'sizeX': cap.get(cv2.CAP_PROP_FRAME_WIDTH), 'sizeY': cap.get(cv2.CAP_PROP_FRAME_HEIGHT), 'video_url': url, 'frames': []}

frame_number = 0
while True:
    ret, frame = cap.read()
    try:
        edges = cv2.Canny(frame, 150, 200)
        # parsedJson['frames'].append(points)
        try:
            test = np.argwhere(edges > 0)
            drawn_points = [[int(y) for y in x] for x in np.argwhere(edges > 0)]
            parsedJson['frames'].append(drawn_points)
        except ValueError:
            pass
        cv2.imwrite(os.path.join(title, str(frame_number) + ".jpg"), edges)
        cv2.imshow("frame", edges)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            break
    except TypeError as e:
        print(e)
        cap.release()
        break
    frame_number += 1

print("This took " + str((datetime.datetime.now() - startTime).total_seconds()))

parsedJson['length'] = len(parsedJson['frames'])

with open('data.json', 'w') as f:
    json.dump(parsedJson, f)
