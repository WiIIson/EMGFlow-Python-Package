---
outline: deep
---

# API Overview

EMGFlow is broken into 5 modules - FileIO, preprocessing signals, feature extraction, detecting outliers, and generating visualizations.

## File Format

The EMGFlow Python package works with CSV files, but is planned to expand to other file formats in the future. To prepare your data to be compatible with EMGFlow, it needs to be a CSV file with ideally a "Time" column, and additional columns for the signals you have recorded. "Time" should contain the time from 0 the signal has been recorded for, and the additional columns will have the recording of the signals at that time. Additionally, the file should have a constant sampling rate (time difference between each sequential row).

## Modules

### Module Structure

```mermaid
mindmap
    root((EMGFlow))
        EF(Extract Features):::link:wiiison.github.io/EMGFlow-Python-Package/reference/feature-extraction.html
        FA(File Access):::link:wiiison.github.io/EMGFlow-Python-Package/reference/file-access.html
        DO(Detect Outliers):::link:wiiison.github.io/EMGFlow-Python-Package/reference/outlier-detection.html
        PlS(Plot Signals):::link:wiiison.github.io/EMGFlow-Python-Package/reference/plot-signals.html
        PrS(Preprocess Signals):::link:wiiison.github.io/EMGFlow-Python-Package/reference/preprocess-signals.html
```

### `FileAccess`

These functions provide helper methods for accessing files, and are mostly used internally by the package.

One notable function, `MapFiles`, takes a path to a folder, and generates a dictionary of paths to files contained within. This makes it easier to create a loop over subfiles, reading them in and performing analysis.

`MapFiles` forms the basis for the two modes of analysis offered by EMGFlow - automated, or manual.

The "automated" mode makes the processing pipeline much simpler. In these functions, a file location is provided, default parameters are set, and a file output location is set. The functions then apply the filters to each file found in the folder, and output the filtered files to the output folder. Notable functions include:
- `NotchFilterSignals`
- `BandpassFilterSignals`
- `SmoothFilterSignals`

The "manual" mode allows for additional customization of processing. In these functions, a dataframe is provided, filter parameters are set, and the dataframe is returned. These functions are useful if the processing pipeline requires further additional processing before being outputted, of if the project is not large-scale enough to warrent batch processing. Notable functions include:
- `ApplyNotchFilters`
- `ApplyBandpassFilter`
- `ApplyRMSSmooth`

For more information about file accessing functions, see [FileAccess API](./file-access.md).

### `PreprocessSignals`

This module provides preprocessing functions for cleaning sEMG signals prior to their use in feature extraction. Signal processing is broken into 3 parts: notch filtering, bandpass filtering and smoothing. Each part has additional functions that support more specific needs, explained in more detail in the module descriptions.

#### `NotchFilterSignals()`

Notch filtering involves filtering specific frequencies. This is typically due to some sort of interference, such as the power source of the device taking the reading.

`NotchFilterSignals()` provides flexibility for use in different regions of the world. Some filtering packages only provide notch filtering for 60Hz, the frequency where power can interfere with signal readings.  However, other regions use 50Hz frequencies.

For more information about further customizations and detail about `NotchFilterSignals()`, see [PreprocessSignals API](./preprocess-signals.md).

#### `BandpassFilterSignals()`

Bandpass filtering involves specifying a range of frequencies to keep, and removing all other frequencies outside this range. This is useful to remove interference outside the most meaningful range of readings. 

`BandpassFilterSignals()` uses bandpass thresholds of 20Hz and 450Hz, as this is default for EMG signals (De Luca et al., 2010). However, there is some disagreement within literature for different muscels, so `BandpassFilterSignals()` provides the option to change the thresholds.

For more information about further customizations and detail about `BandpassFilterSignals()`, see [PreprocessSignals API](./preprocess-signals.md).

#### `SmoothFilterSignals()`

Smoothing involves limiting the impacts of noise and outliers in the signal. By default, this function uses the RMS smoothing method, as it is the best choice for smoothing EMG signals (RENSHAW et al., 2010).

`SmoothFilterSignals()` by default uses the RMS smoothing method, as it is the best choice for filtering EMG signals (RENSHAW et al., 2010). Regardless, EMGFlow provides different methods for smoothing signals which can be used instead.

For more information about further customizations and detail about `SmoothFilterSignals()`, see [PreprocessSignals API](./preprocess-signals.md).

### `ExtractFeatures` Module

This module takes preprocessed data, and extracts features from the sEMG signal that capture information in both time and frequency domains. The main function to do this is `ExtractFeatures`. Within this call, individual features are calculated by their own functions, allowing them to be incorporated into your own workflow.

Analysis involves extracting the features from each signal into a feature file. This is the end of the pipeline, producing the final result.

For a more detailed explanation about the features extracted by `ExtractFeatures()`, see [ExtractFeatures API](./feature-extraction.md).

### `OutlierFinder` Module

This module provides methods to help detect signal files that contain outliers. This helps for workflows involving batch processing of files, where it might be harder to determine if there are any patterns, or specific files that need additional filters applied.

Outlier detection is handled by the function `DetectOutliers()`. This function outputs a dictionary of file names and locations for each signal marked as an outlier.

For more information about further customizations and specifications that can be made to `DetectOutliers()`, see [OutlierFinder API](./outlier-detection.md).

### `PlotSignals` Module

The plotting module `PlotSignals` provides functions to help visualize individual, or large batches of signal data. This helps visually see what is happening in a signal to identify outliers, and determine the kinds of filters that need to be applied.

`PlotSpectrum` can generate a signal plot for every signal file in the folder it is provided.

`PlotCompareSignals()` does the same, generating plots comparing every signal at two different stages of their processing.

For more information about further customizations and specifications that can be made to `PlotSpectrum()` or `PlotCompareSignals()`, see [PlotSignals API](./plot-signals.md).

## Sources

De Luca, C., Gilmore, L., Kuznetsov, M., & Roy, S. (2010). Filtering the surface EMG signal: Movement artifact and baseline noise contamination. _Journal of Biomechanics_, _43_, 1.

RENSHAW, D., BICE, M. R., CASSIDY, C., ELDRIDGE, J. A., & POWELL, D. W. (2010). A Comparison of Three Computer-based Methods Used to Determine EMG Signal Amplitude. _International Journal of Exercise Science_, _3_(1), 43–48.