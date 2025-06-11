# Getting Started with EMGFlow

## Download

EMGFlow can be installed from PyPI:

```bash
pip install EMGFlow
```

## Quick example

_EMGFlow_ extracts a comprehensive set of 32 statistical features from sEMG signals, achieved with only a few lines of code:

```python
import EMGFlow as ef

# Get path dictionary
path_names = ef.make_paths()

# Load sample data
ef.make_sample_data(path_names)

# Preprocess signals
ef.clean_signals(path_names, sampling_rate=2000)

# Plot data on the "EMG_zyg" column
ef.plot_dashboard(path_names, 'EMG_zyg', 'mV')

# Extract features and save results in "Features.csv" in feature_path
df = ef.extract_features(path_names, sampling_rate=2000)
```

## Input data format

_EMGFlow_ accepts data in plaintext .CSV file format. Files should have the following format:

- Row 1 - Column headers
- Col 1 - Labelled Time, and contains the timestamps of sampled data
- Col 2:n - Assumed to be sEMG or related signal data.

As an example, here is the first few rows of some sample data included in the package:

| Time    | EMG_zyg   | EMG_cor   |
| ------- | --------- | --------- |
| 50.0005 | -0.145569 | -0.097046 |
| 50.0010 | -0.129089 | -0.100708 |
| 50.0015 | -0.118713 | -0.101929 |
| 50.0020 | -0.118103 | -0.104675 |
| 50.0025 | -0.104370 | -0.097656 |
| ...     | ...       | ...       |

The "Time" column can generally be omitted when the sampling rate is known, though some functions require a "Time" column.

## EMGFlow Pipeline Processing Steps

![Pipeline processing steps](/figures/figure1.png)
*Figure 1. Decomposition of the EMG signal into individual frequency components.*