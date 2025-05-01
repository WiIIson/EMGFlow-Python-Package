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
pathNames = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(pathNames)

# Sampling rate
samplingRate = 2000

# Filter parameters
notchVals = [(50, 5)]
bandLow = 20
bandHigh = 140
smoothWindow = 50

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# 1. Apply notch filters
EMGFlow.notch_filter_signals(pathNames['Raw'], pathNames['Notch'], samplingRate, notchVals, cols)

# 2. Apply bandpass filter
EMGFlow.bandpass_filter_signals(pathNames['Notch'], pathNames['Bandpass'], samplingRate, bandLow, bandHigh, cols)

# 3. Apply smoothing filter
EMGFlow.smooth_filter_signals(pathNames['Bandpass'], pathNames['Smooth'], smoothWindow, cols)

# 4. Extract features
df = EMGFlow.extract_features(pathNames, samplingRate, cols)
```

### Working With Individual Files

A simple example outlining EMG preprocessing using a loaded dataframe.

```python
import EMGFlow
import os
import pandas as pd

# Get path dictionary
pathNames = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(pathNames)

# Load dataframe from generated data
sampleData = pd.read_csv(os.path.join(pathNames['Raw'], 'sample_data_01.csv'))

# Sampling rate
samplingRate = 2000

# Custom filter parameters
notchVals = [(50, 5)]
bandLow = 20
bandHigh = 140
smoothWindow = 50

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# Preprocess first column of signals ('EMG_zyg')
sampleData = EMGFlow.apply_notch_filters(sampleData, cols[0], samplingRate, notchVals)
sampleData = EMGFlow.apply_bandpass_filter(sampleData, cols[0], samplingRate, bandLow, bandHigh)
sampleData = EMGFlow.apply_rms_smooth(sampleData, cols[0], smoothWindow)

# Preprocess second column of signals ('EMG_cor')
sampleData = EMGFlow.apply_notch_filters(sampleData, cols[1], samplingRate, notchVals)
sampleData = EMGFlow.apply_bandpass_filter(sampleData, cols[1], samplingRate, bandLow, bandHigh)
sampleData = EMGFlow.apply_rms_smooth(sampleData, cols[1], smoothWindow)
```

## Advanced Examples

### Custom Filters for Individiual Files

A more advanced example applying conditional filters based on file names.

```python
import EMGFlow

# Get path dictionary
pathNames = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(pathNames)

# Sampling rate
samplingRate = 2000

# Filter parameters for all files
notchVals = [(50, 5)]
bandLow = 20
bandHigh = 140
smoothWindow = 50

# Filter parameters for the "sample_data_01.csv" file
notchValsS = [(45, 1), (60, 5)]
regStr = '^sample_data_01'

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# Preprocess signals
EMGFlow.notch_filter_signals(pathNames['Raw'], pathNames['Notch'], samplingRate, notchVals, cols)
EMGFlow.notch_filter_signals(pathNames['Notch'], pathNames['Notch'], samplingRate, notchValsS, cols, expression=regStr)
EMGFlow.bandpass_filter_signals(pathNames['Notch'], pathNames['Bandpass'], samplingRate, bandLow, bandHigh, cols)
EMGFlow.smooth_filter_signals(pathNames['Bandpass'], pathNames['Smooth'], smoothWindow, cols)

# Extract features
df = EMGFlow.extract_features(pathNames, samplingRate, cols)
```

### Calling native feature extraction routines

A more advnaced example using custom feature extraction functions.

```python
import EMGFlow
import os
import pandas as pd
import tqdm

# Get path dictionary
pathNames = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(pathNames)

# Sampling rate
samplingRate = 2000

# Custom filter parameters
notchVals = [(50, 5)]
bandLow = 20
bandHigh = 140
smoothWindow = 50

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# Preprocess signals
EMGFlow.notch_filter_signals(pathNames['Raw'], pathNames['Notch'], samplingRate, notchVals, cols)
EMGFlow.bandpass_filter_signals(pathNames['Notch'], pathNames['Bandpass'], samplingRate, bandLow, bandHigh, cols)
EMGFlow.smooth_filter_signals(pathNames['Bandpass'], pathNames['Smooth'], smoothWindow, cols)

# Map locations of files to process
filedirsB = EMGFlow.map_files(pathNames['Bandpass'])
filedirsS = EMGFlow.map_files(pathNames['Smooth'])

# List of measures to extract
measureNames = [
  'IEMG',
  'MAV',
  'MMAV1',
  'Spec_Centroid',
  # ... put column names for additional features here
]

# Construct columns for each combination of data file column and features
dfNames = ['File_ID']
for col in cols:
    for measure in measureNames:
        dfNames.append(col + '_' + measure)

SignalDF = pd.DataFrame(columns=dfNames)
filetype = 'csv'

# Extract features
for file in tqdm.tqdm(filedirsB):
    if (file[-len(filetype):] == filetype):
        dataB = pd.read_csv(filedirsB[file])
        dataS = pd.read_csv(filedirsS[file])
		
        fileID = file
        dfVals = [fileID]
        
        # Make sure to make the same calculations as in measure_names
        for col in cols:
            IEMG = EMGFlow.calc_iemg(dataS, col, samplingRate)
            MAV = EMGFlow.calc_mav(dataS, col)
            MMAV1 = EMGFlow.calc_mmav1(dataS, col)
    		# ... calculate additional time-series features here
    
            psd = EMGFlow.emg_to_psd(dataB[col], samplingRate)
            specCentroid = EMGFlow.calc_sc(psd)
    		# ... calculate additional spectral features here
    		
    		# Create list of measures (should match measure_names)
            colVals = [
    			IEMG,
    			MAV,
    			MMAV1,
    			specCentroid,
    			# ... put additional features here
    		]
            
            # Combine values into list
            dfVals = dfVals + colVals
            
		# Append to data frame
        SignalDF.loc[len(SignalDF.index)] = dfVals

# Save results in "Features.csv" file
SignalDF.to_csv(os.path.join(pathNames['Feature'], 'Features.csv'), index=False)
```
