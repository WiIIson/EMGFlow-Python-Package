# EMGFlow <img src="HexSticker.png"  width="100" height="110" align="right">

[![Versions](https://img.shields.io/pypi/pyversions/EMGFlow.svg?logo=python&logoColor=FFE873)](https://pypi.python.org/pypi/emgflow)
[![Coverage](badges/coverage.svg)](https://github.com/WiIIson/EMGFlow-Python-Package)
[![pypi](https://img.shields.io/pypi/v/emgflow.svg)](https://pypi.python.org/pypi/emgflow)
[![Downloads](https://static.pepy.tech/badge/EMGFlow/month)](https://pepy.tech/project/EMGFlow)
[![Downloads](https://static.pepy.tech/badge/EMGFlow)](https://pepy.tech/project/EMGFlow)

The open workflow for EMG signal processing and feature extraction.

**EMGFlow** is a Python package for researchers and clinicians to engage in signal processing. EMGFlow provides a broad range of functions to meet your EMG signal processing needs, without prescribing a specific workflow. EMGFlow follows open standards of data processing, such as CSV files and Pandas data frames to allow easy integration. With functions to extract 32 different features according to your needs, EMGFlow provides a uniquely deep feature extraction.

EMGFlow also includes an easy method for producing detailed graphs of EMG signals in large quantities.

The simple navigation menu allows you to switch between which files you see as well as which layers are overlayed:
![Example 1](EMGFlow_GUI.gif)

## Statement Of Need

While several packages exist for processing physiological and neurological signals, support for surface electromyography (sEMG) has remained limited. Many packages lack a comprehensive set of features that can be extracted from sEMG data, leaving researchers to use a patchwork of tools. Other packages are orientated around event detection in individual recordings and use GUI-based workflow that requires greater manual intervention. While this design works well for single person recordings, it complicates the extraction of features from large datasets, such as those common to machine learning.

The EMGFlow package – a portmanteau of EMG and Workflow - fills this gap. Our package provides a flexible pipeline for the extraction of a wide range of sEMG features, with a scalable design that is suited to the processing of large datasets.

## Example

As a quick example, the following will create a feature file, starting with a folder of raw data:
```python
import EMGFlow

# Get path dictionary
path_names = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(path_names)

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
EMGFlow.notch_filter_signals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)

# 2. Apply bandpass filter
EMGFlow.bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)

# 3. Apply smoothing filter
EMGFlow.smooth_filter_signals(path_names['Bandpass'], path_names['Smooth'], smooth_window, cols)

# 4. Extract features
df = EMGFlow.extract_features(path_names, sampling_rate, cols)
```

## Documentation

[![pypi](https://img.shields.io/badge/documentation-online-brightgreen.svg)](https://wiiison.github.io/EMGFlow-Python-Package/reference/api-overview.html)
[![pypi](https://img.shields.io/badge/tutorials-examples-orange.svg?colorB=E91E63)](https://wiiison.github.io/EMGFlow-Python-Package/guide/examples.html)

General:
- [EMG processing background](https://wiiison.github.io/EMGFlow-Python-Package/guide/about-emg.html)
- [EMGFlow processing pipeline overview](https://wiiison.github.io/EMGFlow-Python-Package/reference/api-overview.html)
- [FileAccess module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/access-files.html)
- [PreprocessSignals module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/preprocess-signals.html)
- [ExtractFeatures module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/extract-features.html)
- [OutlierFinder module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/detect-outliers.html)
- [PlotSignals module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/plot-signals.html)

Examples:
- [Processing pipeline examples](https://wiiison.github.io/EMGFlow-Python-Package/guide/examples.html)

## Installation

EMGFlow can be installed from PyPI:
```python
pip install EMGFlow
```

Once installed, the package can be loaded as follows:
```python
import EMGFlow
```

Project dependencies can be seen [here](pyproject.toml).

## Contributions

Contributions and community guidelines can be seen [here](https://github.com/WiIIson/EMGFlow-Python-Package/blob/main/.github/CONTRIBUTING.md).

## Citations

This package can be cited as follows:

```bibtex
@software{Conley_EMGFlow_2024,
  author = {Conley, William and Livingstone, Steven R},
  month = {03},
  title = {{EMGFlow Package}},
  url = {https://github.com/WiIIson/EMGFlow-Python-Package},
  version = {1.0.17},
  year = {2024},
  note = "{\tt william@cconley.ca}"
}
```

If you are using a different version of EMGFlow, change the `version` tag to the version you are using.