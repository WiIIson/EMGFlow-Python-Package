# `extract_features` Module Documentation

These functions extract features from the sEMG signal, capturing information in both time and frequency domains. The main function to do this is `extract_features`. Within this call, individual features are calculated by their own functions, allowing them to be incorporated into your own workflow.

## Module Structure

```mermaid
mindmap
    root((EMGFlow))
        AF(Access Files)
        DO(Detect Outliers)
        PrS(Preprocess Signals)
        PlS(Plot Signals)
        EF(Extract Features)
            (Time-Series Features)
                calc_iemg
                calc_mav
                calc_mmav1
                calc_mmav2
                calc_ssi
                calc_var
                calc_vorder
                calc_rms
                calc_wl
                calc_wamp
                calc_log
                calc_mfl
                calc_ap
            (Spectral Features)
                calc_spec_flux
                calc_mdf
                calc_mnf
                calc_twitch_ratio
                calc_twitch_index
                calc_twitch_slope
                calc_sc
                calc_sf
                calc_ss
                calc_sdec
                calc_sentropy
                calc_sroll
                calc_sbw
            extract_features
```

## Basic Time-Series Statistics

The `extract_features` function calculates some basic statistics that don't involve their own functions. This includes:
- Minimum voltage (using `np.min`)
- Maximum voltage (using `np.max`)
- Mean voltage (using `np.mean`)
- Standard deviation of voltage (using `np.std`)
- Skew of voltage (using `scipy.stats.skew`)
- Kurtosis of voltage (using `scipy.stats.kurtosis`)
- Maximum frequency (using `np.max`)

Skew and kurtosis are less common, and have a more detailed explanation below.

### Skew

Skewness describes the symmetry of a dataset, considered more skewed the less symmetrical the left and right distributions of the median are.

Skew is calculated as follows:
$$s=\frac{\frac{\mu-M_o}{\sigma}}{\frac{3(\mu-M_d)}{\sigma}}$$
- $\mu$ <-- Mean
- $\sigma$ <-- Standard deviation
- $M_o$ <-- Mode
- $M_d$ <-- Median

**Skew** is calculated with `scipy.stats.skew`

### Kurtosis

Kurtosis describes the amount of data in the tails of a bell curve of a distribution.

Kurtosis is calculated as follows:
$$
k=\frac{1}{N}\sum_{i=1}^N\left(\frac{x_i-\mu}{\sigma}\right)^4
$$
- $\mu$ <-- Mean
- $\sigma$ <-- Standard deviation
- $N$ <-- Number of data points

**Kurtosis** is calculated with `scipy.stats.kurtosis`





## `calc_iemg`

**Description**

Calculates the Integrated EMG (IEMG) of the signal. The IEMG measures the area under the curve of the signal, which can provide useful information about muscle activity. In an EMG signal, the IEMG describes when the muscle begins contracting, and is related to the signal sequence firing point (Phinyomark et al., 2009).

```python
calc_iemg(Signal, col, sampling_rate)
```

**Theory**

In the reference, the IEMG does not account for the sampling rate. Two signal recordings with the same shape but different sampling rate would have different results since we are integrating with respect to time. As such, the calculation made here will include multiplying by sampling rate.

The IEMG is calculated as follows:
$$
\text{IEMG}=s_r\sum_{i=1}^N|x_i|
$$
- $s_r$ <-- Sampling rate
- $N$ <-- Number of data points

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

`sampling_rate`: int/float
- Sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

An exception is raised if `sampling_rate` is less or equal to 0.

**Returns**

`IEMG`: float
- The IEMG of `Signal`.

**Example**

```python
# Calculate the IEMG of Signal, for column 'EMG_zyg'
IEMG = EMGFlow.calc_iemg(Signal, 'EMG_zyg', 2000)
```





## `calc_mav`

**Description**

Calculates the Mean Absolute Value (MAV) of the signal. In an EMG signal, the MAV describes the muscle contraction level (Phinyomark et al., 2009).

```python
calc_mav(Signal, col)
```

**Theory**

The MAV is calculated as follows:
$$
\text{MAV}=\frac{1}{N}\sum_{i=1}^N|x_i|
$$
- $N$ <-- Number of data points

(Tkach et al., 2010)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`MAV`: float
- The MAV of `Signal`.

**Example**

```python
# Calculate the MAV of Signal, for column 'EMG_zyg'
MAV = EMGFlow.calc_mav(Signal, 'EMG_zyg', 2000)
```






## `calc_mmav1`

**Description**

Calculates the Modified Mean Absolute Value 1 (MMAV1) of the signal. The MMAV1 is an alteration of MAV that gives more weight to values in the middle of the signal to reduce error from the beginning and end of the signal.
```python
calc_mmav1(Signal, col)
```

**Theory**

The MMAV1 is identical to MAV, except it introduces a weight to the calculation. Values are given a weight of 1 when they are between the 25th and 75th percentile, and 0.5 outside.

The MMAV1 is calculated as follows:
$$
\text{MMAV1}=\frac{1}{N}\sum_{i=1}^N|x_iw_i|
$$
$$
w_i=\left\{ \begin{matrix} 1 & \text{if }0.25N\le i\le 0.75N \\ 0.5 & \text{otherwise} \end{matrix} \right\}
$$
- $N$ <-- Number of data points

(Chowdhury et al., 2013)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`MMAV1`: float
- The MMAV1 of `Signal`.

**Example**

```python
# Calculate the MMAV1 of Signal, for column 'EMG_zyg'
MMAV1 = EMGFlow.calc_mmav1(Signal, 'EMG_zyg', 2000)
```





## `calc_mmav2`

**Description**

Calculates the Modified Mean Absolute Value 2 (MMAV2) of the signal. The MMAV2 is an alteration of MAV that gives more weight to values in the middle of the signal to reduce error from the beginning and end of the signal.
```python
calc_mmav2(Signal, col)
```

**Theory**

The MMAV2 is identical to MAV, except it introduces a weight to the calculation. Values are given a weight of 1 when they are between the 25th and 75th percentile, a weight of $\frac{4i}{N}$ when below the 25th percentile, and a weight of $\frac{4(i-N)}{N}$ when above the 75th percentile. This makes the weight smoothly increase and decrease approaching the center of the signal, as opposed to MMAV1 which instantly jumps from a weight of 0.5 to 1.

The MMAV2 is calculated as follows:
$$
\text{MMAV2}=\frac{1}{N}\sum_{i=1}^N|x_iw_i|
$$
$$
w_i=\left\{ \begin{matrix} 1 & \text{if }0.25N\le i\le 0.75N \\ \frac{4i}{N} & \text{if } i<0.25N  \\ \frac{4(i-N)}{4} & \text{if } i>0.75N \end{matrix} \right\}
$$
- $N$ <-- Number of data points

(Hamedi et al., 2014)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`MMAV2`: float
- The MMAV2 of `Signal`.

**Example**

```python
# Calculate the MMAV2 of Signal, for column 'EMG_zyg'
MMAV2 = EMGFlow.calc_mmav2(Signal, 'EMG_zyg', 2000)
```





## `calc_ssi`

**Description**

Calculates the Simple Square Integral (SSI) of the signal. In an EMG signal, the SSI describes the energy of the signal (Phinyomark et al., 2009).

```python
calc_ssi(Signal, col, sampling_rate)
```

**Theory**

In the reference, the SSI does not account for the sampling rate. Two signal recordings with the same shape but different sampling rate would have different results since we are integrating with respect to time. As such, the calculation made here will include multiplying by sampling rate.

The SSI is calculated as follows:
$$
\text{SSI}=s_r^2\sum_{i=1}^N|x_i|^2
$$
- $s_r$ <-- Sampling rate
- $N$ <-- Number of data points

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

`sampling_rate`: int/float
- Sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

An exception is raised if `sampling_rate` is less or equal to 0.

**Returns**

`SSI`: float
- The SSI of `Signal`.

**Example**

```python
# Calculate the SSI of Signal, for column 'EMG_zyg'
SSI = EMGFlow.calc_ssi(Signal, 'EMG_zyg', 2000)
```





## `calc_var`

**Description**

Calculates the Variance (VAR) of the signal. In an EMG signal, the VAR describes the power of the signal (Phinyomark et al., 2009).

```python
calc_var(Signal, col)
```

**Theory**

The VAR is calculated as follows:
$$
\text{VAR}=\frac{1}{N-1}\sum_{i=1}^Nx_i^2
$$

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`VAR`: float
- The VAR of `Signal`.

**Example**

```python
# Calculate the VAR of Signal, for column 'EMG_zyg'
VAR = EMGFlow.calc_var(Signal, 'EMG_zyg')
```





## `calc_vorder`

**Description**

Calculates the V-Order of a signal. The V-Order is an alteration of VAR that takes the square root of the result.

```python
calc_vorder(Signal, col)
```

**Theory**

The V-Order is calculated using the $v$-operator, essentially working like a Euclidean distance to the $v$th order. One study indicates that the best value for $v$ is 2, meaning the V-Order is just the square root of the VAR feature.

The V-Order is calculated as follows:
$$
\text{vORDER}=\sqrt{\text{VAR}}
$$

(Tkach et al., 2010)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`VOrder`: float
- The V-Order of `Signal`.

**Example**

```python
# Calculate the V-Order of Signal, for column 'EMG_zyg'
VOrder = EMGFlow.calc_vorder(Signal, 'EMG_zyg')
```





## `calc_rms`

**Description**

Calculates the Root Mean Square (RMS) of a signal. In an EMG signal, the RMS provides information about the constant force, and non-fatiguing contractions of the muscles (Phinyomark et al., 2009).

```python
calc_rms(Signal, col)
```

**Theory**

The RMS is calculated as follows:
$$
\text{RMS}=\sqrt{\frac{1}{N}\sum_{i=1}^N|x_i|^2}
$$
- $N$ <-- Number of data points

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`RMS`: float
- The RMS of `Signal`.

**Example**

```python
# Calculate the RMS of Signal, for column 'EMG_zyg'
RMS = EMGFlow.calc_rms(Signal, 'EMG_zyg')
```





## `calc_wl`

**Description**

Calculates the Waveform Length (WL) of a signal. The WL provides information about the amplitude, frequency, and duration of the signal.

```python
calc_wl(Signal, col)
```

**Theory**

The WL is calculated as follows:
$$
\text{WL}=\sum_{i=1}^{N-1}|x_{i+1}-x_i|
$$
- $N$ <-- Number of data points

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`WL`: float
- The WL of `Signal`.

**Example**

```python
# Calculate the WL of Signal, for column 'EMG_zyg'
WL = EMGFlow.calc_wl(Signal, 'EMG_zyg')
```





## `calc_wamp`

**Description**

Calculate the Willison Amplitude (WAMP) of a signal. The WAMP measures the number of times an EMG amplitude exceeds a given threshold. In an EMG signal, the WAMP describes the firing of Motor Unit Action Potentials (MUAP), and muscle contraction level (Phinyomark et al., 2009).

```python
calc_wamp(Signal, col, threshold)
```

**Theory**

Thresholds for the WAMP are commonly chosen within the 50-100 mV range. The WAMP counts the number of recorded times in the signal that the charge is greater than the threshold, so it can be affected by the sampling rate. If datasets with different sampling rates are being compared, it may be beneficial to normalize each result by the length of the signal.

When choosing a value, pass it in terms of the same units being used in the data.

The WAMP is calculated as follows:
$$
\text{WAMP}=\sum_{i=1}^{N-1}f(|x_{i+1}-x_i|)
$$
$$
f(x)=\left\{\begin{matrix} 1 & \text{if }x>\epsilon \\ 0 & \text{otherwise} \end{matrix}\right\}
$$
- $N$ <-- Number of data points
- $\epsilon$ <-- Voltage change threshold

(Tkach et al., 2010)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

`threshold`: float
- Threshold of the WAMP.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`WAMP`: int
- The WAMP of `Signal`.

**Example**

```python
# Calculate the WAMP of Signal, for column 'EMG_zyg'
WAMP = EMGFlow.calc_wamp(Signal, 'EMG_zyg', 55)
```





## `calc_log`

**Description**

Calculates the Log-Detector (LOG) of a signal. The LOG provides an estimate of the force exerted by the muscle.

```python
calc_log(Signal, col)
```

**Theory**

The LOG is calculated as follows:
$$
\text{LOG}=e^{\frac{1}{N}\sum_{i=1}^N\log(|x_k|)}
$$
- $N$ <-- Number of data points

(Tkach et al., 2010)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`LOG`: float
- The LOG of `Signal`.

**Example**

```python
# Calculate the LOG of Signal, for column 'EMG_zyg'
LOG = EMGFlow.calc_log(Signal, 'EMG_zyg')
```





## `calc_mfl`

**Description**

Calculates the Maximum Fractal Length (MFL) of a signal. The MFL measures the activation of low-level muscle contractions.

```python
calc_mfl(Signal, col)
```

**Theory**

The MFL is calculated as follows:
$$
\text{MFL}=\log\left(\sqrt{\sum_{i=1}^{N-1}(x_{i+1}-x_i)^2}\right)
$$
- $N$ <-- Number of data points

(Too et al., 2019)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`MFL`: float
- The MFL of `Signal`.

**Example**

```python
# Calculate the MFL of Signal, for column 'EMG_zyg'
MFL = EMGFlow.calc_mfl(Signal, 'EMG_zyg')
```





## `calc_ap`

**Description**

Calculates the Average Power (AP) of a signal. The AP measures the energy distribution of the signal.

```python
calc_ap(Signal, col)
```

**Theory**

The AP is calculated as follows:
$$
\text{AP}=\frac{1}{N}\sum_{i=1}^Nx_i^2
$$
- $N$ <-- Number of data points

(Too et al., 2019)

**Parameters**

`Signal`: pd.DataFrame 
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`col`: str
- Column of `Signal` the feature is calculated from.

**Raises**

An exception is raised if `col` is not a column of `Signal`.

**Returns**

`AP`: float
- The AP of `Signal`.

**Example**

```python
# Calculate the AP of Signal, for column 'EMG_zyg'
AP = EMGFlow.calc_ap(Signal, 'EMG_zyg')
```





## `calc_spec_flux`

**Description**

Calculates the Spectral Flux of a signal. Spectral Flux measures the change in spectrums between two signals, or two sections of a signal.

`calc_spec_flux` behaves differently, depending on if `diff` is a Pandas dataframe or float. A dataframe treats `diff` as a second signal, and finds the spectral flux between it and `Signal1`. Providing a float $n$ will split `Signal1` into the first $n$% of the dataframe, and the remaining $n-1$% of the dataframe, finding the spectral flux between these two parts.

The call to `calc_spec_flux` within `extract_features` uses a default value of `diff=0.5`.

```python
calc_spec_flux(Signal1, diff, col, sampling_rate, diff_sr=None)
```

**Theory**

Spectral Flux is used to compare the spectral compositions of two signals. This is complicated to implement, so there is no one function to handle this.

Spectral Flux is calculated as follows:
$$
\text{FL}_{i,i-1}=\sum_{k=1}^{Wf_L}(\text{EN}_i(k)-\text{EN}_{i-1}(k))^2
$$

(Giannakopoulos & Pikrakis, 2014)

**Parameters**

`Signal1`: pd.DataFrame
- A Pandas dataframe containing a 'Time' column, and additional columns for signal data.

`diff`: pd.DataFrame, float
- Either a new signal dataframe, or a decimal indicating the percentage of the signal to split.

`col`: str
- Column of `Signal` the feature is calculated from.

`sampling_rate`: int/float
- Sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`diff_sr`: int, float, optional (None)
- Sampling rate for `diff`, if it has a different sampling rate than `Signal1`. The default is None, in which case if `diff` is a dataframe, the sampling rate is assumed to be the same as `Signal1`.

**Raises**

An exception is raised if `col` is not a column of `Signal1`.

An exception is raised if `sampling_rate` is less or equal to 0.

An exception is raised if `diff` is a float, but isn't between 0 and 1.

An exception is raised if `diff` is a dataframe and does not contain `col`.

An exception is raised if `diff_sr` is less or equal to 0.

An exception is raised if `diff` is an invalid data type.

**Returns**

`flux`: float
- The Spectral Flux of `Signal`.

**Example**

```python
# Calculate the Spectral Flux of two signals
flux1 = EMGFlow.calc_spec_flux(Signal1, Signal2, 'EMG_zyg', 2000)

# Calculate the Spectral Flux of one signal divided at the halfway point
flux2 = EMGFlow.calc_spec_flux(Signal1, 0.5, 'EMG_zyg', 2000)
```





## calc_mdf

**Description**

Calculates the Median Frequency (MDF) of a Signal.

**Theory**

MDF is the frequency on the power spectrum that can divide it into two regions of equal total power.

Since it may not be possible to perfectly divide the spectrum into two regions of exactly equal power, this function finds the frequency that divides it the best.

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`med_freq`: float
- The MDF of `psd`.

**Example**

```python
# Calculate the MDF of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
MDF = EMGFlow.calc_mdf(psd)
```





## calc_mnf

**Description**

Calculates the Mean Frequency (MNF) of a Signal.

**Theory**

MNF is the mean frequency on the power spectrum, weighted by the power of each frequency.

MNF is calculated as follows:

$$
\text{MNF}=\frac{\sum_i^N f_ip_i}{\sum_i^N p_i}
$$

(Phinyomark et al., 2009)

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`mean_freq`: float
- The MNF of `psd`.

**Example**

```python
# Calculate the MNF of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
MNF = EMGFlow.calc_mnf(psd)
```





## `calc_twitch_ratio`

**Description**

Calculates the Twitch Ratio of a Signal based on its power distribution. 

```python
calc_twitch_ratio(psd, freq=60)
```

**Theory**

This metric uses a proposed muscle separation theory put forward by this project. This measure is typically used in audio feature extraction, separating the high and low frequencies. This kind of separation is not typically done in EMG feature extraction. However, literature suggests that there are both high and low frequency muscle activations that can be separated by an approximately 60Hz threshold (Hegedus et al., 2020). Since these muscles are present in the face (McComas, 1998), this experimental feature is being added by applying this audio feature in a new context.

Twitch Ratio is an adaptation of Alpha Ratio (Eyben et al., 2016).

Twitch Ratio is calculated as follows:
$$
\text{TR}=\frac{\sum_{i=f_0}^{f_t} p_i}{\sum_{i=f_t}^{f_N}p_i}
$$
- $p_i$ <-- Power of normalized PSD at frequency $i$
- $f_0$ <-- Minimum frequency of the PSD
- $f_t$ <-- Threshold frequency of the PSD
- $f_N$ <-- Maximum frequency of the PSD

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

`freq`: int, float, optional (60)
- Frequency threshold separating fast-twitching (high-frequency) muscles from slow-twitching (low-frequency) muscles. The default is 60.

**Raises**

An exception is raised if `freq` is less or equal to 0.

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`twitch_ratio`: float
- The Twitch Ratio of `psd`.

**Example**

```python
# Calculate the Twitch Ratio of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
twitch_ratio = EMGFlow.calc_twitch_ratio(psd)
```





## `calc_twitch_index`

**Description**

Calculates the Twitch Index of a Signal based on its power distribution. 

```python
calc_twitch_index(psd, freq=60)
```

**Theory**

This metric uses a proposed muscle separation theory put forward by this project. This measure is typically used in audio feature extraction, separating the high and low frequencies. This kind of separation is not typically done in EMG feature extraction. However, literature suggests that there are both high and low frequency muscle activations (slow twitching muscles, and fast twitching muscles) that can be separated by an approximately 60Hz threshold. As such, this experimental feature is being added by applying this audio feature in a new context.

Twitch Index is an adaptation of the Hammarberg index (Eyben et al., 2016).

Twitch Index is calculated as follows:
$$
\text{TR}=\frac{\max\left(\sum_{i=f_0}^{f_t} p_i\right)}{\max\left(\sum_{i=f_t}^{f_N}p_i\right)}
$$
- $p_i$ <-- Power of normalized PSD at frequency $i$
- $f_0$ <-- Minimum frequency of the PSD
- $f_t$ <-- Threshold frequency of the PSD
- $f_N$ <-- Maximum frequency of the PSD

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

`freq`: int, float, optional (60)
- Frequency threshold separating fast-twitching (high-frequency) muscles from slow-twitching (low-frequency) muscles. The default is 60.

**Raises**

An exception is raised if `freq` is less or equal to 0.

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`twitch_index`: float
- The Twitch Ratio of `psd`.

**Example**

```python
# Calculate the Twitch Index of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
twitch_index = EMGFlow.calc_twitch_index(psd)
```





## `calc_twitch_slope`

**Description**

Calculates the Twitch Slope of a Signal based on its power distribution.

```python
calc_twitch_slope(psd, freq=60)
```

**Theory**

This metric uses a proposed muscle separation theory put forward by this project. This measure is typically used in audio feature extraction, separating the high and low frequencies. This kind of separation is not typically done in EMG feature extraction. However, literature suggests that there are both high and low frequency muscle activations (slow twitching muscles, and fast twitching muscles) that can be separated by an approximately 60Hz threshold. As such, this experimental feature is being added by applying this audio feature in a new context.

Twitch Slope is an adaptation of spectral slope (Eyben et al., 2016).

`calc_twitch_slope` uses the `np.linalg.lstsq` to find the slope of the line of best fit for the two regions separated by frequency, and returns both values.

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

`freq`: int, float, optional (60)
- Frequency threshold separating fast-twitching (high-frequency) muscles from slow-twitching (low-frequency) muscles. The default is 60.

**Raises**

An exception is raised if `freq` is less or equal to 0.

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`fast_slope`: float
- The Twitch Slope of the fast-twitching muscles of `psd`.

`slow_slope`: float
- The Twitch Slope of the slow-moving muscles of `psd`

**Example**

```python
# Calculate the Twitch Index of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
fast_slope, slow_slope = EMGFlow.calc_twitch_slope(psd)
```





## `calc_sc`

**Description**

Calculates the Spectral Centroid (SC) of a signal. The SC is the "center of mass" of a signal after a Fourier transform is applied.

```python
calc_sc(psd)
```

**Theory**

SC is calculated as follows:
$$
\text{SC}=\frac{\sum_{i=f_0}^{f_N}i\cdot p_i}{\sum_{i=f_0}^{f_N} p_i}
$$
- $p_i$ <-- Power of normalized PSD at frequency $i$
- $f_0$ <-- Minimum frequency of the PSD
- $f_N$ <-- Maximum frequency of the PSD

(Roldán Jiménez et al., 2019)

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`SC`: float
- The SC of `psd`.

**Example**

```python
# Calculate the SC of Signal, for column 'EMG_zyg'
psd = (Signal['EMG_zyg'], 2000)
SC = EMGFlow.calc_sc(psd)
```





## `calc_sf`

**Description**

Calculates the Spectral Flatness (SF) of a signal. The SF measures noise in the magnitude spectrum.

```python
calc_sf(psd)
```

**Theory**

SF is calculated as follows:
$$
\text{SF}=\frac{\prod_{i=0}^{N-1}|p_i|^{\frac{1}{N}}}{\frac{1}{N}\sum_{i=0}^{N-1}|p_i|}
$$
- $p_i$ <-- $i$th element of PSD strength
- $N$ <-- Number of elements in PSD

(Nagineni et al., 2018)

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`SF`: float
- The SF of `psd`.

**Example**

```python
# Calculate the SF of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
SC = EMGFlow.calc_sf(psd)
```





## `calc_ss`

**Description**

Calculates the Spectral Spread (SS) of a signal. SS is also called the "instantaneous bandwidth", and measures the standard deviation around the SC.

```python
calc_ss(psd)
```

**Theory**

SS is calculated as follows:
$$
\text{SS}=\frac{\sum_{m=0}^{N-1}(m-\text{SC})^2 \cdot |X(m)|}{\sum_{m=0}^{N-1}
|X(m)|}
$$

(Nagineni et al., 2018)

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`SS`: float
- The SS of `psd`.

**Example**

```python
# Calculate the SS of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
SS = EMGFlow.calc_ss(psd)
```





## `calc_sd`

**Description**

Calculates the Spectral Decrease (SD) of a signal. SD is the decrease of the slope of the spectrum with respect to frequency.

```python
calc_sd(psd)
```

**Theory**

SD is calculated as follows:
$$
\text{SD}=\frac{\sum_{m=1}^{N-1}\frac{1}{N}(|X(m)|-|X(0)|)}{\sum_{m=1}^{N-1}|X(m)|}
$$

(Nagineni et al., 2018)

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`SD`: float
- The SD of `psd`.

**Example**

```python
# Calculate the SD of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
SD = EMGFlow.calc_sd(psd)
```





## `calc_se`

**Description**

Calculates the Spectral Entropy (SE) of a signal. SE is the Shannon entropy of the spectrum.

```python
calc_se(psd)
```

**Theory**

SE is calculated as follows:
$$
\text{SE}=-\sum_{i=1}^mp(dB_i)\log_2(p(dB_i))
$$

(Llanos et al., 2017)

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

**Returns**

`SE`: float
- The SE of `psd`.

**Example**

```python
# Calculate the SE of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
SEntropy = EMGFlow.calc_se(psd)
```





## `calc_sr`

**Description**

Calculates the Spectral Rolloff (SR) of a signal. The spectral rolloff point is the frequency of the PSD where 85% of the total spectral energy lies below it.

```python
calc_sr(psd, percent=0.85)
```

**Theory**

The actual threshold for SR can be set manually, but literature suggests that 85% is the best point.

(Tjoa, 2022)

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

`percent`: float
- The percentage of power that should be below the SR point. The default is 0.85.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

An exception is raised if `percent` is not between 0 and 1.

**Returns**

`SR`: float
- The SR of `psd`.

**Example**

```python
# Calculate the SR of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
SR = EMGFlow.calc_sr(psd)
```





## `calc_sbw`

**Description**

Calculates the Spectral Bandwidth (SBW) of a signal. The SBW calculates the difference between the upper and lower freqencies in the frequency band.

```python
calc_sbw(psd, p=2)
```

**Theory**

SBW has a parameter $p$ that can be adjusted to different values. Using a value of 2 will result in the standard deviation around the centroid.

SBW is calculated as follows:
$$
\text{SBW}=\left( \sum X(m)\cdot (m-\text{SC})^p \right)^{\frac{1}{p}}
$$

(Tjoa, 2022)

**Parameters**

`psd`: pd.DataFrame
- A Pandas dataframe containing a 'Frequency' and 'Power' column. Should be normalized.

`p`: int, optional (2)
- Order of the SBW. The default is 2, which gives the standard deviation around the centroid.

**Raises**

An exception is raised if `psd` does not only have columns 'Frequency' and 'Power'.

An exception is raised if `p` is not greater than 0.

**Returns**

`SBW`: float
- The SBW of `psd`.

**Example**

```python
# Calculate the SBW of Signal, for column 'EMG_zyg'
psd = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
SBW = EMGFlow.calc_sbw(psd)
```





## `extract_features`

**Description**

Extracts usable features from two sets of signal files (before and after being smoothed). Writes output to a new folder directory, as specified by the 'Feature' key value of the `path_names` dictionary. Output is both saved to the disk as a plaintext file, 'Features.csv', and is also returned as a dataframe object.

Components of a `Signal` dataframe:
- Has a column named `Time` containing time indexes
- `Time` indexes are all equally spaced apart
- Has one (or more) columns with any other name, holding the value of the electrical signal read at that time

All files contained within the folder and subfolder with the proper extension are assumed to be signal files. All signal files within the folder and subfolders should have the same change in time between entries.
```python
extract_features(path_names, sampling_rate, cols=None, expression=None, file_ext='csv', short_name=True)
```

**Theory**

This function requires a path to smoothed and unsmoothed data. This is because while time-series features are extracted from smoothed data, spectral features are not. High-frequency components of the signal can be lost in the smoothing, and we want to ensure the spectral features are as accurate as possible.

**Parameters**

`path_names`: dict-str
- A dictionary of file locations with keys for the stage in the processing pipeline.

`sampling_rate`: int, float
- Sampling rate of the signal files. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`cols`: str, optional (None)
- List of columns of the signal files to extract features from. The default is None, in which case features are extracted from every column except for 'Time'.

`expression`: str, optional (None)
- A regular expression. If provided, will only extract features from files whose names match the regular expression. The default is None.

`file_ext`: str, optional ('csv')
- File extension for files to read. Only reads files with this extension. The default is 'csv'.

`short_names`: bool, optional (True)
- If true, makes the key column of the feature files the relative path of the file. If false, uses the full system path. The default is True.

**Raises**

A warning is raised if `expression` does not match with any files in the folders provided.

An exception is raised if 'Bandpass', 'Smooth' or 'Feature' are not keys of the `path_names` dictionary provided.

An exception is raised if the 'Bandpass' and 'Smooth' filepaths do not contain the same files.

An exception is raised if a file cannot not be read in the 'Bandpass' or 'Smooth' filepaths.

An exception is raised if an unsupported file format was provided for `file_ext`.

An exception is raised if `expression` is not None or a valid regular expression.

**Returns**

`Features`: pd.DataFrame
- A Pandas dataframe of feature data for each file read. Each row is a different file analyzed, marked by the 'File\_ID' column. Additional columns show the values of the features extracted by the function.

**Example**

```python
path_names = EMGFlow.make_paths()
EMGFlow.make_sample_data(path_names)

sampling_rate = 2000
cols = ['EMG_zyg', 'EMG_cor']

# Extracts all features from the files in the 'Bandpass' path and the 'Smooth'
# path. Assumes the same files are in both paths.
features = EMGFlow.extract_features(path_names, sampling_rate, cols)
```





## Sources

Chowdhury, R. H., Reaz, M. B. I., Ali, M. A. B. M., Bakar, A. A. A., Chellappan, K., & Chang, Tae. G. (2013). Surface Electromyography Signal Processing and Classification Techniques. _Sensors (Basel, Switzerland)_, _13_(9), 12431–12466. [https://doi.org/10.3390/s130912431](https://doi.org/10.3390/s130912431)

Eyben, F., Scherer, K. R., Schuller, B. W., Sundberg, J., André, E., Busso, C., Devillers, L. Y., Epps, J., Laukka, P., Narayanan, S. S., & Truong, K. P. (2016). The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective Computing. _IEEE Transactions on Affective Computing_, _7_(2), 190–202. [https://doi.org/10.1109/TAFFC.2015.2457417](https://doi.org/10.1109/TAFFC.2015.2457417)

Giannakopoulos, T., & Pikrakis, A. (2014). Introduction to Audio Analysis. In T. Giannakopoulos & A. Pikrakis (Eds.), _Introduction to Audio Analysis_ (pp. 59–103). Academic Press. [https://doi.org/10.1016/B978-0-08-099388-1.00004-2](https://doi.org/10.1016/B978-0-08-099388-1.00004-2)

Hamedi, M., Salleh, S.-H., Astaraki, M., Noor, A. M., & Harris, A. R. A. (2014). Comparison of Multilayer Perceptron and Radial Basis Function Neural Networks for EMG-Based Facial Gesture Recognition. In H. A. Mat Sakim & M. T. Mustaffa (Eds.), The 8th International Conference on Robotic, Vision, Signal Processing & Power Applications (Vol. 291, pp. 285–294). Springer Singapore. https://doi.org/10.1007/978-981-4585-42-2_33

Hegedus, A., Trzaskoma, L., Soldos, P., Tuza, K., Katona, P., Greger, Z., Zsarnoczky-Dulhazi, F., & Kopper, B. (2020). Adaptation of Fatigue Affected Changes in Muscle EMG Frequency Characteristics for the Determination of Training Load in Physical Therapy for Cancer Patients. _Pathology Oncology Research_, _26_(2), 1129–1135. [https://doi.org/10.1007/s12253-019-00668-3](https://doi.org/10.1007/s12253-019-00668-3)

Llanos, F., Alexander, J. M., Stilp, C. E., & Kluender, K. R. (2017). Power spectral entropy as an information-theoretic correlate of manner of articulation in American English. _The Journal of the Acoustical Society of America_, _141_(2), EL127–EL133. [https://doi.org/10.1121/1.4976109](https://doi.org/10.1121/1.4976109)

McComas, A. J. (1998). Oro-facial muscles: Internal structure, function and ageing. _Gerodontology_, _15_(1), 3–14. [https://doi.org/10.1111/j.1741-2358.1998.00003.x](https://doi.org/10.1111/j.1741-2358.1998.00003.x)

Nagineni, S., Taran, S., & Bajaj, V. (2018). Features based on variational mode decomposition for identification of neuromuscular disorder using EMG signals. _Health Information Science and Systems_, _6_(1), 13. [https://doi.org/10.1007/s13755-018-0050-4](https://doi.org/10.1007/s13755-018-0050-4)

Phinyomark, A., Limsakul, C., & Phukpattaranont, P. (2009). A Novel Feature Extraction for Robust EMG Pattern Recognition. 1(1).

Roldán Jiménez, C., Bennett, P., Ortiz García, A., & Cuesta Vargas, A. I. (2019). Fatigue Detection during Sit-To-Stand Test Based on Surface Electromyography and Acceleration: A Case Study. _Sensors (Basel, Switzerland)_, _19_(19), 4202. [https://doi.org/10.3390/s19194202](https://doi.org/10.3390/s19194202)

Spiewak, C., Islam, M. R., Assad-Uz-Zaman, M., & Rahman, M. (2018). A Comprehensive Study on EMG Feature Extraction and Classifiers. _Open Access Journal of Biomedical Engineering and Its Applications_, _1_. [https://doi.org/10.32474/OAJBEB.2018.01.000104](https://doi.org/10.32474/OAJBEB.2018.01.000104)

Tjoa, S. (2022). _Spectral Features_. Music Information Retrieval. [https://musicinformationretrieval.com/spectral_features.html](https://musicinformationretrieval.com/spectral_features.html)

Tkach, D., Huang, H., & Kuiken, T. A. (2010). Study of stability of time-domain features for electromyographic pattern recognition. _Journal of NeuroEngineering and Rehabilitation_, _7_, 21. [https://doi.org/10.1186/1743-0003-7-21](https://doi.org/10.1186/1743-0003-7-21)

Too, J., Abdullah, A. R., Mohd Saad, N., & Tee, W. (2019). EMG Feature Selection and Classification Using a Pbest-Guide Binary Particle Swarm Optimization. _Computation_, _7_(1), Article 1. [https://doi.org/10.3390/computation7010012](https://doi.org/10.3390/computation7010012)