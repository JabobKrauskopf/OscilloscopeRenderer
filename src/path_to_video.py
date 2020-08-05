import numpy as np
import cv2
import json
import os

with open('json/BURNS_-_When_I\'m_Around_U_(Official_Music_Video).json') as json_file:
    data = json.load(json_file)

if not os.path.exists('video'):
    os.makedirs('video')

frames = data['frames']

video = cv2.VideoWriter(os.path.join("video", data['title'] + '.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), 30, (data["sizeX"], data["sizeY"]))

for frame in frames:
    image = np.zeros((data["sizeY"], data["sizeX"],3), np.uint8)
    for point in frame:
        point.reverse()
    for index in range(1, len(frame)):
        cv2.line(image, tuple(frame[index-1]), tuple(frame[index]), (255,0,0), 1)
    video.write(image)

video.release()
