# Processing Steps

## Download

EMGFlow can be installed from PyPI:

```bash
pip install EMGFlow
```

## Quick example

_EMGFlow_ extracts a comprehensive set of 33 statistical features from sEMG signals, achieved with only a few lines of code:

```python
import EMGFlow as ef

# Get path dictionary
path_names = ef.make_paths()

# Load sample data
ef.make_sample_data(path_names)

# Preprocess signals (sample data recorded at 50 Hz mains)
ef.clean_signals(path_names, sampling_rate=2000, notch_f0=50)

# Plot data on the "EMG_zyg" column
ef.plot_dashboard(path_names, 'EMG_zyg', 'mV')

# Extract features to disk "Features.csv"
df = ef.extract_features(path_names, sampling_rate=2000)
```

## EMGFlow Pipeline Processing Steps

 ![Pipeline processing steps](/figures/figure1.png)
 _Figure 1. An overview of the processing pipeline._
