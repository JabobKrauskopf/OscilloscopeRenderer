from typing import List, Tuple
import numpy as np
import cv2

cam = cv2.VideoCapture(0)


def get_adjacent_indices(y: int, x: int, ySize: int, xSize: int) -> List[Tuple[int, int]]:
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


def depth_first_search(image: np.ndarray, point: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray]:
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
        cache_path += [path]

    return cache_path


while True:
    ret, frame = cam.read()
    resized_image = cv2.resize(
        frame,
        (int(180 * (len(frame[0]) / len(frame))), int(180)),
    )

    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)

    nudge = 0.5
    median = max(10, min(245, np.median(gray)))
    lower = int(max(0, (1 - nudge) * median))
    upper = int(min(255, (1 + nudge) * median))
    filtered = cv2.bilateralFilter(gray, 5, 50, 50)
    edged = cv2.Canny(filtered, lower, upper, L2gradient=True)

    cv2.imshow("Webcam", cv2.resize(edged, (1920, 1080), interpolation=cv2.INTER_NEAREST))
    convert_image_to_path(edged)

    if cv2.waitKey(1) == ord('q'):
        break
