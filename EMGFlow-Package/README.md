# EMGFlow <img src="https://raw.githubusercontent.com/WiIIson/EMGFlow-Python-Package/main/HexSticker.png"  width="100" height="110" align="right">

The open workflow for EMG signal processing and feature extraction.

**EMGFlow** is a Python package for researchers and clinicians to engage in signal processing. EMGFlow provides a broad range of functions to meet your EMG signal processing needs, without prescribing a specific workflow. EMGFlow follows open standards of data processing, such as CSV files and Pandas data frames to allow easy integration. With functions to extract 32 different features according to your needs, EMGFlow provides a uniquely deep feature extraction.

EMGFlow also includes an easy method for producing detailed graphs of EMG signals in large quantities.

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

To see full documentation, see the [GitHub.io Pages](https://wiiison.github.io/EMGFlow-Python-Package/index.html).

## Installation

EMGFlow can be installed from PyPI:
```python
pip install EMGFlow
```

Once installed, the package can be loaded as follows:
```python
import EMGFlow
```

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