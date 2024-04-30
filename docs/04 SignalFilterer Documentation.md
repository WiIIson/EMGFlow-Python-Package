# `SignalFilterer` Module Filtering Documentation

---

## `EMG2PSD`

**Description**

Creates a PSD (power spectrum density) of a Signal. Uses the Welch method, meaning it can be used as a Long Term Average Spectrum (LTAS).

```python
EMG2PSD(Signal, sr=1000, normalize=True)
```

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.`

`sr`: int/float (1000)
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`normalize`: bool (True)
- Normalizes the result of the PSD by its maximum strength.

**Returns**

`EMG2PSD`: pd.DataFrame
- Returns a dictionary of frequencies and related strengths with the columns "Frequency" and "Power".

**Example**

```python
sr = 2000
PSD = EMGFlow.EMG2PSD(SignalDF, sr)
```

---

## `MapFiles`

**Description**

`MapFiles` generates a dictionary of file name and location keys/values from a folder and its subfolders.

```python
MapFiles(in_path, file_ext='csv', expression=None)
```

**Parameters**

`in_path`: str
- String filepath to a directory containing Signal files.

`file_ext`: str ("csv")
- String extension of the files to read. The default is `'csv'`.

`expression`: str (None)
- Optional regular expression. If provided, only maps files whose names match the regular expression matches.

**Returns**

`MapFiles`: dict
- Returns a dictionary of file names and locations keys/values.

**Example**

```python
# Map all csv files in 'dataFiles' folder and subfolders
file_loc1 = EMGFlow.MapFiles('/data/')

# Map all csv files in 'dataFiles' folder and subfolders
# that start with 'DATA_'
file_loc2 = EMGFlow.MapFiles('/data/', expression='^DATA_')
```

---

## `ConvertMapFiles`

**Description**

A more advanced version of `MapFiles` that can coerce other data types into the `MapFiles` format.

If provided a dictionary (assumed to be a file location map), it will return it, filtered by `expression` if provided)

```python
ConvertMapFiles(fileObj, file_ext='csv', experssion=None)
```

**Parameters**

`fileObj`: str, dict
- Any filepath data type supported by the function. Supported data types are: string filepath, or filepath dictionary.

`file_ext`: str ("csv")
- Extension of the files to read. The default is 'csv'.

`expression`: str (None)
- Optional regular expression. If provided, only maps files whose names match the regular expression matches.

**Returns**

`ConvertMapFiles`: dict
- Returns a dictionary of file names and locations keys/values.

**Error**

Raises an error if provided an unsupported file type for `fileObj` is provided.

**Example**

```python
# Read in file locations normally
file_loc1 = EMGFlow.ConvertMapFiles('/data/')

# Filter an existing dataframe with a regular expression
file_loc2 = EMGFlow.ConvertMapFiles(file_loc1, expression='^01')
```

---

## `MapFilesFuse`


**Description**

Combines multiple dictionaries of mapped files (see `MapFiles`) into a Pandas DataFrame.

Assumes that the files contained in the first dictionary are present in each of the following dictionaries.

```python
MapFilesFuse(filedirs, names)
```

**Parameters**

`filedirs`:  dict list
- List of dictionaries assumed to contain file maps.

`names`: str list
- List of names to use for columns, same order as filedirs

**Returns**

`MapFilesFuse`: pd.DataFrame
- Returns a Pandas DataFrame containing each file, and their location for each directory.

**Error**

Raises an error if files contained in the first element of `filedirs` is not contained in the other directories

**Example**

```python
# Create file directory dictionaries
dir_raw = EMGFlow.ConvertMapFiles('/data/raw/')
notch_path = EMGFlow.ConvertMapFiles('/data/notch/')
band_path = EMGFlow.ConvertMapFiles('/data/bandpass/')

# Create dictionary list and names
filedirs = [dir_raw, notch_path, band_path]
names = ['raw', 'notch', 'bandpass']

# Create data frame
df_dirs = EMGFlow.MapFilesFuse(filedirs, names)
```

---

## `ApplyNotchFilters`

**Description**

Applies a list of notch filters to a `Signal`, using the `scipy.signal.iirnotch` method. Returns a new DataFrame object and does not modify the `Signal` provided.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

```python
ApplyNotchFilters(Signal, col, sampling_rate, notch_vals)
```

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

`sampling_rate`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`notch_vals`: tuple list
- List of the notch filters to apply to `Signal`. A notch value is a `(Hz, Q)` tuple of the frequency and Q-factor (intensity) to apply.

**Returns**

`ApplyNotchFilters`: pd.DataFrame
- Returns a `Signal` DataFrame identical to the input, but with the corresponding filters applied to the correct column.

**Example**

```python
# Apply a notch filter at 150Hz and Q-score of 5, and at
# 250Hz and a Q-score of 5
sr = 2000
SignalFiltered = EMGFlow.ApplyNotchFilters(SignalDF, 'column1', sr, [(150, 5), (250, 5)])
```

---

## `NotchFilterSignals`

**Description**

Applies notch filters to all `Signal` files in a folder. Writes output to a new folder directory, mirroring the file hierarchy of the input.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

All files contained within the folder and subfolder with the proper extension are assumed to be `Signal` files. All `Signal` files within the folder and subfolders should have the same change in time between entries.

```python
NotchFilterSignals(in_path, out_path, sampling_rate, notch, cols=None, expresion=None, exp_copy=False, file_ext='csv')
```

**Parameters**

`in_path`: str
- String filepath to a directory containing `Signal` files.

`out_path`: str
- String filepath to a directory for output `Signal` files.

`sampling_rate`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`notch`: tuple list
- List of the notch filters to apply to `Signal`. A notch value is a `(Hz, Q)` tuple of the frequency and Q-factor (intensity) to apply.

`cols`: str (None)
- List of string column names. If provided, will only apply filters to specified columns. If left `None`, will apply filters to each column except for the `'Time'` column.

`expression`: str (None)
- String regular expression. If provided, will only apply filters to `Signal` files whose names match the regular expression, and will ignore everything else.

`exp_copy`: bool (False)
- If `True`, will copy `Signals` that don't match `expression` without modifying them to `out_path`. If `False`, `Signal` files that don't match `expression` will not appear in `out_path`.

`file_ext`: str ("csv")
- String extension of the files to read. Any file in `in_path` with this extension will be considered to be a `Signal` file, and treated as such. The default is `'csv'`.

**Returns**

`NotchFilterSignals`: None
- Does not return a value. Data is written to `out_path`. Data written will be identical to input `Signal` files, but with different values for the filter applied.

**Example**

```python
# Basic parameters
raw_path = '/data/raw/'
notch_path = '/data/notch/'
sampling_rate = 2000
notch_vals = [(50,5), (150,25)]

# Special case parameters
notch_spec = '/data/notch2/'
notch_vals_spec = [(317,25)]
reg = "^(08|11)"
cols = ['EMG_zyg', 'EMG_cor']

# Apply notch_vals filters to all files in raw_path,
# and write them to notch_path
EMGFlow.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols)

# Apply an additional special case filter to files beginning
# with '08' or '11', and write them to notch_spec, making
# sure to copy the other files as well
EMGFlow.NotchFilterSignals(notch_path, notch_spec, sampling_rate, notch_vals_spec, cols, exp_copy=True)
```

---

## `ApplyBandpassFilters`

**Description**

Applies a bandpass filter to a `Signal`, using the `scipy.signal.lfilter` method. Returns a new Pandas DataFrame object and does not modify the `Signal` provided.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

```python
ApplyBandpassFilter(Signal, col, sampling_rate, low, high)
```

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

`sampling_rate`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`low`: int/float
- Numerical value of the lower limit of the bandpass filter.

`high`: int/float
- Numerical value of the upper limit of the bandpass filter.

**Returns**

`ApplyBandpassFilter`: pd.DataFrame
- Returns a `Signal` DataFrame identical to the input, but with the corresponding filters applied to the correct column.

**Example**

```python
# Apply a notch filter from 20Hz to 250Hz
sr = 2000
SignalFiltered = EMGFlow.ApplyNotchFilters(SignalDF, 'column1', sr, 20, 250)
```

---

## `BandpassFilterSignals`

**Description**

Applies a bandpass filter to all `Signal` files in a folder. Writes output to a new folder directory, mirroring the file hierarchy of the input.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

All files contained within the folder and subfolder with the proper extension are assumed to be `Signal` files. All `Signal` files within the folder and subfolders should have the same change in time between entries.

```python
BandpassFilterSignals(in_path, out_path, sampling_rate, low=20, high=450, cols=None, expression=None, exp_copy=False, file_ext='csv')
```

**Theory**

The `low` and `high` parameters default to 20Hz and 450Hz respectively, as research suggests this is a good range for EMG signals. The journal "Filtering the surface EMG signal: Moving artifact and baseline noise contamination" suggests using values if 15-28Hz for the lower threshold, and 400-450Hz for the upper threshold.

These values can also be set manually for specific needs. There is some disagreement in documentation, suggesting other values may be better for some cases.

**Parameters**

`in_path`: str
- String filepath to a directory containing `Signal` files.

`out_path`: str
- String filepath to a directory for output `Signal` files.

`sampling_rate`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`low`: int/float (20)
- Numerical value of the lower limit of the bandpass filter.

`high`: int/float (450)
- Numerical value of the upper limit of the bandpass filter.

`cols`: str (None)
- List of string column names. If provided, will only apply filters to specified columns. If left `None`, will apply filters to each column except for the `'Time'` column.

`expression`: str (None)
- String regular expression. If provided, will only apply filters to `Signal` files whose names match the regular expression, and will ignore everything else.

`exp_copy`: bool (False)
- If `True`, will copy `Signals` that don't match `expression` without modifying them to `out_path`. If `False`, `Signal` files that don't match `expression` will not appear in `out_path`.

`file_ext`: str ("csv")
- String extension of the files to read. Any file in `in_path` with this extension will be considered to be a `Signal` file, and treated as such. The default is `'csv'`.

**Returns**

`BandpassFilterSignals`: None
- Does not return a value. Data is written to `out_path`. Data written will be identical to input `Signal` files, but with different values for the filter applied.

**Example**

```python
notch_path = '/data/notch/'
bandpass_path = '/data/bandpass/'
sampling_rate = 2000
low = 20
high = 200
cols = ['EMG_zyg', 'EMG_cor']

# Apply notch_vals filters to all files in notch_path,
# and write them to bandpass_path
EMGFlow.BandpassFilterSignals(notch_path, bandpass_path, sampling_rate, low, high, cols)
```

---

## `ApplyFWR`

**Description**

Applies a Full Wave Rectifier (FWR) to a `Signal`

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

```python
ApplyFWR(Signal, col)
```

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filter is being applied to.

**Returns**

`ApplyFWR`: pd.DataFrame
- Returns a `Signal` DataFrame identical to the input, but with the corresponding filter applied to the correct column.

**Example**

```python
FWR_DF = EMGFlow.ApplyFWR(SignalDF, 'column1')
```

---

## `ApplyBoxcarSmooth`

**Description**

Applies a boxcar smoothing filter to the `Signal`. Applies a simple unweighted average.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

```python
ApplyBoxcarSmooth(Signal, col, window_size)
```


**Theory**

For a window size $\mu$, the boxcar smoothing algorithm is:
$$s_i=\frac{\sum_{j=i-\mu}^{i+\mu}x_j}{2\mu+1}$$
(O’Haver, 2023)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filter is being applied to.

`window_size`: int
- Size of the window in the smoothing filter.

**Returns**

`ApplyBoxcarSmooth`: pd.DataFrame
- Returns a `Signal` DataFrame identical to the input, but with the corresponding filter applied to the correct column.

**Example**

```python
width = 20
SmoothDF = EMGFlow.ApplyBoxCarSmooth(SignalDF, 'column1', width)
```

---

## `ApplyRMSSmooth`

**Description**

Applies a Root Mean Squared (RMS) smoothing filter to the `Signal`. Takes the average of a window around each point.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

```python
ApplyRMSSmooth(Signal, col, window_size)
```

**Theory**

For a window size $\mu$, the RMS smoothing algorithm is:
$$s_i=\sqrt{\frac{\sum_{j=i-\mu}^{i+\mu}x_j^2}{2\mu+1}}$$

(Dwivedi et al., 2023)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filter is being applied to.

`window_size`: int
- Size of the window in the smoothing filter.

**Returns**

`ApplyRMSSmooth`: pd.DataFrame
- Returns a `Signal` DataFrame identical to the input, but with the corresponding filter applied to the correct column.

**Example**

```python
width = 20
SmoothDF = EMGFlow.ApplyRMSSmooth(SignalDF, 'column1', width)
```

---

## `ApplyGaussianSmooth`

**Description**

Applies a Root Mean Squared (RMS) smoothing filter to the `Signal`. Applies a Gaussian weighted average.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

```python
ApplyGaussianSmooth(Signal, col, window_size, sigma=1)
```

**Theory**

For a window size $\mu$, the Gaussian smoothing algorithm is:
$$s_j=\sum_{i=j-\mu}^{j+\mu}\frac{1}{\sqrt{2\pi}\sigma}e^{-\frac{(\mu-i)^2}{2\sigma^2}}$$
- $\sigma$ is the standard deviation parameter we want to look at

(Fisher et al., 2003)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filter is being applied to.

`window_size`: int
- Size of the window in the smoothing filter.

`sigma`: int/float (1)
- Value of sigma in the Gaussian smoothing's distribution, defaults to 1.

**Returns**

`ApplyGaussianSmooth`: pd.DataFrame
- Returns a `Signal` DataFrame identical to the input, but with the corresponding filter applied to the correct column.

**Example**

```python
width = 20
SmoothDF = EMGFlow.ApplyGaussianSmooth(SignalDF, 'column1', width)
```

---

## `ApplyLoessSmooth`

**Description**

Applies a Loess smoothing filter to the `Signal`. Applies a tricubic weighted average.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

```python
ApplyLoessSmooth(Signal, col, window_size)
```

**Theory**

For a window size $\mu$, the Loess smoothing algorithm is:
$$s_j=\sum_{i=j-\mu}^{j+\mu}w_ix_i$$
$$w_i=\left(1-\left(\frac{d_i}{\max(d_i)}\right)^3\right)^3$$
- $d$ represents a series of evenly spaced numbers such that $-1<d_i<1$

(Figueira, 2021)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filter is being applied to.

`window_size`: int
- Size of the window in the smoothing filter.

**Returns**

`ApplyLoessSmooth`: pd.DataFrame
- Returns a `Signal` DataFrame identical to the input, but with the corresponding filter applied to the correct column.

**Example**

```python
width = 20
SmoothDF = EMGFlow.ApplyLoessSmooth(SignalDF, 'column1', width)
```

---

## `SmoothFilterSignals`

**Description**

Applies a smoothing filter to all `Signal` files in a folder. Writes output to a new folder directory, mirroring the file hierarchy of the input.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

All files contained within the folder and subfolder with the proper extension are assumed to be `Signal` files. All `Signal` files within the folder and subfolders should have the same change in time between entries.

```python
SmoothFilterSignals(in_path, out_path, sampling_rate, window_size, cols=None, expression=None, exp_copy=False, file_ext='csv', method='rms')
```

**Theory**

By default, the `SmoothFilterSignals` function uses the RMS smoothing method. This is because for EMG signals, RMS smoothing is considered to be the best method (RENSHAW et al., 2010).

Other smoothing functions are also available for use if needed.

**Parameters**

`in_path`: str
- String filepath to a directory containing `Signal` files.

`out_path`: str
- String filepath to a directory for output `Signal` files.

`sampling_rate`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`window_size`: int
- Size of the window in the smoothing filter.

`cols`: str (None)
- List of string column names. If provided, will only apply filters to specified columns. If left `None`, will apply filters to each column except for the `'Time'` column.

`expression`: str (None)
- String regular expression. If provided, will only apply filters to `Signal` files whose names match the regular expression, and will ignore everything else.

`exp_copy`: bool (False)
- If `True`, will copy `Signals` that don't match `expression` without modifying them to `out_path`. If `False`, `Signal` files that don't match `expression` will not appear in `out_path`.

`file_ext`: str ("csv")
- String extension of the files to read. Any file in `in_path` with this extension will be considered to be a `Signal` file, and treated as such. The default is `'csv'`.

`method`: str ("rms")
- Smoothing method to be used. Defaults to "rms", but can also be set to "boxcar, "gauss" or "loess"

**Returns**

`SmoothFilterSignals`: None
- Does not return a value. Data is written to `out_path`. Data written will be identical to input `Signal` files, but with different values for the filter applied.

**Example**

```python
bandpass_path = '/data/bandpass/'
smooth_path = '/data/smooth/'
sampling_rate = 2000
size = 20
cols = ['EMG_zyg', 'EMG_cor']

# Apply RMS filters with window size 20 to all files in
# notch_path, and write them to bandpass_path
EMGFlow.SmoothFilterSignals(bandpass_path, smooth_path, sampling_rate, size, cols)
```

---

## `AnalyzeSignals`

**Description**

Extracts usable features from two sets of `Signal` files before and after being smoothed. Writes output to a new folder directory, mirroring the file hierarchy of the two inputs. This assumes that both directories have the same internal file structure.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

All files contained within the folder and subfolder with the proper extension are assumed to be `Signal` files. All `Signal` files within the folder and subfolders should have the same change in time between entries.

For more specifics about the features extracted by this function, see [[05 ExtractFeatures Feature Documentation]]

```python
AnalyzeSignals(in_bandpass, in_smooth, out_path, sampling_rate, cols=None, expression=None, file_ext='csv', short_name=True):
```

**Theory**

This function requires a path to smoothed and unsmoothed data. This is because while time-series features are extracted from smoothed data, spectral features are not. High-frequency components of the signal can be lost in the smoothing, and we want to ensure the spectral features are as accurate as possible.

**Parameters**

`in_bandpass`: str
- String filepath to a directory containing `Signal` files. The files contained within should not have a smoothing filter applied.

`in_smooth`: str
- String filepath to a directory containing `Signal` files. The files contained within should have a smoothing filter applied.

`out_path`: str
- String filepath to a directory for output `Signal` files.

`sampling_rate`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`cols`: str (None)
- List of string column names. If provided, will only apply filters to specified columns. If left `None`, will apply filters to each column except for the `'Time'` column.

`expression`: str (None)
- String regular expression. If provided, will only apply filters to `Signal` files whose names match the regular expression, and will ignore everything else.

`exp_copy`: bool (False)
- If `True`, will copy `Signals` that don't match `expression` without modifying them to `out_path`. If `False`, `Signal` files that don't match `expression` will not appear in `out_path`.

`file_ext`: str ("csv")
- String extension of the files to read. Any file in `in_path` with this extension will be considered to be a `Signal` file, and treated as such. The default is `'csv'`.

`short_names`: bool (True)
- Controls the naming convention of the extracted feature. If left True, will identify each file by their file name. If set to false, will identify each file by their file path. Should be left True unless some files have repeating names.

**Returns**

`AnalyzeSignals`: None
- Does not return a value. Data is written to `out_path`. Data written will be in CSV format. Each row is a different file analyzed, marked by the file ID. Additional columns show the values of the features extracted by the function.

**Example**

```python
bandpass_path = '/data/bandpass/'
smooth_path = '/data/smooth/'
feature_path = '/data/features/'
sampling_rate = 2000
cols = ['EMG_zyg', 'EMG_cor']

# Extracts all features from the files in bandpass_path and
# smooth_path. Assumes the same files are in both paths.
EMGFlow.AnalyzeSignals(bandpass_path, smooth_path, feature_path, sampling_rate, cols)

# Alternatively the same path can be provided twice to extract
# the different feature types from the same files, but spectral
# features may not be as accurate.
EMGFlow.AnalyzeSignals(smooth_path, smooth_path, feature_path, sampling_rate, cols)
```

---

## Sources

Dwivedi, D., Ganguly, A., & Haragopal, V. V. (2023). Contrast between simple and complex classification algorithms. In T. Goswami & G. R. Sinha (Eds.), _Statistical Modeling in Machine Learning_ (pp. 93–110). Academic Press. [https://doi.org/10.1016/B978-0-323-91776-6.00016-6](https://doi.org/10.1016/B978-0-323-91776-6.00016-6)

Figueira, J. P. (2021, June 1). _LOESS_. Medium. [https://towardsdatascience.com/loess-373d43b03564](https://towardsdatascience.com/loess-373d43b03564)

Fisher, R., Perkins, S., Walker, A., & Wolfart, E. (2003). _Gaussian Smoothing_. [https://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm](https://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm)

O’Haver, T. (2023, April). _A Pragmatic Introduction to Signal Processing: Smoothing_. [https://terpconnect.umd.edu/~toh/spectrum/Smoothing.html](https://terpconnect.umd.edu/~toh/spectrum/Smoothing.html)

RENSHAW, D., BICE, M. R., CASSIDY, C., ELDRIDGE, J. A., & POWELL, D. W. (2010). A Comparison of Three Computer-based Methods Used to Determine EMG Signal Amplitude. _International Journal of Exercise Science_, _3_(1), 43–48.