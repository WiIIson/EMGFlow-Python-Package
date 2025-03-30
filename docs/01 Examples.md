# Examples

These examples can be ran by copying and pasting them into a python environment and running them. The only dependency will be that EMGFlow is installed.

The first example loads the example dataset included in the package. Additional examples are included, but use imaginary data stored in declared file paths. To follow along with these examples, you need to crate these folders relative to where your test file is running, and put test data in the `data/raw` folder. The test functions will generate the data in the rest of the folders as the file runs. Additionally, the data is expected to have a `col1` and `col3` column of data.

---

## Simple Example (loading sample data):

A simple example outlining the four main steps of the EMG processing pipeline.

```python
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

# Preprocess first column of signals ('EMG_zyg')
sample_data = EMGFlow.ApplyNotchFilters(sample_data, cols[0], sampling_rate, notch_vals)
sample_data = EMGFlow.ApplyBandpassFilter(sample_data, cols[0], sampling_rate, band_low, band_high)
sample_data = EMGFlow.ApplyRMSSmooth(sample_data, cols[0], smooth_window)

# Preprocess second column of signals ('EMG_cor')
sample_data = EMGFlow.ApplyNotchFilters(sample_data, cols[1], sampling_rate, notch_vals)
sample_data = EMGFlow.ApplyBandpassFilter(sample_data, cols[1], sampling_rate, band_low, band_high)
sample_data = EMGFlow.ApplyRMSSmooth(sample_data, cols[1], smooth_window)
```

---

## Simple Example (loading existing data):

A simple example outlining the four main steps of the EMG processing pipeline.

```python
import EMGFlow

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
cols = ['col1', 'col3']

# Preprocess signals
EMGFlow.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols)
EMGFlow.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high, cols)
EMGFlow.SmoothFilterSignals(band_path, smooth_path, smooth_window, cols)

# Extract features and save results in "Features.csv" in feature_path
df = EMGFlow.ExtractFeatures(band_path, smooth_path, feature_path, sampling_rate, cols)
```

## Advanced Example (loading existing data):

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
cols = ['col1', 'col3']

# Preprocess signals
EMGFlow.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols)
EMGFlow.NotchFilterSignals(notch_path, notch_path_s, sampling_rate, notch_vals_s, cols, expression=reg_str, exp_copy=True)
EMGFlow.BandpassFilterSignals(notch_path_s, band_path, sampling_rate, band_low, band_high, cols)
EMGFlow.SmoothFilterSignals(band_path, smooth_path, smooth_window, cols)

# Extract features and save results in "Features.csv" in feature_path
df = EMGFlow.ExtractFeatures(band_path, smooth_path, feature_path, sampling_rate, cols)
```

## Advanced Example (loading existing data):

A more advnaced example using custom feature extraction functions.

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
cols = ['col1', 'col3']

# Preprocess signals
EMGFlow.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols)
EMGFlow.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high, cols)
EMGFlow.SmoothFilterSignals(band_path, smooth_path, smooth_window, cols)

# ---

# Custom analysis function code below:
filedirs_b = MapFiles(band_path)
filedirs_s = MapFiles(smooth_path)

measure_names = [
	'File_ID', # File ID column is necessary
	'IEMG',
	'MAV',
	'MMAV',
	'Spec_Centroid',
	# ...
	# Put column names for features here
]

SignalDF = pd.DataFrame(columns=measure_names)
filetype = 'csv'

# Extract features
for file in tqdm.tqdm(filedirs_b):
	if (file[-len(filetype):] == filetype):
		data_b = pd.read_csv(filedirs_b[file])
		data_s = pd.read_csv(filedirs_s[file])
		# Calculate time-series measures
		File_ID = file
		IEMG = EMGFlow.CalcIEMG(data_s, col, sampling_rate)
		MAV = EMGFlow.CalcMAV(data_s, col)
		MMAV = EMGFlow.CalcMMAV(data_s, col)
		# ...
		# Calculate spectral measures
		psd = EMGFlow.EMG2PSD(data_b[col], sampling_rate)
		Spec_Centroid = EMGFlow.CalcSC(psd)
		# ...
		
		# Create list of measures
		col_vals = [
			File_ID,
			IEMG,
			MAV,
			MMAV,
			Spec_Centroid,
			# ...
		]
		
		# Append to data frame
		SignalDF.loc[len(SIgnalDF.inddex)] = df_vals

# Save results in "Features.csv" file
SignalDF.to_csv(feature_path + 'Features.csv', index=False)
```