import numpy as np
import simpleaudio as sa
import json
import progressbar
import wave
import os

sample_rate = 192000

fps = 30

samples_per_frame = int(sample_rate / fps)

with open('Stuck In the Sound - Let\'s Go [Official Video].json') as json_file:
    data = json.load(json_file)

if not os.path.exists('wav'):
    os.makedirs('wav')

frames = data['frames']

left_audio = np.array([])
right_audio = np.array([])

bar = progressbar.ProgressBar(maxval=len(frames), widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()

for num, frame in enumerate(frames):
    try:
        left, right = zip(*frame)
        if len(left) > samples_per_frame:
            local_left = np.array(left)[::int(len(left) / samples_per_frame)].astype(np.float64)
            local_right = np.array(right)[::int(len(left) / samples_per_frame)].astype(np.float64)
        else:
            left_cache = [left[0]]
            divident = int(samples_per_frame / len(left))
            for index in range(1, len(left)):
                last_point = left[index-1]
                distance = left[index] - last_point
                for index2 in range(divident):
                    left_cache.append(left[index] + ((distance / divident) * (1+index2)))
            right_cache = [right[0]]
            for index in range(1, len(right)):
                last_point = right[index-1]
                distance = right[index] - last_point
                for index2 in range(divident):
                    right_cache.append(right[index] + ((distance / divident) * (1+index2)))
            local_left = np.array(left_cache).astype(np.float64)
            local_right = np.array(right_cache).astype(np.float64)
        local_left = local_left - (data['sizeY'] / 2)
        local_right = local_right - (data['sizeX'] / 2)
        local_left *= -(32767 * (data['sizeY'] / data['sizeX'])) / data['sizeY']
        local_right *= 32767 / data['sizeX']
        left_audio = np.append(left_audio, local_left)
        right_audio = np.append(right_audio, local_right)
    except ValueError:
        pass
    bar.update(num)
bar.finish()

left_audio = left_audio.astype(np.int16)
right_audio = right_audio.astype(np.int16)

stereo_signal = np.zeros([int(len(left_audio)), 2], dtype=np.int16)
stereo_signal[:, 1] = left_audio[:]
stereo_signal[:, 0] = right_audio[:]

obj = wave.open(os.path.join("wav", str(data['title']) + ".wav"), 'w')
obj.setnchannels(2)
obj.setsampwidth(2)
obj.setframerate(sample_rate)
obj.writeframesraw(stereo_signal)
obj.close()
