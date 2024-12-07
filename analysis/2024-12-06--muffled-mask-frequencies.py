#!/usr/bin/env python3

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

tests = [
    ("muffled-comparison-no-mask.wav", "No Mask", "black"),
    ("muffled-comparison-duckbill-n95.wav", "Duckbill N95", "orange"),
    ("muffled-comparison-new-p100.wav", "Respirator with Diaphram", "blue"),
    ("muffled-comparison-traditional-p100.wav", "Respirator no Diaphram", "purple"),
]

sampling_rate = 44100
num_buckets = 10000

# Initial version by Claude
def generate_frequency_plots():
    # Create plot
    plt.figure(figsize=(15, 7))

    plt.tight_layout()
    
    # Reduce frequency resolution
    max_freq = sampling_rate / 2
    freq_bins = np.logspace(0, np.log10(max_freq), num_buckets)

    # Process each WAV file
    for wav_file_path, label, color in tests:
        print(label)
        with open(wav_file_path + ".json") as inf:
            data = json.load(inf)

        frequencies = data["frequencies"]
        magnitudes = data["magnitudes"]

        # Create bucketed frequency representation
        bucketed_magnitudes = np.zeros(num_buckets)

        for j in range(1, len(frequencies)//2):  # Skip DC component
            # Find which bucket this frequency belongs to
            freq_val = np.abs(frequencies[j])
            if freq_val <= max_freq:
                bucket_index = np.digitize(freq_val, freq_bins)
                if bucket_index < num_buckets:
                    bucketed_magnitudes[bucket_index] += magnitudes[j]

        # Apply Savitzky-Golay smoothing filter
        smoothed_magnitudes = savgol_filter(bucketed_magnitudes,
                                            window_length=297,
                                            polyorder=3)

        if False:
            plt.plot(freq_bins, bucketed_magnitudes, label=label, color=color)
        else:
            plt.plot(freq_bins[:len(smoothed_magnitudes)],
                     smoothed_magnitudes, label=label, color=color)

            
    # Finalize plot
    plt.title('Effect of Masks and Respirators on Frequency')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.yscale("log")
    plt.xscale("log")
    plt.xlim(60, 14000)
    plt.ylim(1, 300)
    plt.legend()

    plt.savefig("muffled-mask-comparison-chart-big.png", dpi=180)
    plt.clf()

if __name__ == "__main__":
    generate_frequency_plots()
