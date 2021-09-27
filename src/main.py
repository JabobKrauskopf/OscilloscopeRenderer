from typing import List, Tuple
import sounddevice as sd
import numpy as np
import datetime

import cv2


def get_adjacent_indices(
    y: int, x: int, ySize: int, xSize: int
) -> List[Tuple[int, int]]:
    cache = []
    if y > 0:
        cache.append((y - 1, x))
    if x > 0:
        cache.append((y, x - 1))
    if y + 1 < ySize:
        cache.append((y + 1, x))
    if x + 1 < xSize:
        cache.append((y, x + 1))
    if y > 0 and x > 0:
        cache.append((y - 1, x - 1))
    if y + 1 < ySize and x + 1 < xSize:
        cache.append((y + 1, x + 1))
    if y > 0 and x + 1 < xSize:
        cache.append((y - 1, x + 1))
    if y + 1 < ySize and x > 0:
        cache.append((y + 1, x - 1))

    return cache


def find_starting_point(image: np.ndarray) -> Tuple[int, int]:
    remaining_points = np.argwhere(image > 0)
    return tuple(remaining_points[np.random.choice(len(remaining_points))])


def depth_first_search(
    image: np.ndarray, point: Tuple[int, int]
) -> Tuple[np.ndarray, np.ndarray]:
    image[point] = 0
    path = [point]
    for index in get_adjacent_indices(*point, *image.shape):
        if image[index] > 0:
            image, cache_path = depth_first_search(image, index)
            path += cache_path

    path.append(point)

    return image, path


def convert_image_to_path(image: np.ndarray) -> List[List[Tuple[int, int]]]:
    cache_path = []
    while np.count_nonzero(image) != 0:
        image, path = depth_first_search(image, find_starting_point(image))
        cache_path += path

    return cache_path


cam = cv2.VideoCapture(0)

resolution = (180, 320)
sample_rate = 192000
fps = 60
samples_per_frame = int(sample_rate / fps)

sd.default.samplerate = sample_rate

cam.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[1])
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[0])

last_time = datetime.datetime.now()

last_path = np.array([(5000,0), (5000,0)])

while cam.isOpened():
    ret, frame = cam.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    nudge = 0.5
    median = max(10, min(245, np.median(gray)))
    lower = int(max(0, (1 - nudge) * median))
    upper = int(min(255, (1 + nudge) * median))
    filtered = cv2.bilateralFilter(gray, 5, 50, 50)
    edged = cv2.Canny(filtered, lower, upper, L2gradient=True)

    cv2.imshow(
        "Webcam", cv2.resize(edged, (1920, 1080), interpolation=cv2.INTER_NEAREST)
    )
    path = convert_image_to_path(edged)

    left, right = zip(*path)
    last_path = path

    samples_this_frame = samples_per_frame * (datetime.datetime.now() - last_time).microseconds
    last_time = datetime.datetime.now()

    if len(left) > samples_per_frame:
        local_left = np.array(left)[:: int(len(left) / samples_per_frame)].astype(
            np.float64
        )
        local_right = np.array(right)[:: int(len(left) / samples_per_frame)].astype(
            np.float64
        )
    else:
        left_cache = [left[0]]
        divident = int(samples_per_frame / len(left))
        for index in range(1, len(left)):
            last_point = left[index - 1]
            distance = left[index] - last_point
            for index2 in range(divident):
                left_cache.append(left[index] + ((distance / divident) * (1 + index2)))
        right_cache = [right[0]]
        for index in range(1, len(right)):
            last_point = right[index - 1]
            distance = right[index] - last_point
            for index2 in range(divident):
                right_cache.append(
                    right[index] + ((distance / divident) * (1 + index2))
                )
        local_left = np.array(left_cache).astype(np.float64)
        local_right = np.array(right_cache).astype(np.float64)

    local_left = local_left - (resolution[0] / 2)
    local_right = local_right - (resolution[1] / 2)
    local_left *= -(32767 * (resolution[0] / resolution[1])) / resolution[0]
    local_right *= 32767 / resolution[1]

    local_left = local_left.astype(np.int16)
    local_right = local_right.astype(np.int16)

    local_left = np.tile(local_left, 15)
    local_right = np.tile(local_right, 15)

    stereo_signal = np.zeros([int(len(local_left)), 2], dtype=np.int16)
    stereo_signal[:, 1] = local_left[:]
    stereo_signal[:, 0] = local_right[:]
    
    sd.play(stereo_signal)

    if cv2.waitKey(1) == ord("q"):
        break
