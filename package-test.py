import EMGFlow
import pandas as pd

# Verify that the examples work

import EMGFlow

# Data
sample_data = EMGFlow.sample_data

# Sampling rate
sampling_rate = 2000

# Filter parameters
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

print(sample_data.head())

# Preprocess signals
sample_data = EMGFlow.ApplyNotchFilters(sample_data, cols[0], sampling_rate, notch_vals)
sample_data = EMGFlow.ApplyNotchFilters(sample_data, cols[1], sampling_rate, notch_vals)
sample_data = EMGFlow.ApplyBandpassFilter(sample_data, cols[0], sampling_rate, band_low, band_high)
sample_data = EMGFlow.ApplyBandpassFilter(sample_data, cols[1], sampling_rate, band_low, band_high)
sample_data = EMGFlow.ApplyRMSSmooth(sample_data, cols[0], smooth_window)
sample_data = EMGFlow.ApplyRMSSmooth(sample_data, cols[1], smooth_window)

print(sample_data.head())