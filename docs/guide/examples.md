---
outline: deep
---

# Examples

This page demonstrates how to use EMGFlow with simple and more advanced examples. The examples can be ran by copying and pasting the code into a Python environment, ensuring the appropriate packages have been installed.

## Simple Examples

### Using Custom Filter Parameters

A simple example outlining EMG preprocessing and feature extraction using manual parameter selection.

```python
import EMGFlow

# Get path dictionary
path_names = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(path_names)

# Sampling rate
sampling_rate = 2000

# Filter parameters
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# 1. Apply notch filters
EMGFlow.notch_filter_signals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)

# 2. Apply bandpass filter
EMGFlow.bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)

# 3. Apply smoothing filter
EMGFlow.smooth_filter_signals(path_names['Bandpass'], path_names['Smooth'], sampling_rate, smooth_window, cols)

# 4. Apply artefact screening
EMGFlow.screen_artefact_signals(path_names['Smooth'], path_names['Filled'], sampling_rate, cols=cols)

# 5. Fill missing data
EMGFlow.fill_missing_signals(path_names['Filled'], path_names['Filled'], sampling_rate, cols=cols)

# 4. Extract features
df = EMGFlow.extract_features(path_names, sampling_rate, cols)
```

### Using Your Own Data Paths

A simple example constructing a custom `path_names` dictionary for predefined data paths.

```python
import EMGFlow as ef

# PeakAffectDS data
path_names = {
    'Raw': 'E:\\UOIT\\UOIT-Thesis\\Other_Work\\Data\\01_Raw',
    'Notch': 'E:\\UOIT\\UOIT-Thesis\\Other_Work\\Data\\02_Notch',
    'Bandpass': 'E:\\UOIT\\UOIT-Thesis\\Other_Work\\Data\\03_Bandpass',
    'Smooth': 'E:\\UOIT\\UOIT-Thesis\\Other_Work\\Data\\04_Smooth'
}

# Preprocess signals
ef.clean_signals(path_names, sampling_rate=2000)

# Plot data on the "EMG_zyg" column
ef.plot_dashboard(path_names, 'EMG_zyg', 'mV')

# Extract features and save results in "Features.csv" in feature_path
df = ef.extract_features(path_names, sampling_rate=2000)
```

### Working With Individual Files

A simple example outlining EMG preprocessing using a loaded dataframe.

```python
import EMGFlow
import os
import pandas as pd

# Get path dictionary
path_names = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(path_names)

# Load dataframe from generated data
sampleData = pd.read_csv(os.path.join(path_names['Raw'], '01', 'sample_data_01.csv'))

# Sampling rate
sampling_rate = 2000

# Custom filter parameters
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# Preprocess first column of signals ('EMG_zyg')
sampleData = EMGFlow.apply_notch_filters(sampleData, cols[0], sampling_rate, notch_vals)
sampleData = EMGFlow.apply_bandpass_filter(sampleData, cols[0], sampling_rate, band_low, band_high)
sampleData = EMGFlow.apply_rms_smooth(sampleData, cols[0], smooth_window)

# Preprocess second column of signals ('EMG_cor')
sampleData = EMGFlow.apply_notch_filters(sampleData, cols[1], sampling_rate, notch_vals)
sampleData = EMGFlow.apply_bandpass_filter(sampleData, cols[1], sampling_rate, band_low, band_high)
sampleData = EMGFlow.apply_rms_smooth(sampleData, cols[1], smooth_window)
```

## Advanced Examples

### Custom Filters for Individiual Files

A more advanced example applying conditional filters based on file names.

```python
import EMGFlow

# Get path dictionary
path_names = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(path_names)

# Sampling rate
sampling_rate = 2000

# Filter parameters for all files
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Filter parameters for the "sample_data_01.csv" file
notch_vals_s = [(45, 1), (60, 5)]
reg_str = '^sample_data_01'

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# Preprocess signals
EMGFlow.notch_filter_signals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)
EMGFlow.notch_filter_signals(path_names['Notch'], path_names['Notch'], sampling_rate, notch_vals_s, cols, expression=reg_str)
EMGFlow.bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)
EMGFlow.smooth_filter_signals(path_names['Bandpass'], path_names['Smooth'], smooth_window, cols)

# Extract features
df = EMGFlow.extract_features(path_names, sampling_rate, cols)
```

### Calling native feature extraction routines

A more advnaced example using custom feature extraction functions.

```python
import EMGFlow
import os
import pandas as pd
import tqdm

# Get path dictionary
path_names = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(path_names)

# Sampling rate
sampling_rate = 2000

# Custom filter parameters
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# Preprocess signals
EMGFlow.notch_filter_signals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)
EMGFlow.bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)
EMGFlow.smooth_filter_signals(path_names['Bandpass'], path_names['Smooth'], smooth_window, cols)

# Map locations of files to process
file_dirs_b = EMGFlow.map_files(path_names['Bandpass'])
file_dirs_s = EMGFlow.map_files(path_names['Smooth'])

# List of measures to extract
measureNames = [
  'IEMG',
  'MAV',
  'MMAV1',
  'Spec_Centroid',
  # ... put column names for additional features here
]

# Construct columns for each combination of data file column and features
df_names = ['File_ID']
for col in cols:
    for measure in measureNames:
        df_names.append(col + '_' + measure)

SignalDF = pd.DataFrame(columns=df_names)
filetype = 'csv'

# Extract features
for file in tqdm.tqdm(file_dirs_b):
    if (file[-len(filetype):] == filetype):
        data_B = pd.read_csv(file_dirs_b[file])
        data_S = pd.read_csv(file_dirs_s[file])

        df_vals = [file]
        
        # Make sure to make the same calculations as in measure_names
        for col in cols:
            IEMG = EMGFlow.calc_iemg(data_S, col, sampling_rate)
            MAV = EMGFlow.calc_mav(data_S, col)
            MMAV1 = EMGFlow.calc_mmav1(data_S, col)
    		# ... calculate additional time-series features here
    
            psd = EMGFlow.emg_to_psd(data_B[col], sampling_rate)
            specCentroid = EMGFlow.calc_sc(psd)
    		# ... calculate additional spectral features here
    		
    		# Create list of measures (should match measure_names)
            col_vals = [
    			IEMG,
    			MAV,
    			MMAV1,
    			specCentroid,
    			# ... put additional features here
    		]
            
            # Combine values into list
            df_vals = df_vals + col_vals
            
		# Append to data frame
        SignalDF.loc[len(SignalDF.index)] = df_vals

# Save results in "Features.csv" file
SignalDF.to_csv(os.path.join(path_names['Feature'], 'Features.csv'), index=False)
```
