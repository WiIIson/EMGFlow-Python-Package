# `SignalFilterer` Module Feature Extraction Documentation

---

## Importing

The following functions require the `EMGFlow.SignalFilterer` module, which can be imported with:
```python
import EMGFlow.SignalFilterer as ESIG
```

---

## Basic Time-Series Statistics

The `AnalyzeSignal` function calculates some basic statistics that don't involve their own functions. This includes:
- Minimum voltage
- Maximum voltage
- Mean voltage
- Standard deviation of voltage
- Skew of voltage
- Kurtosis of voltage
- Maximum frequency

The values returned will be a voltage equivalent to the units used in the data provided.

Most of these are commonly understood concepts:
- **Minimum** is calculated with `np.min`
- **Maximum** is calculated with `np.max`
- **Mean** is calculated with `np.mean`
- **Standard Deviation** is calculated with `np.std`

Skew and kurtosis are lesser known statistical measurements.

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
$$k=\frac{1}{N}\sum_{i=1}^N\left(\frac{x_i-\mu}{\sigma}\right)^4$$
- $\mu$ <-- Mean
- $\sigma$ <-- Standard deviation
- $N$ <-- Number of data points

**Kurtosis** is calculated with `scipy.stats.kurtosis`

---

## `CalcIEMG`

**Description**

Calculates the Integrated EMG (IEMG) of the signal. The IEMG measures the area under the curve of the signal, which can provide useful information about muscle activity.

```python
CalcIEMG(Signal, col, sr)
```

**Theory**

In the reference, the IEMG does not account for the sampling rate. Two signal recordings with the same shape but different sampling rate would have different results since we are integrating with respect to time. As such, the calculation made here will include multiplying by sampling rate.

The IEMG is calculated as follows:
$$\text{IEMG}=s_r\sum_{i=1}^N|x_i|$$
- $s_r$ <-- Sampling rate
- $N$ <-- Number of data points

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

`sr`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

**Returns**

`CalcIEMG`: float
- Returns the value of the IEMG.

**Example**

```python
# Calculate the IEMG of SignalDF, for column 'column1'
IEMG = ESIG.CalcIEMG(SignalDF, 'column1', 2000)
```

---

## `CalcMAV`

**Description**

Calculates the Mean Absolute Value (MAV) of the signal.

```python
CalcMAV(Signal, col)
```

**Theory**

The MAV is calculated as follows:
$$\text{MAV}=\frac{1}{N}\sum_{i=1}^N|x_i|$$
- $N$ <-- Number of data points

(Tkach et al., 2010)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcMAV`: float
- Returns the value of the MAV.

**Example**

```python
# Calculate the MAV of SignalDF, for column 'column1'
MAV = ESIG.CalcMAV(SignalDF, 'column1', 2000)
```


---

## `CalcMMAV`

**Description**

Calculates the Modified Mean Absolute Value (MMAV) of the signal. The MMAV is an alteration of MAV that gives more weight to values in the middle of the signal to reduce error from the beginning and end of the signal.

**Theory**

The MMAV is identical to MAV, except it introduces a weight to the calculation. Values are given a weight of 1 when they are between the 25th and 74th percentile, and 0.5 outside. The article describing the MMAV also listed another modification, MMAV2, but the description appeared to be flawed, and as such the measure was not included.

The MMAV is calculated as follows:
$$\text{MMAV}=\frac{1}{N}\sum_{i=1}^N|x_iw_i|$$
$$w_i=\left\{ \begin{matrix} 1 & \text{if }0.25N\le n\le 0.75N \\\ 0.5 & \text{otherwise} \end{matrix} \right.$$
- $N$ <-- Number of data points

(Chowdhury et al., 2013)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcMMAV`: float
- Returns the value of the MMAV.

**Example**

```python
# Calculate the MMAV of SignalDF, for column 'column1'
MMAV = ESIG.CalcMMAV(SignalDF, 'column1', 2000)
```

---

## `CalcSSI`

**Description**

Calculates the Simple Square Integral (SSI) of the signal. See more about the SSI.

```python
CalcSSI(Signal, col, sr)
```

**Theory**

In the reference, the SSI does not account for the sampling rate. Two signal recordings with the same shape but different sampling rate would have different results since we are integrating with respect to time. As such, the calculation made here will include multiplying by sampling rate.

The SSI is calculated as follows:
$$\text{SSI}=s_r^2\sum_{i=1}^N|x_i|^2$$
- $s_r$ <-- Sampling rate
- $N$ <-- Number of data points

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

`sr`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

**Returns**

`CalcSSI`: float
- Returns the value of the SSI.

**Example**

```python
# Calculate the SSI of SignalDF, for column 'column1'
SSI = ESIG.CalcSSI(SignalDF, 'column1', 2000)
```

---

## `CalcVAR`

**Description**

Calculates the Variance (VAR) of the signal. The variance provides information about the power of the EMG signal.

```python
CalcVAR(Signal, col)
```

**Theory**

The VAR is calculated as follows:
$$\text{VAR}=\frac{1}{N-1}\sum_{i=1}^Nx_i^2$$

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcVAR`: float
- Returns the value of the VAR.

**Example**

```python
# Calculate the VAR of SignalDF, for column 'column1'
VAR = ESIG.CalcVAR(SignalDF, 'column1')
```

---

## `CalcVOrder`

**Description**

Calculates the V-Order of a signal.

```python
CalcVOrder(Signal, col)
```

**Theory**

The V-Order is calculated using the $v$-operator, essentially working like a Euclidean distance to the $v$th order. One study indicates that the best value for $v$ is 2, meaning the V-Order is just the square root of the VAR feature.

The V-Order is calculated as follows:
$$\text{vORDER}=\sqrt{\text{VAR}}$$

(Tkach et al., 2010)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcVOrder`: float
- Returns the value of the V-Order.

**Example**

```python
# Calculate the V-Order of SignalDF, for column 'column1'
VOrder = ESIG.CalcVOrder(SignalDF, 'column1')
```

---

## `CalcRMS`

**Description**

Calculates the Root Mean Square (RMS) of a signal. The RMS provides information about the constant force, and non-fatiguing contractions of the muscles.

```python
CalcRMS(Signal, col)
```

**Theory**

The RMS is calculated as follows:
$$\text{RMS}=\sqrt{\frac{1}{N}\sum_{i=1}^N}|x_i|^2$$
- $N$ <-- Number of data points

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcRMS`: float
- Returns the value of the RMS.

**Example**

```python
# Calculate the RMS of SignalDF, for column 'column1'
RMS = ESIG.CalcRMS(SignalDF, 'column1')
```

---

## `CalcWL`

**Description**

Calculates the Waveform Length (WL) of a signal. The WL provides information about the amplitude, frequency, and duration of the signal.

```python
CalcWL(Signal, col)
```

**Theory**

The WL is calculated as follows:
$$\text{WL}=\sum_{i=1}^{N-1}|x_{i+1}-x_i|$$
- $N$ <-- Number of data points

(Spiewak et al., 2018)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcWL`: float
- Returns the value of the WL.

**Example**

```python
# Calculate the WL of SignalDF, for column 'column1'
WL = ESIG.CalcWL(SignalDF, 'column1')
```

---

## `CalcWAMP`

**Description**

Calculate the Willison Amplitude (WAMP) of a signal. The WAMP measures the number of times an EMG amplitude exceeds a given threshold.

```python
CalcWAMP(Signal, col, threshold)
```

**Theory**

Thresholds for the WAMP are commonly chosen within the 50-100 mV range. The WAMP counts the number of recorded times in the signal that the charge is greater than the threshold, so it can be affected by the sampling rate. If datasets with different sampling rates are being compared, it may be beneficial to normalize each result by the length of the signal.

When choosing a value, pass it in terms of the same units being used in the data.

The WAMP is calculated as follows:
$$\text{WAMP}=\sum_{i=1}^{N-1}f(|x_{i+1}-x_i|)$$
$$f(x)=\left\{\begin{matrix} 1 & \text{if }x>\epsilon \\\ 0 & \text{otherwise} \end{matrix}\right.$$
- $N$ <-- Number of data points
- $\epsilon$ <-- Voltage change threshold

(Tkach et al., 2010)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

`threshold`: float
- Voltage threshold for the WAMP.

**Returns**

`CalcWAMP`: int
- Returns the value of the WAMP.

**Example**

```python
# Calculate the WL of SignalDF, for column 'column1'
WAMP = ESIG.CalcWAMP(SignalDF, 'column1', 55)
```

---

## `CalcLOG`

**Description**

Calculates the Log-Detector (LOG) of a signal. The LOG provides an estimate of the force exerted by the muscle.

```python
CalcLOG(Signal, col)
```

**Theory**

The LOG is calculated as follows:
$$\text{LOG}=e^{\frac{1}{N}\sum_{i=1}^N\log(|x_k|)}$$
- $N$ <-- Number of data points

(Tkach et al., 2010)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcLOG`: float
- Returns the value of the LOG.

**Example**

```python
# Calculate the LOG of SignalDF, for column 'column1'
LOG = ESIG.CalcLOG(SignalDF, 'column1')
```

---

## `CalcMFL`

**Description**

Calculates the Maximum Fractal Length (MFL) of a signal. The MFL measures the activation of low-level muscle contractions.

```python
CalcMFL(Signal, col)
```

**Theory**

The MFL is calculated as follows:
$$\text{MFL}=\log\left(\sqrt{\sum_{i=1}^{N-1}(x_{i+1}-x_i)^2}\right)$$
- $N$ <-- Number of data points

(Too et al., 2019)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcMFL`: float
- Returns the value of the MFL.

**Example**

```python
# Calculate the MFL of SignalDF, for column 'column1'
MFL = ESIG.CalcMFL(SignalDF, 'column1')
```

---

## `CalcAP`

**Description**

Calculates the Average Power (AP) of a signal. The AP measures the energy distribution of the signal.

```python
CalcAP(Signal, col)
```

**Theory**

The AP is calculated as follows:
$$\text{AP}=\frac{1}{N}\sum_{i=1}^Nx_i^2$$
- $N$ <-- Number of data points

(Too et al., 2019)

**Parameters**

`Signal`: pd.DataFrame 
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

**Returns**

`CalcAP`: float
- Returns the value of the AP.

**Example**

```python
# Calculate the AP of SignalDF, for column 'column1'
AP = ESIG.CalcMFL(SignalDF, 'column1')
```

---

## `CalcSpecFlux`

**Description**

Calculates the Spectral Flux of a signal. Spectral Flux measures the change in spectrums between two signals, or two sections of a signal.

`CalcSpecFlux` behaves differently, depending on if it is given a Pandas DataFrame or float. Providing a DataFrame treats the dataframe as a new signal, and finds the spectral flux between them. Providing a float $n$ will provide the spectral flux between the first $n$% of the signal, and the second $n-1$% of the signal.

The call to `CalcSpecFlux` within `AnalyzeSignals` uses a default value of `diff=0.5`.

```python
CalcSpecFlux(Signal1, diff, col, sr, diff_sr=None)
```

**Theory**

Spectral Flux is used to compare two different signals together. The applications of this are more difficult to implement, so there is no one function to handle this.

Spectral Flux is calculated as follows:
```math
\text{FL}_{i,i-1}=\sum_{k=1}^{Wf_L}(\text{EN}_i(k)-\text{EN}_{i-1}(k))^2
```

(Giannakopoulos & Pikrakis, 2014)

**Parameters**

`Signal1`: pd.DataFrame
- Should have one column called "`Time`" for the time indexes, and other named columns for the values at those times.

`diff`: pd.DataFrame, float
- Either a new signal DataFrame, or a decimal indicating the percentage of the signal to split.

`col`: str
- String name of a column in `Signal` the filters are being applied to.

`sr`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`diff_sr`: int/float (None)
- Sampling rate of `diff` if it has a different sampling rate than the first signal. If left None, will assume both signals are using the same sampling rate.

**Returns**

`CalcSpecFlux`: float
- Returns the value of the Spectral Flux.

**Example**

```python
# Calculate the Spectral Flux of Signal1DF, for column 'column1'
AP = ESIG.CalcSpecFlux(Signal1DF, Signal2DF, 'column1', 2000)
```

---

## `CalcTwitchRatio`

**Description**

Calculates the Twitch Ratio of a Signal based on its power distribution. 

```python
CalcTwitchRatio(psd, freq=60)
```

**Theory**

This metric uses a proposed muscle separation theory put forward by this project. This measure is typically used in audio feature extraction, separating the high and low frequencies. This kind of separation is not typically done in EMG feature extraction. However, literature suggests that there are both high and low frequency muscle activations (Penney, 2022) that can be separated by an approximately 60Hz threshold (Hegedus et al., 2020). Since these muscles are present in the face (McComas, 1998), this experimental feature is being added by applying this audio feature in a new context.

Twitch Ratio is an adaptation of Alpha Ratio (Eyben et al., 2016).

Twitch Ratio is calculated as follows:
$$\text{TR}=\frac{\sum_{i=f_0}^{f_t} p_i}{\sum_{i=f_t}^{f_N}p_i}$$
- $p_i$ <-- Power of normalized PSD at frequency $i$
- $f_0$ <-- Minimum frequency of the PSD
- $f_t$ <-- Threshold frequency of the PSD
- $f_N$ <-- Maximum frequency of the PSD

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

`freq`: int/float (60Hz)
- Frequency threshold of the calculation. Defaults to 60Hz, as that is the theorized frequency threshold between slow-twitching and fast-twitching muscles.

**Returns**

`CalcTwitchRatio`: float
- Returns the value of the Twitch Ratio

**Example**

```python
# Calculate the Twitch Ratio of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
TR = ESIG.CalcTwitchRatio(psd)
```

---

## `CalcTwitchIndex`

**Description**

Calculates the Twitch Index of a Signal based on its power distribution. 

```python
CalcTwitchIndex(psd, freq=60)
```

**Theory**

This metric uses a proposed muscle separation theory put forward by this project. This measure is typically used in audio feature extraction, separating the high and low frequencies. This kind of separation is not typically done in EMG feature extraction. However, literature suggests that there are both high and low frequency muscle activations (slow twitching muscles, and fast twitching muscles) that can be separated by an approximately 60Hz threshold. As such, this experimental feature is being added by applying this audio feature in a new context.

Twitch Index is an adaptation of the Hammarberg index (Eyben et al., 2016).

Twitch Index is calculated as follows:
$$\text{TR}=\frac{\max\left(\sum_{i=f_0}^{f_t} p_i\right)}{\max\left(\sum_{i=f_t}^{f_N}p_i\right)}$$
- $p_i$ <-- Power of normalized PSD at frequency $i$
- $f_0$ <-- Minimum frequency of the PSD
- $f_t$ <-- Threshold frequency of the PSD
- $f_N$ <-- Maximum frequency of the PSD

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

`freq`: int/float (60Hz)
- Frequency threshold of the calculation. Defaults to 60Hz, as that is the theorized frequency threshold between slow-twitching and fast-twitching muscles.

**Returns**

`CalcTwitchRatio`: float
- Returns the value of the Twitch Ratio

**Example**

```python
# Calculate the Twitch Index of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
TI = ESIG.CalcTwitchIndex(psd)
```

---

## `CalcTwitchSlope`

**Description**

Calculates the Twitch Slope of a Signal based on its power distribution.

```python
CalcTwitchIndex(psd, freq=60)
```

**Theory**

This metric uses a proposed muscle separation theory put forward by this project. This measure is typically used in audio feature extraction, separating the high and low frequencies. This kind of separation is not typically done in EMG feature extraction. However, literature suggests that there are both high and low frequency muscle activations (slow twitching muscles, and fast twitching muscles) that can be separated by an approximately 60Hz threshold. As such, this experimental feature is being added by applying this audio feature in a new context.

Twitch Slope is an adaptation of spectral slope (Eyben et al., 2016).

`CalcTwitchSlope` uses the `np.linalg.lstsq` to find the slope of the line of best fit for the two regions separated by frequency, and returns both values.

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

`freq`: int/float (60Hz)
- Frequency threshold of the calculation. Defaults to 60Hz, as that is the theorized frequency threshold between slow-twitching and fast-twitching muscles.

**Returns**

`CalcTwitchSlope`: float, float
- Returns both of the values of the Twitch Ratio.

**Example**

```python
# Calculate the Twitch Index of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
TS_Fast, TS_Slow = ESIG.CalcTwitchSlope(psd)
```

---

## `CalcSC`

**Description**

Calculates the Spectral Centroid (SC) of a signal. The SC is the "center of mass" of a signal after a Fourier transform is applied.

```python
CalcSC(psd)
```

**Theory**

SC is calculated as follows:
$$\text{SC}=\frac{\sum_{i=f_0}^{f_N}i\cdot p_i}{\sum_{i=f_0}^{f_N} p_i}$$
- $p_i$ <-- Power of normalized PSD at frequency $i$
- $f_0$ <-- Minimum frequency of the PSD
- $f_N$ <-- Maximum frequency of the PSD

(Roldán Jiménez et al., 2019)

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

**Returns**

`CalcSC`: float
- Returns the value of the SC.

**Example**

```python
# Calculate the SC of SignalDF, for column 'column1'
psd = (SignalDF['column1'], 2000)
SC = ESIG.CalcSC(psd)
```

---

## `CalcSF`

**Description**

Calculates the Spectral Flatness (SF) of a signal. The SF measures noise in the magnitude spectrum.

```python
CalcSF(psd)
```

**Theory**

SF is calculated as follows:
$$\text{SF}=\frac{\prod_{i=0}^{N-1}|p_i|^{\frac{1}{N}}}{\frac{1}{N}\sum_{i=0}^{N-1}|p_i|}$$
- $p_i$ <-- $i$th element of PSD strength
- $N$ <-- Number of elements in PSD

(Nagineni et al., 2018)

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

**Returns**

`CalcSF`: float
- Returns the value of the SF.

**Example**

```python
# Calculate the SF of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
SC = ESIG.CalcSF(psd)
```

---

## `CalcSS`

**Description**

Calculates the Spectral Spread (SS) of a signal. SS is also called the "instantaneous bandwidth", and measures the standard deviation around the SC.

```python
CalcSS(psd)
```

**Theory**

SS is calculated as follows:
$$\text{SS}=\frac{\sum_{m=0}^{N-1}(m-\text{SC})^2 \cdot |X(m)|}{\sum_{m=0}^{N-1}
|X(m)|}$$

(Nagineni et al., 2018)

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

**Returns**

`CalcSS`: float
- Returns the value of the SS.

**Example**

```python
# Calculate the SS of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
SS = ESIG.CalcSS(psd)
```

---

## `CalcSDec`

**Description**

Calculates the Spectral Decrease (SDec) of a signal. SDec is the decrease of the slope of the spectrum with respect to frequency.

```python
CalcSDec(psd)
```

**Theory**

SDec is calculated as follows:
$$\text{SDec}=\frac{\sum_{m=1}^{N-1}\frac{1}{N}(|X(m)|-|X(0)|)}{\sum_{m=1}^{N-1}|X(m)|}$$

(Nagineni et al., 2018)

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

**Returns**

`CalcSDec`: float
- Returns the value of the SDec.

**Example**

```python
# Calculate the SDec of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
SDec = ESIG.CalcSDec(psd)
```

---

## `CalcSEntropy`

**Description**

Calculates the Spectral Entropy of a signal. Spectral Entropy is the Shannon entropy of the spectrum.

```python
CalcSEntropy(psd)
```

**Theory**

Spectral Entropy is calculated as follows:
$$\text{Spectral Entropy}=-\sum_{i=1}^mp(dB_i)\log_2(p(dB_i))$$

(Llanos et al., 2017)

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.


**Returns**

`CalcSEntropy`: float
- Returns the value of the SEntropy.

**Example**

```python
# Calculate the SEntropy of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
SEntropy = ESIG.CalcSEntropy(psd)
```

---

## `CalcSRoll`

**Description**

Calculates the Spectral Rolloff (SRoll) of a signal. The spectral rolloff point is the frequency of the PSD where 85% of the total spectral energy lies below it.

```python
CalcSRoll(psd, percent=0.85)
```

**Theory**

The actual threshold for SRoll can be set manually, but literature suggests that 85% is the best point.

(Tjoa, 2022)

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

`percent`: float
- Percentage threshold for SRoll.

**Returns**

`CalcSRoll`: float
- Returns the value of the SRoll.

**Example**

```python
# Calculate the SRoll of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
SRoll = ESIG.CalcSRoll(psd)
```

---

## `CalcSBW`

**Description**

Calculates the Spectral Bandwidth (SBW) of a signal. The SBW calculates the difference between the upper and lower freqencies in the frequency band.

```python
CalcSBW(psd, p=2)
```

**Theory**

SBW has a parameter $p$ that can be adjusted to different values. Using a value of 2 will result in the standard deviation around the centroid.

SBW is calculated as follows:
$$\text{SBW}=\left( \sum X(m)\cdot (m-\text{SC})^p \right)^{\frac{1}{p}}$$

(Verma, 2021)

**Parameters**

`psd`: pd.DataFrame
- Normalized PSD of a signal. Should have a "frequency" and "power" column.

`p`: int
- Parameter of $p$ in calculation of SBW

**Returns**

`CalcSBW`: float
- Returns the value of the SBW.

**Example**

```python
# Calculate the SBW of SignalDF, for column 'column1'
psd = ESIG.EMG2PSD(SignalDF['column1'], 2000)
SBW = ESIG.CalcSBW(psd)
```

---

## Sources

Chowdhury, R. H., Reaz, M. B. I., Ali, M. A. B. M., Bakar, A. A. A., Chellappan, K., & Chang, Tae. G. (2013). Surface Electromyography Signal Processing and Classification Techniques. _Sensors (Basel, Switzerland)_, _13_(9), 12431–12466. [https://doi.org/10.3390/s130912431](https://doi.org/10.3390/s130912431)

Eyben, F., Scherer, K. R., Schuller, B. W., Sundberg, J., André, E., Busso, C., Devillers, L. Y., Epps, J., Laukka, P., Narayanan, S. S., & Truong, K. P. (2016). The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective Computing. _IEEE Transactions on Affective Computing_, _7_(2), 190–202. [https://doi.org/10.1109/TAFFC.2015.2457417](https://doi.org/10.1109/TAFFC.2015.2457417)

Giannakopoulos, T., & Pikrakis, A. (2014). Introduction to Audio Analysis. In T. Giannakopoulos & A. Pikrakis (Eds.), _Introduction to Audio Analysis_ (pp. 59–103). Academic Press. [https://doi.org/10.1016/B978-0-08-099388-1.00004-2](https://doi.org/10.1016/B978-0-08-099388-1.00004-2)

Hegedus, A., Trzaskoma, L., Soldos, P., Tuza, K., Katona, P., Greger, Z., Zsarnoczky-Dulhazi, F., & Kopper, B. (2020). Adaptation of Fatigue Affected Changes in Muscle EMG Frequency Characteristics for the Determination of Training Load in Physical Therapy for Cancer Patients. _Pathology Oncology Research_, _26_(2), 1129–1135. [https://doi.org/10.1007/s12253-019-00668-3](https://doi.org/10.1007/s12253-019-00668-3)

Llanos, F., Alexander, J. M., Stilp, C. E., & Kluender, K. R. (2017). Power spectral entropy as an information-theoretic correlate of manner of articulation in American English. _The Journal of the Acoustical Society of America_, _141_(2), EL127–EL133. [https://doi.org/10.1121/1.4976109](https://doi.org/10.1121/1.4976109)

McComas, A. J. (1998). Oro-facial muscles: Internal structure, function and ageing. _Gerodontology_, _15_(1), 3–14. [https://doi.org/10.1111/j.1741-2358.1998.00003.x](https://doi.org/10.1111/j.1741-2358.1998.00003.x)

Nagineni, S., Taran, S., & Bajaj, V. (2018). Features based on variational mode decomposition for identification of neuromuscular disorder using EMG signals. _Health Information Science and Systems_, _6_(1), 13. [https://doi.org/10.1007/s13755-018-0050-4](https://doi.org/10.1007/s13755-018-0050-4)

Penney, S. (2022). _Fast-Twitch Vs. Slow-Twitch Muscle Fiber Types + Training Tips | NASM_. [https://blog.nasm.org/fitness/fast-twitch-vs-slow-twitch](https://blog.nasm.org/fitness/fast-twitch-vs-slow-twitch)

Roldán Jiménez, C., Bennett, P., Ortiz García, A., & Cuesta Vargas, A. I. (2019). Fatigue Detection during Sit-To-Stand Test Based on Surface Electromyography and Acceleration: A Case Study. _Sensors (Basel, Switzerland)_, _19_(19), 4202. [https://doi.org/10.3390/s19194202](https://doi.org/10.3390/s19194202)

Spiewak, C., Islam, M. R., Assad-Uz-Zaman, M., & Rahman, M. (2018). A Comprehensive Study on EMG Feature Extraction and Classifiers. _Open Access Journal of Biomedical Engineering and Its Applications_, _1_. [https://doi.org/10.32474/OAJBEB.2018.01.000104](https://doi.org/10.32474/OAJBEB.2018.01.000104)

Tjoa, S. (2022). _Spectral Features_. Music Information Retrieval. [https://musicinformationretrieval.com/spectral_features.html](https://musicinformationretrieval.com/spectral_features.html)

Tkach, D., Huang, H., & Kuiken, T. A. (2010). Study of stability of time-domain features for electromyographic pattern recognition. _Journal of NeuroEngineering and Rehabilitation_, _7_, 21. [https://doi.org/10.1186/1743-0003-7-21](https://doi.org/10.1186/1743-0003-7-21)

Too, J., Abdullah, A. R., Mohd Saad, N., & Tee, W. (2019). EMG Feature Selection and Classification Using a Pbest-Guide Binary Particle Swarm Optimization. _Computation_, _7_(1), Article 1. [https://doi.org/10.3390/computation7010012](https://doi.org/10.3390/computation7010012)

Verma, Y. (2021, September 19). _A Tutorial on Spectral Feature Extraction for Audio Analytics_. Analytics India Magazine. [https://analyticsindiamag.com/a-tutorial-on-spectral-feature-extraction-for-audio-analytics/](https://analyticsindiamag.com/a-tutorial-on-spectral-feature-extraction-for-audio-analytics/)