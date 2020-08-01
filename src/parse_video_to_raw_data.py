import cv2
import numpy as np
import pafy
import datetime
import os
import re
import threading
import json

url = 'https://www.youtube.com/watch?v=VYOjWnS4cMY'
vPafy = pafy.new(url)
video = vPafy.getbest()
title = re.sub("\s", "_", video.title)

title = "Webcam"

if not os.path.exists(title):
    os.makedirs(title)

cap = cv2.VideoCapture(0)

startTime = datetime.datetime.now()

parsed_json = {"title": title, "sizeX": 0, "sizeY": 0, "frames": []}


def find_starting_point(drawn_pixels: np.array, visited_pixels: np.array, last_pixel: np.array):
    # print(last_pixel)
    if last_pixel is None:
        return drawn_pixels[0]
    smallest_distance = 1000000000
    smallest_distance_pixel = None

    index = 0
    for pixel in drawn_pixels:
        if not visited_pixels[pixel[0]][pixel[1]]:
            distance = (last_pixel[0]-pixel[0])**2 + (last_pixel[1]-pixel[1])**2
            if distance < smallest_distance:
                smallest_distance = distance
                smallest_distance_pixel = pixel
            if index > 400 and smallest_distance_pixel is not None:
                return smallest_distance_pixel
            index += 1
    return smallest_distance_pixel


def depth_first_search(visited: np.array, image: np.array, point: tuple, path: list, iteration_depth: int):
    x, y = point
    if visited[x][y] or image[x][y] <= 0:
        return path, visited, iteration_depth
    cache_path = []
    cache_path.append([int(x), int(y)])
    visited[x][y] = True
    iteration_depth += 1
    maximum_depth_array = [0, 0, 0, 0, 0, 0, 0, 0]
    branches = 0
    if x - 1 >= 0:
        cache_path, visited, maximum_depth_array[0] = depth_first_search(visited, image, (x-1, y), cache_path, iteration_depth)
        branches += 1
    if x + 1 < len(visited):
        cache_path, visited, maximum_depth_array[1] = depth_first_search(visited, image, (x+1, y), cache_path, iteration_depth)
        branches += 1
    if y - 1 >= 0:
        cache_path, visited, maximum_depth_array[2] = depth_first_search(visited, image, (x, y-1), cache_path, iteration_depth)
        branches += 1
    if y + 1 < len(visited[0]):
        cache_path, visited, maximum_depth_array[3] = depth_first_search(visited, image, (x, y+1), cache_path, iteration_depth)
        branches += 1
    if x - 1 >= 0 and y - 1 <= 0:
        cache_path, visited, maximum_depth_array[4] = depth_first_search(visited, image, (x-1, y-1), cache_path, iteration_depth)
        branches += 1
    if x + 1 < len(visited) and y + 1 < len(visited[0]):
        cache_path, visited, maximum_depth_array[5] = depth_first_search(visited, image, (x+1, y+1), cache_path, iteration_depth)
        branches += 1
    if x - 1 >= 0 and y + 1 < len(visited[0]):
        cache_path, visited, maximum_depth_array[6] = depth_first_search(visited, image, (x-1, y+1), cache_path, iteration_depth)
        branches += 1
    if x + 1 < len(visited) and y - 1 <= 0:
        cache_path, visited, maximum_depth_array[7] = depth_first_search(visited, image, (x+1, y-1), cache_path, iteration_depth)
        branches += 1
    if branches > 1:
        cache_path.append([int(x), int(y)])
    cache = max(maximum_depth_array)
    if iteration_depth == 1 and cache < 2:
        return path, visited, cache
    path += cache_path
    return path, visited, cache


def convert_image(image, frame_number):
    parsed_json['sizeX'] = len(image[0])
    parsed_json['sizeY'] = len(image)
    emptyImage = np.zeros((len(image), len(image[0]), 3), dtype=np.uint8)
    path = []
    if np.sum(image) > 0:
        drawn_pixels = np.argwhere(image > 0)
        np.random.shuffle(drawn_pixels)
        visited_pixels = np.full((len(image), len(image[0])), False)
        starting_point = None
        while(np.count_nonzero(visited_pixels) != len(drawn_pixels)):
            last_point = starting_point if len(path) == 0 else path[-1]
            starting_point = find_starting_point(drawn_pixels, visited_pixels, last_point)
            path, visited_pixels, _ = depth_first_search(visited_pixels, image, starting_point, path, 0)
        for index in range(1, len(path)):
            cv2.line(emptyImage, (path[index-1][1], path[index-1][0]), (path[index][1], path[index][0]), (255,255,255))
    cv2.imwrite(os.path.join(title, str(frame_number) + ".jpg"), emptyImage)
    parsed_json['frames'].insert(frame_number, path)


def auto_canny(image, sigma=0.33):
    v = np.median(image)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    return edged


frame_number = 0
frames = []
while True:
    ret, frame = cap.read()
    if frame_number % 2 == 0:
        try:
            image = cv2.Canny(frame, 50, 200)
            print('Saved image to stack ' + str(frame_number))
            cv2.imshow("frame", image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cap.release()
                cv2.destroyAllWindows()
                break
            frames.append(image)
        except:
            print('Error')
            break
            cap.release()
            cv2.destroyAllWindows()
    frame_number += 1

frame_index = 0
number_of_threads = 0
threads = []
for frame in frames:
    x = threading.Thread(target=convert_image, args=(frame, frame_index))
    threads.append(x)
    frame_index += 1

while(len(threads) > 0):
    threads_cache = threads[:20]
    for thread in threads_cache:
        print("Taking image from stack")
        thread.start()
    for thread in threads_cache:
        print("Finished")
        thread.join()
    print("Starting next job")
    threads = threads[20:]

with open(title + ".json", 'w') as outfile:
    json.dump(parsed_json, outfile)
