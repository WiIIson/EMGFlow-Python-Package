# EMGFlow <img src="HexSticker.png"  width="100" height="110" align="right">

The open workflow for EMG signal processing and feature extraction.

**EMGFlow** is a Python package for researchers and clinicians to engage in signal processing using the data you have your way. EMGFlow provides a broad range of functions to meet your EMG signal processing needs, without prescribing a specific workflow. With functions to extract over 30 different features according to your needs, EMGFlow provides a uniquely deep feature extraction.

EMGFLow also includes an easy method for producing detailed graphs of EMG signals in large quantities.

The simple navigation menu allows you to switch between which files you see as well as which layers are overlayed:
![Example 1](EMGFlow_GUI.gif)

---

## Example

As a quick example, the following will create a feature file, starting with a folder of raw data:
```python
import EMGFlow.SignalFilterer as ESIG

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
ESIG.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals)
ESIG.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high)
ESIG.SmoothFilterSignals(band_path, smooth_path, sampling_rate, smooth_window)
ESIG.AnalyzeSignals(band_oath, smooth_path, feature_path, sampling_rate)
# Will create a "Features.csv" file in feature_path with results
```

---

## Documentation

General:
- [EMG processing background](docs/02%20Background.md)
- [EMGFlow processing pipeline overview](docs/03%20Processing%20Pipeline.md)
- [SignalFilterer module EMG processing documentation](docs/04%20SignalFilterer%20Documentation.md)
- [SignalFilterer module feature extraction documentation](docs/05%20ExtractFeatures%20Feature%20Documentation.md)
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

EMGFlow's functions are divided into 3 different modules, which can be imported with shorthands as follows:
```python
import EMGFlow.SignalFilterer as ESIG
import EMGFlow.OutlierFinder as EOLF
import EMGFlow.PlotSignals as EPLT
```

---

## Citations

This package can be cited as follows:

```bibtex
@software{Conley_EMGFlow_2024,
  author = {Conley {\tt william@cconley.ca}, William and Livingstone, Steven R},
  month = {03},
  title = {{EMGFlow Package}},
  url = {https://github.com/WiIIson/EMGFlow-Python-Package},
  version = {1.0.9},
  year = {2024}
}
```