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
path_names = EMGFlow.makePaths()

# Load sample data
EMGFlow.makeSampleData(path_names)

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
EMGFlow.NotchFilterSignals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)

# 2. Apply bandpass filter
EMGFlow.BandpassFilterSignals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)

# 3. Apply smoothing filter
EMGFlow.SmoothFilterSignals(path_names['Bandpass'], path_names['Smooth'], smooth_window, cols)

# 4. Extract features
df = EMGFlow.ExtractFeatures(path_names, sampling_rate, cols)
```

### Working With Individual Files

A simple example outlining EMG preprocessing using a loaded dataframe.

```python
import EMGFlow
import os
import pandas as pd

# Get path dictionary
path_names = EMGFlow.makePaths()

# Load sample data
EMGFlow.makeSampleData(path_names)

# Load dataframe from generated data
sample_data = pd.read_csv(os.path.join(path_names['Raw'], 'sample_data_01.csv'))

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
sample_data = EMGFlow.ApplyNotchFilters(sample_data, cols[0], sampling_rate, notch_vals)
sample_data = EMGFlow.ApplyBandpassFilter(sample_data, cols[0], sampling_rate, band_low, band_high)
sample_data = EMGFlow.ApplyRMSSmooth(sample_data, cols[0], smooth_window)

# Preprocess second column of signals ('EMG_cor')
sample_data = EMGFlow.ApplyNotchFilters(sample_data, cols[1], sampling_rate, notch_vals)
sample_data = EMGFlow.ApplyBandpassFilter(sample_data, cols[1], sampling_rate, band_low, band_high)
sample_data = EMGFlow.ApplyRMSSmooth(sample_data, cols[1], smooth_window)
```

## Advanced Examples

### Custom Filters for Individiual Files

A more advanced example applying conditional filters based on file names.

```python
import EMGFlow

# Get path dictionary
path_names = EMGFlow.makePaths()

# Load sample data
EMGFlow.makeSampleData(path_names)

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
EMGFlow.NotchFilterSignals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)
EMGFlow.NotchFilterSignals(path_names['Notch'], path_names['Notch'], sampling_rate, notch_vals_s, cols, expression=reg_str)
EMGFlow.BandpassFilterSignals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)
EMGFlow.SmoothFilterSignals(path_names['Bandpass'], path_names['Smooth'], smooth_window, cols)

# Extract features
df = EMGFlow.ExtractFeatures(path_names, sampling_rate, cols)
```

### Calling native feature extraction routines

A more advnaced example using custom feature extraction functions.

```python
import EMGFlow
import os
import pandas as pd
import tqdm

# Get path dictionary
path_names = EMGFlow.makePaths()

# Load sample data
EMGFlow.makeSampleData(path_names)

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
EMGFlow.NotchFilterSignals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)
EMGFlow.BandpassFilterSignals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)
EMGFlow.SmoothFilterSignals(path_names['Bandpass'], path_names['Smooth'], smooth_window, cols)

# Map locations of files to process
filedirs_b = EMGFlow.MapFiles(path_names['Bandpass'])
filedirs_s = EMGFlow.MapFiles(path_names['Smooth'])

# List of measures to extract
measure_names = [
  'IEMG',
  'MAV',
  'MMAV1',
  'Spec_Centroid',
  # ... put column names for additional features here
]

# Construct columns for each combination of data file column and features
df_names = ['File_ID']
for col in cols:
    for measure in measure_names:
        df_names.append(col + '_' + measure)

SignalDF = pd.DataFrame(columns=df_names)
filetype = 'csv'

# Extract features
for file in tqdm.tqdm(filedirs_b):
    if (file[-len(filetype):] == filetype):
        data_b = pd.read_csv(filedirs_b[file])
        data_s = pd.read_csv(filedirs_s[file])
		
        File_ID = file
        df_vals = [File_ID]
        
        # Make sure to make the same calculations as in measure_names
        for col in cols:
            IEMG = EMGFlow.CalcIEMG(data_s, col, sampling_rate)
            MAV = EMGFlow.CalcMAV(data_s, col)
            MMAV1 = EMGFlow.CalcMMAV1(data_s, col)
    		# ... calculate additional time-series features here
    
            psd = EMGFlow.EMG2PSD(data_b[col], sampling_rate)
            Spec_Centroid = EMGFlow.CalcSC(psd)
    		# ... calculate additional spectral features here
    		
    		# Create list of measures (should match measure_names)
            col_vals = [
    			IEMG,
    			MAV,
    			MMAV1,
    			Spec_Centroid,
    			# ... put additional features here
    		]
            
            # Combine values into list
            df_vals = df_vals + col_vals
            
		# Append to data frame
        SignalDF.loc[len(SignalDF.index)] = df_vals

# Save results in "Features.csv" file
SignalDF.to_csv(os.path.join(path_names['Feature'], 'Features.csv'), index=False)
```
