# Signal pre-processing

The `PreProcessSignals` module provides preprocessing functions for cleaning sEMG signals prior to their use in feature extraction. Signal processing is broken into 3 parts: notch filtering, bandpass filtering and smoothing. Each part has additional functions that support more specific needs, explained in more detail in the module descriptions.



## `EMG2PSD`

### Description

Creates a PSD (power spectrum density) of a Signal. Uses the Welch method, meaning it can be used as a Long Term Average Spectrum (LTAS).

```python
EMG2PSD(Sig_vals, sr=1000, normalize=True)
```

### Parameters

`Sig_vals`: float list
- A list of float values. A column of a Signal.

`sr`: int/float (1000)
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`normalize`: bool (True)
- Normalizes the result of the PSD by its maximum strength.

### Returns

`EMG2PSD`: pd.DataFrame
- Returns a dictionary of frequencies and related strengths with the columns "Frequency" and "Power".

### Error

Raises an error if the sampling rate is less or equal to 0.

### Example

```python
sr = 2000
PSD = EMGFlow.EMG2PSD(SignalDF['col1'], sr)
```



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

**Error**

Raises an error if `col` is not found in `Signal`.

Raises an error if the sampling rate is less or equal to 0.

Raises an error if a value in `notch_vals` is greater than `sampling_rate/2` or less than 0.

**Example**

```python
# Apply a notch filter at 150Hz and Q-score of 5, and at
# 250Hz and a Q-score of 5
sr = 2000
SignalFiltered = EMGFlow.ApplyNotchFilters(SignalDF, 'column1', sr, [(150, 5), (250, 5)])
```



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

**Error**

Raises an error if `col` is not found in any of the Signal files found.

Raises an error if the sampling rate is less or equal to 0.

Raises an error if a value in `notch_vals` is greater than `sampling_rate/2` or less than 0.

Raises a warning if `expression` causes all files to be filtered out.

Raises an error if a file cannot be read in `in_path`.

Raises an error if an unsupported file format was provided for `file_ext`.

Raises an error if `expression` is not a valid regular expression.

**Example**

```python
# Basic parameters
raw_path = '/data/raw'
notch_path = '/data/notch'
sampling_rate = 2000
notch_vals = [(50,5), (150,25)]

# Special case parameters
notch_spec = '/data/notch2'
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



## `ApplyBandpassFilter`

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

`low`: int/float (20)
- Numerical value of the lower limit of the bandpass filter. Defaults to 20Hz.

`high`: int/float (450)
- Numerical value of the upper limit of the bandpass filter. Defaults to 450Hz.

**Returns**

`ApplyBandpassFilter`: pd.DataFrame
- Returns a `Signal` DataFrame identical to the input, but with the corresponding filters applied to the correct column.

**Error**

Raises an error if `col` is not found in `Signal`.

Raises an error if the sampling rate is less or equal to 0.

Raises an error if `high` is not higher than `low`.

**Example**

```python
# Apply a notch filter from 20Hz to 250Hz
sr = 2000
SignalFiltered = EMGFlow.ApplyNotchFilters(SignalDF, 'column1', sr, 20, 250)
```



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

**Error**

Raises an error if `col` is not found in any of the Signal files found.

Raises an error if the sampling rate is less or equal to 0.

Raises a warning if `expression` causes all files to be filtered out.

Raises an error if `high` is not higher than `low`.

Raises an error if a file cannot be read in `in_path`.

Raises an error if an unsupported file format was provided for `file_ext`.

Raises an error if `expression` is not a valid regular expression.

**Example**

```python
notch_path = '/data/notch'
bandpass_path = '/data/bandpass'
sampling_rate = 2000
low = 20
high = 200
cols = ['EMG_zyg', 'EMG_cor']

# Apply notch_vals filters to all files in notch_path,
# and write them to bandpass_path
EMGFlow.BandpassFilterSignals(notch_path, bandpass_path, sampling_rate, low, high, cols)
```



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

**Error**

Raises an error if `col` is not found in `Signal`.

**Example**

```python
FWR_DF = EMGFlow.ApplyFWR(SignalDF, 'column1')
```



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
$$
s_i=\frac{\sum_{j=i-\mu}^{i+\mu}x_j}{2\mu+1}
$$
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

**Error**

Raises an error if `col` is not found in `Signal`.

Raises an error if `window_size` is less or equal to 0.

Raises a warning if `window_size` is greater than the length of `Signal`.

**Example**

```python
width = 20
SmoothDF = EMGFlow.ApplyBoxCarSmooth(SignalDF, 'column1', width)
```



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
$$
s_i=\sqrt{\frac{\sum_{j=i-\mu}^{i+\mu}x_j^2}{2\mu+1}}
$$

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

**Error**

Raises an error if `col` is not found in `Signal`.

Raises an error if `window_size` is less or equal to 0.

Raises a warning if `window_size` is greater than the length of `Signal`.

**Example**

```python
width = 20
SmoothDF = EMGFlow.ApplyRMSSmooth(SignalDF, 'column1', width)
```



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
$$
s\\_j=\sum\\_{i=j-\mu}^{j+\mu}\frac{1}{\sqrt{2\pi}\sigma}e^{-\frac{(\mu-i)^2}{2\sigma^2}}
$$
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

**Error**

Raises an error if `col` is not found in `Signal`.

Raises an error if `window_size` is less or equal to 0.

Raises a warning if `window_size` is greater than the length of `Signal`.

**Example**

```python
width = 20
SmoothDF = EMGFlow.ApplyGaussianSmooth(SignalDF, 'column1', width)
```



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
$$
s_j=\sum_{i=j-\mu}^{j+\mu}w_ix_i
$$
$$
w_i=\left(1-\left(\frac{d_i}{\max(d_i)}\right)^3\right)^3
$$
- $d$ represents a series of evenly spaced numbers such that $-1\lt d_i\lt 1$

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

**Error**

Raises an error if `col` is not found in `Signal`.

Raises an error if `window_size` is less or equal to 0.

Raises a warning if `window_size` is greater than the length of `Signal`.

**Example**

```python
width = 20
SmoothDF = EMGFlow.ApplyLoessSmooth(SignalDF, 'column1', width)
```



## `SmoothFilterSignals`

**Description**

Applies a smoothing filter to all `Signal` files in a folder. Writes output to a new folder directory, mirroring the file hierarchy of the input.

Components of a "`Signal` file":
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

All files contained within the folder and subfolder with the proper extension are assumed to be `Signal` files. All `Signal` files within the folder and subfolders should have the same change in time between entries.

```python
SmoothFilterSignals(in_path, out_path, window_size, cols=None, expression=None, exp_copy=False, file_ext='csv', method='rms', sigma=1)
```

**Theory**

By default, the `SmoothFilterSignals` function uses the RMS smoothing method. This is because for EMG signals, RMS smoothing is considered to be the best method (RENSHAW et al., 2010).

Other smoothing functions are also available for use if needed.

**Parameters**

`in_path`: str
- String filepath to a directory containing `Signal` files.

`out_path`: str
- String filepath to a directory for output `Signal` files.

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
- Smoothing method to be used. Defaults to "rms", but can also be set to "boxcar, "gauss" or "loess".

`sigma`: float (1)
- Value of `sigma` used with a Gaussian filter. Only affects output when using a Gaussian filter.

**Returns**

`SmoothFilterSignals`: None
- Does not return a value. Data is written to `out_path`. Data written will be identical to input `Signal` files, but with different values for the filter applied.

**Error**

Raises an error if an invalid smoothing method is passed to `method`.

Raises an error if any of the Signal files don't contain a column listed in `cols`.

Raises an error if `window_size` is less or equal to 0.

Raises a warning if `expression` causes all files to be filtered out.

Raises a warning if `window_size` is greater than the length of `Signal`.

Raises an error if a file cannot be read in `in_path`.

Raises an error if an unsupported file format was provided for `file_ext`.

Raises an error if `expression` is not a valid regular expression.

**Example**

```python
bandpass_path = '/data/bandpass'
smooth_path = '/data/smooth'
size = 20
cols = ['EMG_zyg', 'EMG_cor']

# Apply smoothing filter with window size 20 to all files in
# bandpass_path, and write them to smooth_path
EMGFlow.SmoothFilterSignals(bandpass_path, smooth_path, size, cols)
```



## Sources

Dwivedi, D., Ganguly, A., & Haragopal, V. V. (2023). Contrast between simple and complex classification algorithms. In T. Goswami & G. R. Sinha (Eds.), _Statistical Modeling in Machine Learning_ (pp. 93–110). Academic Press. [https://doi.org/10.1016/B978-0-323-91776-6.00016-6](https://doi.org/10.1016/B978-0-323-91776-6.00016-6)

Figueira, J. P. (2021, June 1). _LOESS_. Medium. [https://towardsdatascience.com/loess-373d43b03564](https://towardsdatascience.com/loess-373d43b03564)

Fisher, R., Perkins, S., Walker, A., & Wolfart, E. (2003). _Gaussian Smoothing_. [https://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm](https://homepages.inf.ed.ac.uk/rbf/HIPR2/gsmooth.htm)

O’Haver, T. (2023, April). _A Pragmatic Introduction to Signal Processing: Smoothing_. [https://terpconnect.umd.edu/~toh/spectrum/Smoothing.html](https://terpconnect.umd.edu/~toh/spectrum/Smoothing.html)

RENSHAW, D., BICE, M. R., CASSIDY, C., ELDRIDGE, J. A., & POWELL, D. W. (2010). A Comparison of Three Computer-based Methods Used to Determine EMG Signal Amplitude. _International Journal of Exercise Science_, _3_(1), 43–48.