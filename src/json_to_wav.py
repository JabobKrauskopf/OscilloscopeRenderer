from alive_progress import alive_bar
import numpy as np
import json
import wave
import os
import sys
import getopt


def usage():
    print("Usage: oscilloscope.py [OPTIONS]")
    print()
    print("Options:")
    print(
        " --file=<file_path>              REQUIRED: Full path to the input file of the script."
    )
    print(
        " --fps=<fps>                     OPTIONAL: framerate the video will be rendered at."
    )
    print(
        " --rep=<repititions>             OPTIONAL: Repetitions of the Video."
    )
    print(
        " --reverse                       OPTIONAL: In conjunction to --rep"
    )
    print(
        " --rep=<repititions>             OPTIONAL: Repetitions of the Video."
    )
    print(
        " -a, --auto                      OPTIONAL: Automatically detects the framerate."
    )
    print(
        " --sample_rate=<sample_rate>     OPTIONAL: Sample_rate the video will be rendered with."
    )
    print(" -h, --help                    OPTIONAL: Show tis message and exit.")


sample_rate = 192000

fps = 60

input_file = ""

repetition = 1

reverse = False

try:
    opts, args = getopt.getopt(
        sys.argv[1:], "ha", ["file=", "fps=", "rep=", "sample_rate=", "reverse", "help", "auto"]
    )
    found_file = False
    already_set = False
    for opt, arg in opts:
        if opt == "--file":
            input_file = arg
            found_file = True
        elif opt == "--sample_rate":
            sample_rate = int(arg)
        elif opt == "--fps" and not already_set:
            fps = int(arg)
            already_set = True
        elif opt == "--rep":
            repetition = int(arg)
        elif opt in ["-a", "--auto"] and not already_set:
            fps = 30
            already_set = True
        elif opt == "--reverse":
            reverse = True
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
    if not found_file:
        print("Argument --file=<file_path> not found")
        usage()
        sys.exit(2)
except getopt.GetoptError as e:
    print(e)
    print("oscilloscope.py [OPTIONS]")
    sys.exit(2)

samples_per_frame = int(sample_rate / fps)

with open(input_file) as json_file:
    data = json.load(json_file)

if not os.path.exists("wav"):
    os.makedirs("wav")

frames = data["frames"]

left_audio = np.array([])
right_audio = np.array([])

with alive_bar(len(frames)) as bar:
    for num, frame in enumerate(frames):
        try:
            left, right = zip(*frame)
            if len(left) > samples_per_frame:
                local_left = np.array(left)[
                    :: int(len(left) / samples_per_frame)
                ].astype(np.float64)
                local_right = np.array(right)[
                    :: int(len(left) / samples_per_frame)
                ].astype(np.float64)
            else:
                left_cache = [left[0]]
                divident = int(samples_per_frame / len(left))
                for index in range(1, len(left)):
                    last_point = left[index - 1]
                    distance = left[index] - last_point
                    for index2 in range(divident):
                        left_cache.append(
                            left[index] + ((distance / divident) * (1 + index2))
                        )
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
            local_left = local_left - (data["sizeY"] / 2)
            local_right = local_right - (data["sizeX"] / 2)
            local_left *= -(32767 * (data["sizeY"] / data["sizeX"])) / data["sizeY"]
            local_right *= 32767 / data["sizeX"]
            left_audio = np.append(left_audio, local_left)
            right_audio = np.append(right_audio, local_right)
        except ValueError:
            pass
        bar()

left_audio = left_audio.astype(np.int16)
right_audio = right_audio.astype(np.int16)

if repetition > 1:
    if reverse:
        left_audio = np.concatenate([left_audio, left_audio[::-1]])
        right_audio = np.concatenate([right_audio, right_audio[::-1]])
    left_audio = np.tile(left_audio, repetition)
    right_audio = np.tile(right_audio, repetition)

stereo_signal = np.zeros([int(len(left_audio)), 2], dtype=np.int16)
stereo_signal[:, 1] = left_audio[:]
stereo_signal[:, 0] = right_audio[:]

obj = wave.open(os.path.join("wav", str(data["title"]) + ".wav"), "w")
obj.setnchannels(2)
obj.setsampwidth(2)
obj.setframerate(sample_rate)
obj.writeframesraw(stereo_signal)
obj.close()
