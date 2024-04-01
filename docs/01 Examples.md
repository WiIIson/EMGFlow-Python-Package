# Examples

---

## Simple Example:

A simple example outlining the four main steps of the EMG processing pipeline.

```python
import EMGFlow.SignalFilterer as ESIG

# Paths for data files
raw_path = '/data/raw/'
notch_path = '/data/notch/'
band_path = '/data/bandpass/'
smooth_path = '/data/smoothed/'
feature_path = '/data/feature/'

# Sampling rate
sampling_rate = 2000

# Filter parameters
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Column to apply to
col = 'col1'

# Signal analysis
ESIG.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, col)
ESIG.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high, col)
ESIG.SmoothFilterSignals(band_path, smooth_path, sampling_rate, smooth_window, col)
ESIG.AnalyzeSignals(band_path, smooth_path, feature_path, sampling_rate, [col])
```

## Advanced Example

A more advanced example applying conditional filters based on file names.

```python
import EMGFlow.SignalFilterer as ESIG

# Paths for data files
raw_path = '/data/raw/'
notch_path = '/data/notch/'
notch_path_s = '/data/notch_s/'
band_path = '/data/bandpass/'
smooth_path = '/data/smoothed/'
feature_path = '/data/feature/'

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

# Column to apply to
col = 'col1'

# Signal analysis
ESIG.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, col, expression=reg_str)
ESIG.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high, col, expression=reg_str)
ESIG.SmoothFilterSignals(band_path, smooth_path, sampling_rate, smooth_window, col, expression=reg_str)
ESIG.AnalyzeSignals(band_path, smooth_path, feature_path, sampling_rate, [col], expression=reg_str)
```

## Advanced Example

A more advnaced example using custom feature extraction functions.

```python
import EMGFlow.SignalFilterer as ESIG
import tqdm

# Paths for data files
raw_path = '/data/raw/'
notch_path = '/data/notch/'
band_path = '/data/bandpass/'
smooth_path = '/data/smoothed/'
feature_path = '/data/feature/'

# Sampling rate
sampling_rate = 2000

# Filter parameters
notch_vals = [(50, 5)]
band_low = 20
band_high = 140
smooth_window = 50

# Column to apply to
col = 'col1'

# Signal analysis
ESIG.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, col)
ESIG.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high, col)
ESIG.SmoothFilterSignals(band_path, smooth_path, sampling_rate, smooth_window, col)

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

for file in tqdm.tqdm(filedirs_b):
	if (file[-len(filetype):] == filetype):
		data_b = pd.read_csv(filedirs_b[file])
		data_s = pd.read_csv(filedirs_s[file])
		# Calculate time-series measures
		File_ID = file
		IEMG = ESIG.CalcIEMG(data_s, col, sampling_rate)
		MAV = ESIG.CalcMAV(data_s, col)
		MMAV = ESIG.CalcMMAV(data_s, col)
		# ...
		# Calculate spectral measures
		psd = ESIG.EMG2PSD(data_b[col], sampling_rate)
		Spec_Centroid = ESIG.CalcSC(psd)
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

# Write to output location
SignalDF.to_csv(feature_path + 'Features.csv', index=False)
```