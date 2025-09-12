# File Formats

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

" ", "#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN", "-NaN", "-nan", "1.#IND", "1.#QNAN", "\<NA\>", "N/A", "NA", "NULL", "NaN", "None", "n/a", "nan", "null"

## Output Data Format

*EMGFlow* outputs a single plaintext .CSV file format containing features extracted from all processed input files. The output file has the following format:

| File_path | EMG_Zyg_Min | ... | EMG_Zyg_SpecPmissing | EMG_Cor_Min | ... | EMG_Cor_SpecPmissing |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 01\sample_data_01.csv | 0.0027489562796772 | ... | 0.00525 | 0.0035784079507369 | ... | 0.0058 |
| 01\sample_data_02.csv | 0.0049906242832924 | ... | 0.00085 | 0.0040041486806442 | ... | 0.00035 |
| 02\sample_data_03.csv | 0.0020494782305965 | ... | 0.0168 | 0.0021287377144706 | ... | 0.01805 |
| 02\sample_data_04.csv | 0.0024170458470961 | ... | 0.0021 | 0.0021508113881666 | ... | 0.001 |

Within the output feature file, each muscle's features are blocked together. E.g., muscle 1 spans columns 2:36, muscle 2 spans 37:71 etc. The number of columns is dependent on the number of recorded muscles contained in the input data.

Column name definitions:

| Column name | Feature | Type |
| :-- | :-- | :-- |
| [EMG_Min](./extract-features#basic-time-series-statistics) | Minimum voltage | Time-series |
| [EMG_Max](./extract-features#basic-time-series-statistics) | Maximum voltage | Time-series |
| [EMG_Mean](./extract-features#basic-time-series-statistics) | Mean voltage | Time-series |
| [EMG_SD](./extract-features#basic-time-series-statistics) | Standard deviation of voltage | Time-series |
| [EMG_Skew](./extract-features#basic-time-series-statistics) | Skew of voltage | Time-series |
| [EMG_Kurtosis](./extract-features#basic-time-series-statistics) | Kurtosis of voltage | Time-series |
| [EMG_IEMG](./extract-features.md#calc_iemg) | Integrated EMG of voltage | Time-series |
| [EMG_MAV](./extract-features.md#calc_mav) | Mean absolute value of voltage | Time-series |
| [EMG_MMAV1](./extract-features.md#calc_mmav1) | Modified mean absolute value 1 of voltage | Time-series |
| [EMG_MMAV2](./extract-features.md#calc_mmav2) | Modified mean absolute value 2 of voltage | Time-series |
| [EMG_SSI](./extract-features.md#calc_ssi) | Simple square integral of voltage | Time-series |
| [EMG_VAR](./extract-features.md#calc_var) | Variance of voltage | Time-series |
| [EMG_VOrder](./extract-features.md#calc_vorder) | V-order of voltage | Time-series |
| [EMG_RMS](./extract-features.md#calc_rms) | Root mean square of voltage | Time-series |
| [EMG_WL](./extract-features.md#calc_wl) | Waveform length of voltage | Time-series |
| [EMG_LOG](./extract-features.md#calc_log) | Log-detector of voltage | Time-series |
| [EMG_MFL](./extract-features.md#calc_mfl) | Maximum fractal length of voltage | Time-series |
| [EMG_AP](./extract-features.md#calc_ap) | Average power of voltage | Time-series |
| EMG_Timeseries_Pmissing | Percentage of missing data | Time-series |
| [EMG_Max_Freq](./extract-features.md#basic-time-series-statistics) | Maximum frequency | Spectral |
| [EMG_MDF](./extract-features.md#calc_mdf) | Median frequency | Spectral |
| [EMG_MNF](./extract-features.md#calc_mnf) | Mean frequency | Spectral |
| [EMG_Twitch_Ratio](./extract-features.md#calc_twitch_ratio) | Twitch ratio of frequency | Spectral |
| [EMG_Twitch_Index](./extract-features.md#calc_twitch_index) | Twitch index of frequency | Spectral |
| [EMG_Twitch_Slope](./extract-features.md#calc_twitch_slope) | Twitch slope of frequency | Spectral |
| [EMG_SC](./extract-features.md#calc_sc) | Spectral centroid of frequency | Spectral |
| [EMG_SFlt](./extract-features.md#calc_sflt) | Spectral flatness of frequency | Spectral |
| [EMG_SFlx](./extract-features.md#calc_sflx) | Spectral flux of frequency | Spectral |
| [EMG_SS](./extract-features.md#calc_ss) | Spectral spread of frequency | Spectral |
| [EMG_SDec](./extract-features.md#calc_sdec) | Spectral decrease of frequency | Spectral |
| [EMG_SE](./extract-features.md#calc_se) | Spectral entropy of frequency | Spectral |
| [EMG_SR](./extract-features.md#calc_sr) | Spectral rolloff of frequency | Spectral |
| [EMG_SBw](./extract-features.md#calc_sbw) | Spectral bandwidth | Spectral |
| EMG_Spec_PMissing | Percentage of missing data | Spectral |

## Sample Data Files

The sample data used in EMGFlow is taken from [PeakAffectDS](https://zenodo.org/records/6403363).

| PeakAffectDS Name | EMGFlow Name       | Timeframe             |
| :---------------- | :----------------- | :-------------------: |
| 01-03-01.csv      | sample_data_01.csv | 50.0005s : 60.0000s   |
| 01-04-01.csv      | sample_data_02.csv | 130.0005s : 140.0000s |
| 02-06-02.csv      | sample_data_03.csv | 10.0005s : 20.0000s   |
| 02-07-02.csv      | sample_data_04.csv | 15.0005s : 25.0000s   |

### File Manipulations

The sample data files were manipulated in the following ways:
- `sample_data_01.csv`: Added chunk of NaN values.
- `sample_data_02.csv`: Added scattered individual NaN values.
- `sample_data_03.csv`: Added several large chunks of NaN values creating "data islands"
- `sample_data_04.csv`: Injected a small high-intensity bandlimited noise pulse.