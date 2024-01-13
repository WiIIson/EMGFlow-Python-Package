# EMGFlow

The EMG Workflow Toolkit (EMGFlow) was created to provide a more streamlined way to perform the processing of EMG signals in Python. The package provides modules for different steps in inspection, preprocessing, and analysis.

The EMGFlow package stands out among others as it does not follow a strict pipeline, allowing users to use what functions they need, rather than forcing users to follow a specific series of functions.

## EMGFlow - Signals

The EMGFlow package handles the processing of EMG signals. In EMGFlow, a 'Signal' is just a Pandas dataframe. Such a dataframe should have a 'Time' column, and additional columns that contain the signal strengths recorded at said time.
- The number of columns does not matter - you can have one recording column or more
- A column named 'Time' will be treated as recorded time and ignored. Any other columns can be analyzed (or not)
- The 'Time' column is not necessary to process signals, so you don't have to add one as long as you know the sampling rate

## EMGFlow - Sampling Rate

When processing signals in EMGFlow, the other thing you need to know is the sampling rate of your data. The sampling rate is how many samples of the signals are taken per second. This is easily calculated by finding the inverse of the time between your samples.
- Don't combine signals that have different sampling rates
- Signals with different sampling rates can be compared after analysis

---

# EMGFlow.SignalFilterer

The `SignalFilterer` module provides functions for the processing of signals. These functions make up the main part of the package, and provide customization options for specific needs

In EMGFlow, a "signal" is defined as a Pandas dataframe. This dataframe will have one or more columns for strength of the different signals being recorded (e.g., mV), and a `Time` column for the time since the start of recording that the reading was taken. 

## EMGFlow.SignalFilterer.MapFiles

```python
EMGFlow.SignalFilterer.Mapfiles(in_path, file_ext='csv', expression=None)
```

Returns a dictionary of filename/filepath key/value items for files found in subdirectories of a folder.

Parameters:

&nbsp;&nbsp;&nbsp;&nbsp;in_path: String,

---

# OutlierFinder Module

The `OutlierFinder` module provides functions for the detection of outliers in signals. This can help decide if special cases need to be taken into consideration when applying filters to signals.

---

# PlotSignals Module

The `PlotSignals` module provides functions for generating visualizations of signals.