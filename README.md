# EMGFlow <img src="HexSticker.png"  width="100" height="110" align="right">

[![Tests](https://github.com/WiIIson/EMGFlow-Python-Package/actions/workflows/tests.yml/badge.svg)](https://github.com/WiIIson/EMGFlow-Python-Package/actions/workflows/tests.yml)
![pypi](https://img.shields.io/pypi/v/emgflow.svg)
[![Downloads](https://static.pepy.tech/badge/EMGFlow/month)](https://pepy.tech/project/EMGFlow)
[![Downloads](https://static.pepy.tech/badge/EMGFlow)](https://pepy.tech/project/EMGFlow)

The open workflow for EMG signal processing and feature extraction.

**EMGFlow** is a Python package for researchers and clinicians to engage in signal processing. EMGFlow provides a broad range of functions to meet your EMG signal processing needs, without prescribing a specific workflow. EMGFlow follows open standards of data processing, such as CSV files and Pandas data frames to allow easy integration. With functions to extract over 30 different features according to your needs, EMGFlow provides a uniquely deep feature extraction.

EMGFlow also includes an easy method for producing detailed graphs of EMG signals in large quantities.

The simple navigation menu allows you to switch between which files you see as well as which layers are overlayed:
![Example 1](EMGFlow_GUI.gif)

---

## Statement Of Need

While several packages exist for processing physiological and neurological signals, support for surface electromyography (sEMG) has remained limited. Many packages lack a comprehensive set of features that can be extracted from sEMG data, leaving researchers to use a patchwork of tools. Other packages are orientated around event detection in individual recordings and use GUI-based workflow that requires greater manual intervention. While this design works well for single person recordings, it complicates the extraction of features from large datasets, such as those common to machine learning.

The EMGFlow package – a portmanteau of EMG and Workflow - fills this gap. Our package provides a flexible pipeline for the extraction of a wide range of sEMG features, with a scalable design that is suited to the processing of large datasets.

---

## Example

As a quick example, the following will create a feature file, starting with a folder of raw data:
```python
import EMGFlow

# Paths for data files
raw_path = '/data/raw/'          # Raw file contains raw data
notch_path = '/data/notch/'
band_path = '/data/bandpass/'    # Additional files are empty
smooth_path = '/data/smoothed/'
feature_path = '/data/feature/'

# Sampling rate for all files
sampling_rate = 2000

# Filter parameters
notch_vals = [(50, 5)]  # Notch filters to apply (Q, Hz)
band_low = 20           # Low threshold for bandpass filter
band_high = 140         # High threshold for bandpass filter
smooth_window = 50      # Window size for smoothing filter

# Signal analysis
EMGFlow.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals)
EMGFlow.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high)
EMGFlow.SmoothFilterSignals(band_path, smooth_path, sampling_rate, smooth_window)
EMGFlow.AnalyzeSignals(band_oath, smooth_path, feature_path, sampling_rate)
# Will create a "Features.csv" file in feature_path with results
```

---

## Documentation

General:
- [EMG processing background](docs/02%20Background.md)
- [EMGFlow processing pipeline overview](docs/03%20Processing%20Pipeline.md)
- [PreprocessSignals module EMG processing documentation](docs/04%20PreprocessSignals%20Documentation.md)
- [PreprocessSignals module feature extraction documentation](docs/05%20ExtractFeatures%20Feature%20Documentation.md)
- [OutlierFinder module documentation](docs/06%20OutlierFinder%20Documentation.md)
- [PlotSignals module documentation](docs/07%20PlotSignals%20Documentation.md)

Examples:
- [Processing pipeline examples](docs/01%20Examples.md)

---

## Installation

EMGFlow can be installed from PyPI:
```python
pip install EMGFlow
```

Once installed, the package can be loaded as follows:
```python
import EMGFlow
```

Project dependencies can be seen [here](EMGFlow-Package/pyproject.toml).

---

## Community Guidelines

We welcome contributions to the project. These can be initiated through the project's issue tracker or through a pull request. Suggestions for feature enhancements, tips, as well as general questions and concerns can also be expressed through direct interaction with contributors and developers.

If you experience any challenges with this module such as bugs, test support, or feature requests, please feel free to use this [issue tracker](https://github.com/WiIIson/EMGFlow-Python-Package/issues).

---

## Citations

This package can be cited as follows:

```bibtex
@software{Conley_EMGFlow_2024,
  author = {Conley {\tt william@cconley.ca}, William and Livingstone, Steven R},
  month = {03},
  title = {{EMGFlow Package}},
  url = {https://github.com/WiIIson/EMGFlow-Python-Package},
  version = {1.0.14},
  year = {2024}
}
```