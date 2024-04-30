# Processing Pipeline

EMGFlow is broken into 3 parts - processing signals, detecting outliers, and creating visualizations. Descriptions of functions for each part are grouped together on the same documentation page

---

## Signal Processing Pipeline

Signal processing is broken into 4 parts: notch filtering, bandpass filtering, smoothing and analysis. Each part has additional functions that support more specific needs, explained in more detail in the module descriptions.

### `NotchFilterSignals()`

**Description**

Notch filtering involves filtering specific frequencies. This is typically due to some sort of interference, such as the power source of the device taking the reading.

**Parameters**

Notch filtering is controlled by the function `NotchFilterSignals()`, with the following main parameters:
- `in_path` <-- File path to input folder
- `out_path` <-- File path to output folder
- `sampling_rate` <-- Sampling rate of the data
- `notch` <-- Notch filters to be applied

`in_path` refers to the folder containing the signal data. The function will be able to detect signals in the folder, and in any subfolders.

`out_path` refers to the folder where the filtered signals will be output to. The function will automatically recreate the file structure of the input folder with additional subfolders.

`sampling_rate` refers to the sampling rate of the data. The function will assume that each signal, and each column, is using the same sampling rate.

`notch` refers to the notch filters being applied to the signal. This takes the form of a list of `(Hz,Q)` tuples. `Hz` is the frequency to which the filter is being applied, and `Q` is the Q-factor (strength of the filter, where a lower number is a stronger filter). The Q-factor needs to be explored to find a suitable value.  When the Q-factor is too high, there will be barely any effect.  When the Q_factor is too, important frequencies around the target being filtered out. All filters in the list will be applied to each column and signal.

**Value-Added**

`NotchFilterSignals()` provides flexibility for use in different regions of the world. Some filtering packages only provide notch filtering for 60Hz, the frequency where power can interfere with signal readings.  However, other regions use 50Hz frequencies.

For more information about further customizations and detail about `NotchFilterSignals()`, see [SignalFilterer documentation](./04%20SignalFilterer%20Documentation.md).

### `BandpassFilterSignals()`

**Description**

Bandpass filtering involves specifying a range of frequencies to keep, and removing all other frequencies outside this range. This is useful to remove interference outside the most meaningful range of readings. 

**Parameters**

Bandpass filtering is controlled by the function `BandpassFilterSignals()`, with the following parameters:
- `in_path` <-- File path to input folder
- `out_path` <-- File path to output folder
- `sampling_rate` <-- Sampling rate of the data
- `low` <-- Lower frequency range
- `high` <-- Upper frequency range

`in_path` refers to the folder containing the signal data. The function will be able to detect signals in the folder, and in any subfolders.

`out_path` refers to the folder where the filtered signals will be output to. The function will automatically recreate the file structure of the input folder with additional subfolders.

`sampling_rate` refers to the sampling rate of the data. The function will assume that each signal, and each column, is using the same sampling rate.

`low` and `high` are the thresholds for the bandpass filter. All frequencies outside the range provided are filtered out of the signal. The defaults respectively are 20 and 450.

**Value-Added**

`BandpassFilterSignals()` uses bandpass thresholds of 20Hz and 450Hz, as this is default for EMG signals (De Luca et al., 2010). However, there is some disagreement within literature for different muscels, so `BandpassFilterSignals()` provides the option to change the thresholds.

For more information about further customizations and detail about `BandpassFilterSignals()`, see [SignalFilterer documentation](./04%20SignalFilterer%20Documentation.md).

### `SmoothFilterSignals()`

Smoothing involves limiting the impacts of noise and outliers in the signal. By default, this function uses the RMS smoothing method, as it is the best choice for smoothing EMG signals (RENSHAW et al., 2010).

Smoothing is controlled by the function `SmoothFilterSignals()`, with the following main parameters:
- `in_path` <-- File path to input folder
- `out_path` <-- File path to output folder
- `sampling_rate` <-- Sampling rate of the data
- `window_size` <-- Size of the window to smooth
- `method` <-- Smoothing method to use

`in_path` refers to the folder containing the signal data. The function will be able to detect signals in the folder, and in any subfolders.

`out_path` refers to the folder where the filtered signals will be output to. The function will automatically recreate the file structure of the input folder with additional subfolders.

`sampling_rate` refers to the sampling rate of the data. The function will assume that each signal, and each column, is using the same sampling rate.

`window_size` refers to the size of the window when the data is being smoothed. This affects how large of an area around the value to take an average of.

`method` refers to the smoothing method to use. Can be one of 'rms', 'boxcar', 'gauss' or 'loess'. The default is 'rms'.

**Value-Added**

`SmoothFilterSignals()` by default uses the RMS smoothing method, as it is the best choice for filtering EMG signals (RENSHAW et al., 2010). Regardless, EMGFlow provides different methods for smoothing signals which can be used instead.

For more information about further customizations and detail about `SmoothFilterSignals()`, see [SignalFilterer documentation](./04%20SignalFilterer%20Documentation.md).

### `AnalyzeSignals()`

**Description**

Analysis involves extracting the features from each signal into a feature file. This is the end of the pipeline, producing the final result.

Analysis is controlled by the function `AnalyzeSignals()`, with the following main parameters:
- `in_bandpass` <-- File path to input folder of data before being smoothed
- `in_smooth` <-- File path to input folder of data after being smoothed
- `out_path` <-- File path to output folder
- `sampling_rate` <-- Sampling rate of the data

`AnalyzeSignals()` extracts the following time-series features:
- Min
- Max
- Mean
- SD
- Skew
- Kurtosis
- IEMG
- MAV
- MMAV
- SSI
- VAR
- VOrder
- RMS
- WL
- LOG
- MFL
- AP
- Spectral Flux

And the following spectral features:
- Max frequency
- Twitch ratio
- Twitch index
- Twitch slope fast
- Twitch slope slow
- Spectral centroid
- Spectral flatness
- Spectral decrease
- Spectral entropy
- Spectral rolloff
- Spectral bandwidth

This function requires a path to smoothed and unsmoothed data. This is because while time-series features are extracted from smoothed data, spectral features are not. High-frequency components of the signal can be lost in the smoothing, and we want to ensure the spectral features are as accurate as possible.

For more information about further customizations and specifications that can be made to `AnalyzeSignals()`, see [SignalFilterer documentation](./04%20SignalFilterer%20Documentation.md).

For a more detailed explanation about the features extracted by `AnalyzeSignals()`, see [ExtractFeatures documentation](./05%20ExtractFeatures%20Feature%20Documentation.md).

---
## Outlier Detection

EMGFlow provides functions to help detect outliers in large batches of signal data. This helps to identify which files need to be inspected for outliers.

Outlier detection is handled by the function `DetectOutliers()`. This function fits an inverse graph to the PSD representation of the signal, and identifies if there is a value significantly above a threshold.
- `in_path` <-- File path to input folder
- `sampling_rate` <-- Sampling rate of the data
- `threshold` <-- Threshold to consider a value an outlier

`in_path` refers to the folder containing the raw signal data. The function will be able to detect signals in the folder, and in any subfolders.

`sampling_rate` refers to the sampling rate of the data. The function will assume that each signal, and each column, is using the same sampling rate.

`threshold` refers to the number of times above the median for a value to be considered an outlier. This is checked for each column in the signal file, and is marked as an outlier if an outlier is found in any column.

This function outputs a dictionary of file names and locations for each signal marked as an outlier.

For more information about further customizations and specifications that can be made to `DetectOutliers()`, see [OutlierFinder documentation](./06%20OutlierFinder%20Documentation.md).

---

## Plotting

The plotting module `PlotSignals` provides functions to help visualize individual, or large batches of signal data. This helps visually see what is happening in a signal to identify outliers, and determine the kinds of filters that need to be applied.

### `PlotSpectrum()`

`PlotSpectrum` takes care of generating large numbers of signal plots for all signals contained in a folder and subfolders.
- `in_path` <-- File path to input folder
- `out_path` <-- File path to output folder
- `sampling_rate` <-- Sampling rate of the data

`in_path` refers to the folder containing the raw signal data. The function will be able to detect signals in the folder, and in any subfolders.

`out_path` refers to the folder where the plots will be output to. The function will automatically recreate the file structure of the input folder with additional subfolders.

`sampling_rate` refers to the sampling rate of the data. The function will assume that each signal, and each column, is using the same sampling rate.

For more information about further customizations and specifications that can be made to `PlotSpectrum()`, see [PlotSignals documentation](./07%20PlotSignals%20Documentation.md).

### `PlotCompareSignals()`

`PlotCompareSignals()` compares plots of signals for two different stages of processing.
- `in_path1` <-- File path to input folder
- `in_path2` <-- File path to input folder
- `out_path` <-- File path to output folder
- `sampling_rate` <-- Sampling rate of the data

`in_path1` refers to the folder containing the first group of signal data. The function will be able to detect signals in the folder, and in any subfolders.

`in_path2` refers to the folder containing the second group of signal data. The function will be able to detect signals in the folder, and in any subfolders.

`out_path` refers to the folder where the plots will be output to. The function will automatically recreate the file structure of the input folder with additional subfolders.

`sampling_rate` refers to the sampling rate of the data. The function will assume that each signal, and each column, is using the same sampling rate.

For more information about further customizations and specifications that can be made to `PlotCompareSignals()`, see [[07 PlotSignals Documentation]]

---

## Sources

De Luca, C., Gilmore, L., Kuznetsov, M., & Roy, S. (2010). Filtering the surface EMG signal: Movement artifact and baseline noise contamination. _Journal of Biomechanics_, _43_, 1.

RENSHAW, D., BICE, M. R., CASSIDY, C., ELDRIDGE, J. A., & POWELL, D. W. (2010). A Comparison of Three Computer-based Methods Used to Determine EMG Signal Amplitude. _International Journal of Exercise Science_, _3_(1), 43–48.