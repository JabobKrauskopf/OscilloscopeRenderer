import numpy as np
import simpleaudio as sa
import json
import progressbar
import wave

sample_rate = 192000

with open('Webcam.json') as json_file:
    data = json.load(json_file)

frames = data['frames']

left_audio = np.array([])
right_audio = np.array([])

bar = progressbar.ProgressBar(maxval=len(frames), widgets=[progressbar.Bar('=',
                              '[', ']'), ' ', progressbar.Percentage()])
bar.start()

for num, frame in enumerate(frames):
    try:
        left, right = zip(*frame)
        local_left = np.array(left)[::3].astype(np.float64)
        local_left = local_left - (data['sizeY'] / 2)
        local_right = np.array(right))[::3].astype(np.float64)
        local_right = local_right - (data['sizeX'] / 2)
        local_left *= -18431 / (1 * np.max(np.abs(local_left)))
        local_right *= 32767 / (1 * np.max(np.abs(local_right)))
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

play_obj = sa.play_buffer(stereo_signal, 2, 2, sample_rate)

play_obj.wait_done()

obj = wave.open(str(data['title']) + ".wav", 'w')
obj.setnchannels(2)
obj.setsampwidth(2)
obj.setframerate(sample_rate)
obj.writeframesraw(stereo_signal)
obj.close()
