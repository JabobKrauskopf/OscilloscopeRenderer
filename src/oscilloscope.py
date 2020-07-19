import numpy as np
import simpleaudio as sa

A_freq = 60
Csh_freq = A_freq * 2 ** (4 / 12)

E_freq = A_freq * 2 ** (7 / 12)

ka_freq = A_freq * 2 ** (1 / 1)

sample_rate = 44100
T = 360
t = np.linspace(0, T, int(T * sample_rate), False)

A_note = np.sin(A_freq * t * 2 * np.pi)
Csh_note = np.sin(Csh_freq * t * 2 * np.pi)
E_note = np.sin(E_freq * t * 2 * np.pi)
ka_note = np.cos(ka_freq * t * 2 * np.pi)

right_audio = A_note
left_audio = ka_note

# right_audio = []
# for i in range(len(left_audio)):
#     right_audio.append(float(i) / len(left_audio))

# right_audio = np.array(right_audio)

# left_audio = Csh_note
# right_audio = E_note

# left_audio = A_note
# right_audio = Csh_note

# right_audio = A_note
# left_audio = ka_note

print(left_audio)

left_audio *= 32767 / 1 * np.max(np.abs(left_audio))
right_audio *= 32767 / 1 * np.max(np.abs(right_audio))

print(left_audio)

left_audio = left_audio.astype(np.int16)
right_audio = right_audio.astype(np.int16)

print(left_audio)

stereo_signal = np.zeros([int(sample_rate*T), 2], dtype=np.int16)
stereo_signal[:, 1] = left_audio[:]
stereo_signal[:, 0] = right_audio[:]
print(stereo_signal)

play_obj = sa.play_buffer(stereo_signal, 2, 2, sample_rate)

play_obj.wait_done()
