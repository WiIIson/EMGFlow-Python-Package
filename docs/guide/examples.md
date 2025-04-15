---
outline: deep
---

# Examples

This page demonstrates how to use EMGFlow with simple and more advanced examples.

## Simple Examples

The simple examples can run by copying and pasting the code into a Python environment. The only requirement is for the EMGFlow package to be installed

### Using Custom Filter Parameters

A simple example outlining EMG preprocessing and feature extraction using manual parameter selection.

```python
import EMGFlow

# Load sample data
EMGFlow.make_sample_data()

# Paths for data files
path_names = EMGFlow.make_path_dict()

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

### Working with individual files

A simple example outlining EMG preprocessing using a loaded dataframe.

```python
import EMGFlow

# Load built-in dataframe
sample_data = EMGFlow.sample_data

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

### Preprocessing and Plotting Pipeline

A simple example outlining EMG preprocessing and plotting.

```python
import EMGFlow

# Load sample data
EMGFlow.make_sample_data()

# Set sampling rate
sampling_rate = 2000

# Load path dictionary
path_names = EMGFlow.make_path_dict()

# Clean data
EMGFlow.CleanSignals(path_names)

# Plot data on the "EMG_zyg" column
EMGFlow.GenPlotDash(path_names, 'EMG_zyg', 'mV')
```

## Advanced examples

The advanced examples can ran by copying and pasting the code into a Python environment.

In addition, they require having a local "data" folder, with "raw", "notch", "notch_s", "bandpass", "smoothed" and "feature" subfolders. The "raw" subfolder is required to have one or more signal CSV files inside.

The `cols` parameter may need to be modified to contain some of the column names of the signal CSV in the "raw" subfolder.

They serve more as a template of how analysis can be done, to be replicated with your own data.

### Custom filters for individiual files

A more advanced example applying conditional filters based on file names.

```python
import EMGFlow

# Paths for data files
raw_path = 'data/raw'
notch_path = 'data/notch'
notch_path_s = 'data/notch_s'
band_path = 'data/bandpass'
smooth_path = 'data/smoothed'
feature_path = 'data/feature'

path_names = {
	'Raw': raw_path,
	'Notch': notch_path_s, # Use the notch path with all filters applied
	'Bandpass': band_path,
	'Smooth': smooth_path,
	'Feature': feature_path
}

# Sampling rate
sampling_rate = 2000

# Filter parameters for all files
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Filter parameters for files that start with "08" or "11"
notch_vals_s = [(45, 1), (60, 5)]
reg_str = '^(08|11)'

# Columns containing data for preprocessing
cols = ['col1', 'col2']

# Preprocess signals
EMGFlow.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols)
EMGFlow.NotchFilterSignals(notch_path, notch_path_s, sampling_rate, notch_vals_s, cols, expression=reg_str, exp_copy=True)
EMGFlow.BandpassFilterSignals(notch_path_s, band_path, sampling_rate, band_low, band_high, cols)
EMGFlow.SmoothFilterSignals(band_path, smooth_path, smooth_window, cols)

# Extract features and save results in "Features.csv" in feature_path
df = EMGFlow.ExtractFeatures(path_names, sampling_rate, cols)
```

### Calling native feature extraction routines

A more advnaced example using custom feature extraction functions.

This example is intended to be used as a template for extracting only specific features from emotional data. It makes use of the `tqdm` library, which helps visualize loops for lengthy processes, such as large EMG processing workflows.

```python
import EMGFlow
import tqdm

# Paths for data files
raw_path = 'data/raw'
notch_path = 'data/notch'
band_path = 'data/bandpass'
smooth_path = 'data/smoothed'
feature_path = 'data/feature'

# Sampling rate
sampling_rate = 2000

# Filter parameters
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Columns containing data for preprocessing
cols = ['col1', 'col2']

# Preprocess signals
EMGFlow.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols)
EMGFlow.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high, cols)
EMGFlow.SmoothFilterSignals(band_path, smooth_path, smooth_window, cols)

# Custom analysis function code below:
filedirs_b = MapFiles(band_path)
filedirs_s = MapFiles(smooth_path)

measure_names = [
  'File_ID', # File ID column is necessary
  'IEMG',
  'MAV',
  'MMAV',
  'Spec_Centroid',
  # ... put column names for additional features here
]

SignalDF = pd.DataFrame(columns=measure_names)
filetype = 'csv'

# Extract features
for file in tqdm.tqdm(filedirs_b):
	if (file[-len(filetype):] == filetype):
		data_b = pd.read_csv(filedirs_b[file])
		data_s = pd.read_csv(filedirs_s[file])
		
		File_ID = file
		IEMG = EMGFlow.CalcIEMG(data_s, col, sampling_rate)
		MAV = EMGFlow.CalcMAV(data_s, col)
		MMAV = EMGFlow.CalcMMAV(data_s, col)
		# ... calculate additional time-series features here

		psd = EMGFlow.EMG2PSD(data_b[col], sampling_rate)
		Spec_Centroid = EMGFlow.CalcSC(psd)
		# ... calculate additional spectral features here
		
		# Create list of measures (should match measure_names)
		col_vals = [
			File_ID,
			IEMG,
			MAV,
			MMAV,
			Spec_Centroid,
			# ... put additional features here
		]
		
		# Append to data frame
		SignalDF.loc[len(SIgnalDF.inddex)] = df_vals

# Save results in "Features.csv" file
SignalDF.to_csv(feature_path + 'Features.csv', index=False)
```
