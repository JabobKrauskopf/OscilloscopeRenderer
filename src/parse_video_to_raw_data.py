from alive_progress import alive_bar
import cv2
import numpy as np
import pafy
import datetime
import os
import re
import threading
import json
import sys

number_of_threads = 30

url = "https://www.youtube.com/watch?v=VYOjWnS4cMY"
vPafy = pafy.new(url)
video = vPafy.getbest()
title = re.sub(r"\s", "_", video.title)
title = re.sub(r"\"", "", title)

sys.setrecursionlimit(10000)

cap = cv2.VideoCapture(video.url)

startTime = datetime.datetime.now()

parsed_json = {
    "title": title,
    "sizeX": None,
    "sizeY": None,
    "frames": [],
    "length": vPafy.length,
}

if not os.path.exists("json"):
    os.makedirs("json")


def find_starting_point(
    drawn_pixels: np.array, visited_pixels: np.array, last_pixel: np.array
):
    if last_pixel is None:
        return drawn_pixels[0]
    smallest_distance = 1000000000
    smallest_distance_pixel = None

    index = 0
    for pixel in drawn_pixels:
        if not visited_pixels[pixel[0]][pixel[1]]:
            distance = (last_pixel[0] - pixel[0]) ** 2 + (last_pixel[1] - pixel[1]) ** 2
            if distance < smallest_distance:
                smallest_distance = distance
                smallest_distance_pixel = pixel
            if index > 150 and smallest_distance_pixel is not None:
                break
            index += 1
    return smallest_distance_pixel


def depth_first_search(
    visited: np.array,
    image: np.array,
    point: tuple,
    path: list,
    iteration_depth: int,
):
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
        cache_path, visited, maximum_depth_array[0] = depth_first_search(
            visited, image, (x - 1, y), cache_path, iteration_depth
        )
        branches += 1
    if x + 1 < len(visited):
        cache_path, visited, maximum_depth_array[1] = depth_first_search(
            visited, image, (x + 1, y), cache_path, iteration_depth
        )
        branches += 1
    if y - 1 >= 0:
        cache_path, visited, maximum_depth_array[2] = depth_first_search(
            visited, image, (x, y - 1), cache_path, iteration_depth
        )
        branches += 1
    if y + 1 < len(visited[0]):
        cache_path, visited, maximum_depth_array[3] = depth_first_search(
            visited, image, (x, y + 1), cache_path, iteration_depth
        )
        branches += 1
    if x - 1 >= 0 and y - 1 <= 0:
        cache_path, visited, maximum_depth_array[4] = depth_first_search(
            visited, image, (x - 1, y - 1), cache_path, iteration_depth
        )
        branches += 1
    if x + 1 < len(visited) and y + 1 < len(visited[0]):
        cache_path, visited, maximum_depth_array[5] = depth_first_search(
            visited, image, (x + 1, y + 1), cache_path, iteration_depth
        )
        branches += 1
    if x - 1 >= 0 and y + 1 < len(visited[0]):
        cache_path, visited, maximum_depth_array[6] = depth_first_search(
            visited, image, (x - 1, y + 1), cache_path, iteration_depth
        )
        branches += 1
    if x + 1 < len(visited) and y - 1 <= 0:
        cache_path, visited, maximum_depth_array[7] = depth_first_search(
            visited, image, (x + 1, y - 1), cache_path, iteration_depth
        )
        branches += 1
    if branches > 1:
        cache_path.append([int(x), int(y)])
    cache = max(maximum_depth_array)
    if iteration_depth == 1 and cache < 2:
        return path, visited, cache
    path += cache_path
    return path, visited, cache


def convert_image(image, frame_number):
    parsed_json["sizeX"] = len(image[0])
    parsed_json["sizeY"] = len(image)
    path = []
    if np.sum(image) > 0:
        drawn_pixels = np.argwhere(image > 0)
        length = len(drawn_pixels)
        np.random.shuffle(drawn_pixels)
        visited_pixels = np.full((len(image), len(image[0])), False)
        starting_point = None
        while np.count_nonzero(visited_pixels) != length:
            last_point = starting_point if len(path) == 0 else path[-1]
            starting_point = find_starting_point(
                drawn_pixels, visited_pixels, last_point
            )
            path, visited_pixels, _ = depth_first_search(
                visited_pixels, image, tuple(starting_point), path, 0
            )
    parsed_json["frames"].insert(frame_number, path)


frame_number = 0
frames = []
while True:
    ret, frame = cap.read()
    if frame_number % 2 == 0:
        try:
            canny_image = cv2.Canny(frame, 50, 200)
            canny_image = cv2.resize(
                canny_image, (int(360 * (len(canny_image[0]) / len(canny_image))), int(360))
            )
            print("Saved image to stack " + str(frame_number))
            cv2.imshow("frame", canny_image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cap.release()
                cv2.destroyAllWindows()
                break
            frames.append(canny_image)
        except:
            print("Finished saving images")
            cap.release()
            cv2.destroyAllWindows()
            break
    frame_number += 1

frame_index = 0
queued_threads = []
for frame in frames:
    x = threading.Thread(target=convert_image, args=(frame, frame_index))
    queued_threads.append(x)
    frame_index += 1
running_threads = queued_threads[:number_of_threads]
queued_threads = queued_threads[number_of_threads:]
[thread.start() for thread in running_threads]

with alive_bar(len(frames)) as bar:
    while len(running_threads) > 0:
        for thread in running_threads:
            thread.join(0.001)
            if not thread.isAlive():
                bar()
                running_threads.remove(thread)
                if len(queued_threads) > 0:
                    new_thread = queued_threads.pop()
                    new_thread.start()
                    running_threads.append(new_thread)

with open(os.path.join("json", title + ".json"), "w") as outfile:
    json.dump(parsed_json, outfile)
