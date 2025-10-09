---
outline: deep
---

# Examples

This page demonstrates how to use EMGFlow with simple and more advanced examples. The examples can be ran by copying and pasting the code into a Python environment, ensuring the appropriate packages have been installed.

## Simple Examples

### Standard Preprocessing Workflow

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
passband_edges = (20, 140)
smooth_window = 50

# Columns containing data for preprocessing
column_names = ['EMG_zyg', 'EMG_cor']

# 1. Apply notch filters
EMGFlow.notch_filter_signals(path_names['Raw'], path_names['Notch'], column_names, sampling_rate, notch_vals)

# 2. Apply bandpass filter
EMGFlow.bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], column_names, sampling_rate, passband_edges)

# 3. Apply full wave rectifier
EMGFlow.rectify_signals(path_names['Bandpass'], path_names['FWR'])

# 4. Apply artefact screening
EMGFlow.screen_artefact_signals(path_names['FWR'], path_names['Screened'], column_names, sampling_rate)

# 5. Fill missing data
EMGFlow.fill_missing_signals(path_names['Screened'], path_names['Filled'], column_names, sampling_rate)

# 6. Apply smoothing filter
EMGFlow.smooth_signals(path_names['Filled'], path_names['Smooth'], column_names, sampling_rate, window_ms=smooth_window)

# 7. Extract features
df = EMGFlow.extract_features(path_names, column_names, sampling_rate)
```

### Using Your Own Data Paths

A simple example constructing a custom `path_names` dictionary for predefined data paths.

```python
import os
import EMGFlow as ef

# Create sample data
path_names = ef.make_paths()
ef.make_sample_data(path_names)

# Define custom path locations
root = os.getcwd()
path_names = {
    'Raw': os.path.join(root, 'Data', '1_raw'),
    'Notch': os.path.join(root, 'Data', '2_notch'),
    'Bandpass': os.path.join(root, 'Data', '3_bandpass'),
    'FWR': os.path.join(root, 'Data', '4_fwr'),
    'Feature': os.path.join(root, 'Data', '8_feature')
}

# Preprocess signals
ef.clean_signals(path_names, sampling_rate=2000, do_fill=False, do_smooth=False)

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
import numpy as np

# Get path dictionary
path_names = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(path_names)

# Load dataframe from generated data
root = os.getcwd()
sample_data = pd.read_csv(os.path.join(root, 'Data', '1_raw', '01', 'sample_data_01.csv'))

# Sampling rate
sampling_rate = 2000

# Custom filter parameters
notch_vals = [(50, 5)]
passband_edges = (20, 140)
smooth_window = 50

# Columns containing data for preprocessing
column_names = ['EMG_zyg', 'EMG_cor']

# Preprocess first column of signals ('EMG_zyg')
sample_data = EMGFlow.apply_notch_filters(sample_data, column_names[0], sampling_rate, notch_vals)
sample_data = EMGFlow.apply_bandpass_filter(sample_data, column_names[0], sampling_rate, passband_edges)
sample_data[column_names[0]] = np.abs(sample_data[column_names[0]])

# Preprocess second column of signals ('EMG_cor')
sample_data = EMGFlow.apply_notch_filters(sample_data, column_names[1], sampling_rate, notch_vals)
sample_data = EMGFlow.apply_bandpass_filter(sample_data, column_names[1], sampling_rate, passband_edges)
sample_data[column_names[1]] = np.abs(sample_data[column_names[1]])
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
passband_edges = (20, 140)
smooth_window = 50

# Filter parameters for the "sample_data_01.csv" file
notch_vals_s = [(45, 1), (60, 5)]
expression = '^01'

# Columns containing data for preprocessing
column_names = ['EMG_zyg', 'EMG_cor']

# Preprocess signals
EMGFlow.notch_filter_signals(path_names['Raw'], path_names['Notch'], column_names, sampling_rate, notch_vals)
EMGFlow.notch_filter_signals(path_names['Notch'], path_names['Notch'], column_names, sampling_rate, notch_vals_s, expression=expression)
EMGFlow.bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], column_names, sampling_rate, passband_edges)
EMGFlow.rectify_signals(path_names['Bandpass'], path_names['FWR'], column_names)

# Extract features
df = EMGFlow.extract_features(path_names, column_names, sampling_rate)
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
passband_edges = (20, 140)
smooth_window = 50

# Columns containing data for preprocessing
column_names = ['EMG_zyg', 'EMG_cor']

# Preprocess signals
EMGFlow.notch_filter_signals(path_names['Raw'], path_names['Notch'], column_names, sampling_rate, notch_vals)
EMGFlow.bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], column_names, sampling_rate, passband_edges)
EMGFlow.rectify_signals(path_names['Bandpass'], path_names['Smooth'], column_names)

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
for col in column_names:
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
        for col in column_names:
            IEMG = EMGFlow.calc_iemg(data_S, col, sampling_rate)
            MAV = EMGFlow.calc_mav(data_S, col)
            MMAV1 = EMGFlow.calc_mmav1(data_S, col)
    		# ... calculate additional time-series features here
    
            psd = EMGFlow.emg_to_psd(data_B, col, sampling_rate)
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
