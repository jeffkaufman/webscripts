#!/usr/bin/env python3

import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile


wav_file_path, = sys.argv[1:]

print("Processing", wav_file_path)

sampling_rate, audio_data = wavfile.read(wav_file_path)

print("  sampling_rate:", sampling_rate)

# If stereo, take the first channel
if len(audio_data.shape) > 1:
    audio_data = audio_data[:, 0]

print("  starting fft")
    
# Perform Fast Fourier Transform
fft_result = np.fft.fft(audio_data)

print("  calculating frequencies")

# Calculate the frequencies
n = len(audio_data)
frequencies = np.fft.fftfreq(n, d=1/sampling_rate)

print("  calculating magnitudes")


# Calculate magnitude spectrum (take absolute value and normalize)
magnitudes = np.abs(fft_result)

print("  normalizing magnitudes")

magnitudes = magnitudes / n  # Normalize

with open(wav_file_path + ".json", "w") as outf:
    json.dump({
        "magnitudes": list(magnitudes),
        "frequencies": list(frequencies),
    }, outf)
