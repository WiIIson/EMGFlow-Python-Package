# EMGFlow <img src="https://raw.githubusercontent.com/WiIIson/EMGFlow-Python-Package/main/HexSticker.png"  width="100" height="110" align="right">

The open workflow for EMG signal processing and feature extraction.

**EMGFlow** is a Python package for researchers and clinicians to engage in signal processing. EMGFlow provides a broad range of functions to meet your EMG signal processing needs, without prescribing a specific workflow. EMGFlow follows open standards of data processing, such as CSV files and Pandas data frames to allow easy integration. With functions to extract 32 different features according to your needs, EMGFlow provides a uniquely deep feature extraction.

EMGFlow also includes an easy method for producing detailed graphs of EMG signals in large quantities.

## Example

As a quick example, the following will create a feature file, starting with a folder of raw data:
```python
import EMGFlow

# Paths for data files
raw_path = '/data/raw'          # Raw file contains raw data
notch_path = '/data/notch'
band_path = '/data/bandpass'    # Additional files are empty
smooth_path = '/data/smoothed'
feature_path = '/data/feature'

# Sampling rate for all files
sampling_rate = 2000

# Filter parameters
notch_vals = [(50, 5)]  # Notch filters to apply (Q, Hz)
band_low = 20           # Low threshold for bandpass filter
band_high = 140         # High threshold for bandpass filter
smooth_window = 50      # Window size for smoothing filter

# Preprocess signals
EMGFlow.NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals)
EMGFlow.BandpassFilterSignals(notch_path, band_path, sampling_rate, band_low, band_high)
EMGFlow.SmoothFilterSignals(band_path, smooth_path, sampling_rate, smooth_window)

# Extract features and save results to "Features.csv" in feature_path
df = EMGFlow.ExtractFeatures(band_oath, smooth_path, feature_path, sampling_rate)
```

---

## Documentation

To see full documentation, see the [GitHub.io Pages](https://wiiison.github.io/EMGFlow-Python-Package/index.html).

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

---

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