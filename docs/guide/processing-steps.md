# Processing Steps

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

As an example, here is the first few rows of some sample data included in the package with added NaN values:

| Time   | EMG_zyg   | EMG_cor   |
| ------ | --------- | --------- |
| 0.0005 | -0.145569 | -0.097046 |
| 0.0010 | -0.129089 | -0.100708 |
| 0.0015 | -0.118713 | -0.101929 |
| 0.0020 | NaN       | NaN       |
| 0.0025 | -0.104370 | -0.097656 |
| ...    | ...       | ...       |

For proper calculations, ensure the 'Time' column has an equal difference between each sequential row.

EMGFlow uses `pd.read_csv()` from the Pandas package to read in files. Continuing with the documentation for Pandas, the following values are interpreted as `NaN`:
- " "
- "#N/A"
- "#N/A N/A"
- "#NA"
- "-1.#IND"
- "-1.#QNAN"
- "-NaN"
- "-nan"
- "1.#IND"
- "1.#QNAN"
- "\<NA\>"
- "N/A"
- "NA"
- "NULL"
- "NaN"
- "None"
- "n/a"
- "nan"
- "null"

In the future, we plan to make EMGFlow compatible with other file formats.

## EMGFlow Pipeline Processing Steps

![Pipeline processing steps](/figures/figure1.png)
*Figure 1. Decomposition of the EMG signal into individual frequency components.*

## Sample Data Files

The sample data used in EMGFlow is taken from [PeakAffectDS](https://zenodo.org/records/6403363).

| PeakAffectDS Name | EMGFlow Name       | Timeframe             |
| ----------------- | ------------------ | :-------------------: |
| 01-03-01.csv      | sample_data_01.csv | 50.0005s : 60.0000s   |
| 01-04-01.csv      | sample_data_02.csv | 130.0005s : 140.0000s |
| 02-06-02.csv      | sample_data_03.csv | 10.0005s : 20.0000s   |
| 02-07-02.csv      | sample_data_04.csv | 15.0005s : 25.0000s   |