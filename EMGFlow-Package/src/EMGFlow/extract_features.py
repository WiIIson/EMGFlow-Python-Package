import scipy
import pandas as pd
import numpy as np
import os
import re
from tqdm import tqdm
import warnings

from .access_files import *
from .preprocess_signals import emg_to_psd

#
# =============================================================================
#

"""
A collection of functions for extracting features.
"""

#
# =============================================================================
#


def calc_iemg(Signal, col, sr):
    """
    Calculate the Integreated EMG (IEMG) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.
    sr : float
        Sampling rate of the Signal.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if sr is less or equal to 0.

    Returns
    -------
    IEMG : float
        IEMG of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    if sr <= 0:
        raise Exception("Sampling rate cannot be 0 or negative")
    
    IEMG = np.sum(np.abs(Signal[col]) * sr)
    return IEMG

#
# =============================================================================
#

# Calculate the Mean Absolute Value (MAV) of a signal
def calc_mav(Signal, col):
    """
    Calculate the Mean Absolute Value (MAV) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    MAV : float
        MAV of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    N = len(Signal[col])
    MAV = np.sum(np.abs(Signal[col])) / N
    return MAV

#
# =============================================================================
#

def calc_mmav1(Signal, col):
    """
    Calculate the Modified Mean Absolute Value 1 (MMAV1) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    MMAV1 : float
        MMAV1 of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    N = len(Signal[col])
    vals = list(np.abs(Signal[col]))
    total = 0
    for n in range(N):
        if (0.25*N <= n) and (n <= 0.75*N):
            total += vals[n]
        else:
            total += 0.5 * vals[n]
    MMAV1 = total/N
    return MMAV1

#
# =============================================================================
#

def calc_mmav2(Signal, col):
    """
    Calculate the Modified Mean Absolute Value 2 (MMAV2) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    MMAV2 : float
        MMAV2 of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    N = len(Signal[col])
    vals = list(np.abs(Signal[col]))
    total = 0
    for n in range(N):
        if (0.25*N <= n) and (n <= 0.75*N):
            total += vals[n]
        elif (0.25*N > n):
            total += (4*n/N) * vals[n]
        else:
            total += (4*(n-N)/N) * vals[n]
    MMAV2 = total/N
    return MMAV2

#
# =============================================================================
#

def calc_ssi(Signal, col, sr):
    """
    Calculate the Simple Square Integreal (SSI) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.
    sr : float
        Sampling rate of the Signal.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if sr is less or equal to 0.

    Returns
    -------
    SSI : float
        SSI of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    if sr <= 0:
        raise Exception("Sampling rate cannot be 0 or negative")
    
    SSI = np.sum((np.abs(Signal[col]) * sr) ** 2)
    return SSI

#
# =============================================================================
#

def calc_var(Signal, col):
    """
    Calculate the Variance (VAR) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    VAR : float
        VAR of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    N = len(Signal[col])
    VAR = 1/(N - 1) * np.sum(Signal[col] ** 2)
    return VAR

#
# =============================================================================
#

def calc_vorder(Signal, col):
    """
    Calculate the V-Order of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    vOrder : float
        V-Order of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    vOrder = np.sqrt(calc_var(Signal, col))
    return vOrder

#
# =============================================================================
#

def calc_rms(Signal, col):
    """
    Calculate the Root Mean Square (RMS) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    RMS : float
        RMS of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    N = len(Signal)
    RMS = np.sqrt((1/N) * np.sum(Signal[col] ** 2))
    return RMS

#
# =============================================================================
#

def calc_wl(Signal, col):
    """
    Calculate the Waveform Length (WL) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    WL : float
        WL of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    N = len(Signal[col])
    vals = list(Signal[col])
    diff = np.array([np.abs(vals[i + 1] - vals[i]) for i in range(N - 1)])
    WL = np.sum(diff)
    return WL

#
# =============================================================================
#

def calc_wamp(Signal, col, threshold):
    """
    Calculate the Willison Amplitude (WAMP) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.
    threshold : float
        Threshold of the WAMP.
        
    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    WAMP : int
        WAMP of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    N = len(Signal[col])
    vals = list(Signal[col])
    diff = np.array([np.abs(vals[i + 1] - vals[i]) for i in range(N - 1)])
    WAMP = np.sum(diff > threshold)
    return WAMP

#
# =============================================================================
#

def calc_log(Signal, col):
    """
    Calculate the Log Detector (LOG) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    LOG : float
        LOG of the Signal.
    
    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    N = len(Signal[col])
    ex = (1/N) * np.sum(np.log(Signal[col]))
    LOG = np.e ** ex
    return LOG

#
# =============================================================================
#

def calc_mfl(Signal, col):
    """
    Calculate the Maximum Fractal Length (MFL) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    MFL : float
        MFL of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    vals = Signal[col]
    N = len(Signal[col])
    diff = np.array([np.abs(vals[i + 1] - vals[i]) for i in range(N - 1)])
    MFL = np.log(np.sqrt(np.sum(diff ** 2)))
    return MFL

#
# =============================================================================
#

def calc_ap(Signal, col):
    """
    Calculate the Average Power (AP) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the summary to.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.

    Returns
    -------
    AP : float
        AP of the Signal.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    AP = np.sum(Signal[col] ** 2) / len(Signal[col])
    return AP

#
# =============================================================================
#

def calc_spec_flux(Signal1, diff, col, sr, diffSr=None):
    """
    Calculate the spectral flux of a Signal.

    Parameters
    ----------
    Signal1 : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    diff : float, DataFrame
        The divisor of the calculation. If a percentage is provided, it will
        calculate the spectral flux of the percentage of the Signal with one
        minus the percentage of the Signal.
    col : str
        Column of the Signal to apply the summary to. If a second signal is
        provided for diff, a column of the same name should be available for
        use.
    sr : float
        Sampling rate of the Signal.
    diffSr : float, optional
        Sampling rate for the second Signal if provided. The default is None,
        in which case if a second Signal is provided, the sampling rate is
        assumed to be the same as the first.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if sr is less or equal to 0.
    Exception
        An exception is raised if diff is a float and not between 0 and 1.
    Exception
        An exception is raised if diff is a dataframe and does not contain col.
    Exception
        An exception is raised if diffSr is less or equal to 0.

    Returns
    -------
    flux : float
        Spectral flux of the Signal.

    """
    
    if col not in list(Signal1.columns.values):
        raise Exception("Column " + col + " not in Signal1")
        
    if sr <= 0:
        raise Exception("Sampling rate cannot be 0 or negative")
    
    # Separate Signal1 by div and find spectral flux
    if isinstance(diff, float):
        if diff >= 1 or diff <= 0:
            raise Exception("diff must be a float between 0 and 1")
        
        # Find column divider index
        diff_ind = int(len(Signal1[col]) * diff)
        # Take the PSD of each signal
        psd1 = emg_to_psd(Signal1[col][:diff_ind], samplingRate=sr)
        psd2 = emg_to_psd(Signal1[col][diff_ind:], samplingRate=sr)
        # Calculate the spectral flux
        flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
        
    # Find spectral flux of Signal1 by div
    elif isinstance(diff, pd.DataFrame):
        if col not in list(diff.columns.values):
            raise Exception("Column " + col + " not in diff")
        
        # If no second sampling rate, assume same sampling rate as first Signal
        if diffSr == None: diffSr = sr
        
        if diffSr <= 0:
            raise Exception("Sampling rate cannot be 0 or negative")
        # Take the PSD of each signal
        psd1 = emg_to_psd(Signal1[col], samplingRate=sr)
        psd2 = emg_to_psd(diff[col], samplingRate=diffSr)
        # Calculate the spectral flux
        flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
    
    return flux

#
# =============================================================================
#

def calc_mdf(psd):
    """
    Calculate the Median Frequency (MDF) of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.
    
    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    med_freq : int, float
        The MDF of the psd provided.
    
    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    prefix_sum = psd['Power'].cumsum()
    suffix_sum = psd['Power'][::-1].cumsum()[::-1]
    diff = np.abs(prefix_sum - suffix_sum)

    min_ind = np.argmin(diff)
    med_freq = psd.loc[diff.index.values[min_ind]]['Frequency']
    
    return med_freq
    
#
# =============================================================================
#

def calc_mnf(psd):
    """
    Calculate the Mean Frequency (MNF) of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.
    
    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    mean_freq : int, float
        The MNF of the psd provided.
    
    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    mean_freq = np.sum(psd['Frequency'] * psd['Power']) / np.sum(psd['Power'])
    return mean_freq

#
# =============================================================================
#

def calc_twitch_ratio(psd, freq=60):
    """
    Calculate the Twitch Ratio of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.
    freq : float, optional
        Frequency threshold of the Twitch Ratio separating fast-twitching
        (high-frequency) muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if freq is less or equal to 0.
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    twitch_ratio : float
        Twitch Ratio of the PSD.

    """
    
    if freq <= 0:
        raise Exception("freq cannot be less or equal to 0")
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    fast_twitch = psd[psd['Frequency'] > freq]
    slow_twitch = psd[psd['Frequency'] < freq]
    
    twitch_ratio = np.sum(fast_twitch['Power']) / np.sum(slow_twitch['Power'])
    
    return twitch_ratio

#
# =============================================================================
#

def calc_twitch_index(psd, freq=60):
    """
    Calculate the Twitch Index of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.
    freq : float, optional
        Frequency threshold of the Twitch Index separating fast-twitching
        (high-frequency) muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if freq is less or equal to 0.
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    twitch_index : float
        Twitch Index of the PSD.

    """
    
    if freq <= 0:
        raise Exception("freq cannot be less or equal to 0")
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    fast_twitch = psd[psd['Frequency'] > freq]
    slow_twitch = psd[psd['Frequency'] < freq]
    
    twitch_index = np.max(fast_twitch['Power']) / np.max(slow_twitch['Power'])
    
    return twitch_index

#
# =============================================================================
#

def calc_twitch_slope(psd, freq=60):
    """
    Calculate the Twitch Slope of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.
    freq : float, optional
        Frequency threshold of the Twitch Slope separating fast-twitching
        (high-frequency) muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if freq is less or equal to 0.
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    fast_slope : float
        Twitch Slope of the fast-twitching muscles.
    slow_slope : float
        Twitch Slope of the slow-twitching muscles.

    """
    
    if freq <= 0:
        raise Exception("freq cannot be less or equal to 0")
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    fast_twitch = psd[psd['Frequency'] > freq]
    slow_twitch = psd[psd['Frequency'] < freq]
    
    x_fast = fast_twitch['Frequency']
    y_fast = fast_twitch['Power']
    A_fast = np.vstack([x_fast, np.ones(len(x_fast))]).T
    
    x_slow = slow_twitch['Frequency']
    y_slow = slow_twitch['Power']
    A_slow = np.vstack([x_slow, np.ones(len(x_slow))]).T
    
    fast_alpha = np.linalg.lstsq(A_fast, y_fast, rcond=None)[0]
    slow_alpha = np.linalg.lstsq(A_slow, y_slow, rcond=None)[0]
    
    fast_slope = fast_alpha[0]
    slow_slope = slow_alpha[0]
    
    return fast_slope, slow_slope

#
# =============================================================================
#

def calc_sc(psd):
    """
    Calculate the Spectral Centroid (SC) of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    SC : float
        SC of the PSD.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    SC = np.sum(psd['Power']*psd['Frequency']) / np.sum(psd['Power'])
    return SC

#
# =============================================================================
#

def calc_sf(psd):
    """
    Calculate the Spectral Flatness (SF) of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    SF : float
        SF of the PSD.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    N = psd.shape[0]
    SF = np.prod(psd['Power'] ** (1/N)) / ((1/N) * np.sum(psd['Power']))
    return SF

#
# =============================================================================
#

def calc_ss(psd):
    """
    Calculate the Spectral Spread (SS) of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    SS : float
        SS of the PSD.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    SC = calc_sc(psd)
    SS = np.sum(((psd['Frequency'] - SC) ** 2) * psd['Power']) / np.sum(psd['Power'])
    return SS

#
# =============================================================================
#

def calc_sd(psd):
    """
    Calculate the Spectral Decrease (SDec) of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    SDec : float
        SDec of the PSD.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    N = psd.shape[0]
    vals = np.array(psd['Power'])
    SDec = np.sum((vals[1:] - vals[0])/N) / np.sum(vals[1:])
    return SDec

#
# =============================================================================
#

def calc_se(psd):
    """
    Calculate the Spectral Entropy of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'

    Returns
    -------
    SEntropy : float
        Spectral Entropy of the PSD.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    prob = psd['Power'] / np.sum(psd['Power'])
    SEntropy = -np.sum(prob * np.log(prob))
    return SEntropy

#
# =============================================================================
#

def calc_sr(psd, percent=0.85):
    """
    Calculate the Spectral Rolloff of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.
    percent : float, optional
        The percentage of power to look for the Spectral Rolloff after. The
        default is 0.85.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'
    Exception
        An exception is raised if percent is not between 0 and 1

    Returns
    -------
    float
        Spectral Rolloff of the PSD.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    if percent <= 0 or percent >= 1:
        raise Exception("percent must be between 0 and 1")
    
    total_prob = 0
    total_power = np.sum(psd['Power'])
    # Make copy and reset rows to iterate over them
    psdCalc = psd.copy()
    psdCalc = psdCalc.reset_index()
    for i in range(len(psdCalc)):
        prob = psdCalc.loc[i, 'Power'] / total_power
        total_prob += prob
        if total_power >= percent:
            return psdCalc.loc[i, 'Frequency']

#
# =============================================================================
#

def calc_sbw(psd, p=2):
    """
    Calculate the Spectral Bandwidth (SBW) of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.
    p : int, optional
        Order of the SBW. The default is 2, which gives the standard deviation
        around the centroid.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency'
        and 'Power'
    Exception
        An exception is raised if p is not greater than 0

    Returns
    -------
    SBW : float
        The SBW of the PSD.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    if p <= 0:
        raise Exception("p must be greater than 0")
    
    cent = calc_sc(psd)
    SBW = (np.sum(psd['Power'] * (psd['Frequency'] - cent) ** p)) ** (1/p)
    return SBW

#
# =============================================================================
#

def extract_features(pathNames, samplingRate, cols=None, expression=None, fileExt='csv', shortName=True):
    """
    Analyze Signals by performing a collection of analyses on them and saving a
    feature file.

    Parameters
    ----------
    pathNames : [str] dict
        A dictionary of path names for reading data. Required paths are: Notch,
        Bandpass and Feature. The dictionary can be created with the
        make_paths function.
    samplingRate : float
        Sampling rate for all Signals read (all files in in_bandpass and
        in_smooth).
    cols : [str] list, optional
        List of columns to analyze in each Signal (all files in in_bandpass and
        in_smooth). The default is None, in which case all columns except for
        "Time" will be analyzed. All Signals should have the columns listed, or
        if None is used, all Signals should have the same columns.
    expression : str, optional
        A regular expression. If provided, will only count files whose names
        match the regular expression. The default is None.
    fileExt : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    shortName : bool, optional
        If true, makes the key column of the feature files the name of the
        file. If false, uses the file path to ensure unique keys. The default
        is True.

    Raises
    ------
    Exception
        An exception is raised if 'Bandpass', 'Smooth' or 'Feature' are not
        keys of the pathNames dictionary provided
    Exception
        An exception is raised if Bandpass and Smooth (keys) do not contain the
        same files
    Exception
        An exception is raised if p is not greater than 0
    Exception
        Raises an exception if a file cannot not be read in Bandpass or
        Smooth.
    Exception
        Raises an exception if an unsupported file format was provided for
        fileExt.
    Exception
        Raises an exception if expression is not None or a valid regular
        expression.

    Returns
    -------
    None.

    """
    
    if 'Bandpass' not in pathNames:
        raise Exception('Bandpass path not detected in provided dictionary (pathNames)')
    if 'Smooth' not in pathNames:
        raise Exception('Smooth path not detected in provided dictionary (pathNames)')
    if 'Feature' not in pathNames:
        raise Exception('Feature path not detected in provided dictionary (pathNames)')
    
    in_bandpass = pathNames['Bandpass']
    in_smooth = pathNames['Smooth']
    out_path = pathNames['Feature']
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    
    # Directories don't have to have the same file structure, but
    # Must have files with the same name
    filedirs_b = map_files(in_bandpass, fileExt=fileExt, expression=expression)
    filedirs_s = map_files(in_smooth, fileExt=fileExt, expression=expression)
    if len(filedirs_b) == 0 or len(filedirs_s) == 0:
        warnings.warn("Warning: The regular expression " + expression + " did not match with any files.")
    
    # List of measure names
    measure_names = [
        # Time-series features
        'Min',
        'Max',
        'Mean',
        'SD',
        'Skew',
        'Kurtosis',
        'IEMG',
        'MAV',
        'MMAV1',
        'MMAV2',
        'SSI',
        'VAR',
        'VOrder',
        'RMS',
        'WL',
        'LOG',
        'MFL',
        'AP',
        'Spectral_Flux',
        
        # Spectral features
        'Max_Freq',
        'MDF',
        'MNF',
        'Twitch_Ratio',
        'Twitch_Index',
        'Twitch_Slope_Fast',
        'Twitch_Slope_Slow',
        'Spec_Centroid',
        'Spec_Flatness',
        'Spec_Spread',
        'Spec_Decrease',
        'Spec_Entropy',
        'Spec_Rolloff',
        'Spec_Bandwidth'
    ]
    
    # Read the first file to get column names
    if cols == None:
        path1 = next(iter(filedirs_s.values()))
        data1 = read_file_type(path1, fileExt)
        cols = list(data1.columns)
        if 'Time' in cols:
            cols.remove('Time')
    
    
    # Create row labels
    df_names = ['File_ID']
    for col in cols:
        for measure in measure_names:
            df_names.append(col + '_' + measure)
    
    SignalDF = pd.DataFrame(columns=df_names)
    
    # Apply transformations
    for file in tqdm(filedirs_b):
        if (file[-len(fileExt):] == fileExt) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data_b = read_file_type(filedirs_b[file], fileExt)
            data_s = read_file_type(filedirs_s[file], fileExt)
            
            if col not in list(data_b.columns.values):
                raise Exception("Bandpass file " + file + " does not contain column " + col)
            if col not in list(data_s.columns.values):
                raise Exception("Smooth file " + file + " does not contain column " + col)
            
            # Calculate ID
            if shortName:
                File_ID = file
            else:
                File_ID = filedirs_s[file]
             
            df_vals = [File_ID]
            # Evaluate the measures of each column
            for col in cols:
                
                # Calculate time-series measures
                Min = np.min(data_s[col])
                Max = np.max(data_s[col])
                Mean = np.mean(data_s[col])
                SD = np.std(data_s[col])
                Skew = scipy.stats.skew(data_s[col])
                Kurtosis = scipy.stats.kurtosis(data_s[col])
                IEMG = calc_iemg(data_s, col, samplingRate)
                MAV = calc_mav(data_s, col)
                MMAV1 = calc_mmav1(data_s, col)
                MMAV2 = calc_mmav2(data_s, col)
                SSI = calc_ssi(data_s, col, samplingRate)
                VAR = calc_var(data_s, col)
                VOrder = calc_vorder(data_s, col)
                RMS = calc_rms(data_s, col)
                WL = calc_wl(data_s, col)
                LOG = calc_log(data_s, col)
                MFL = calc_mfl(data_s, col)
                AP = calc_ap(data_s, col)
    
                # Calculate spectral features
                Spectral_Flux = calc_spec_flux(data_s, 0.5, col, samplingRate)
                psd = emg_to_psd(data_b[col], samplingRate=samplingRate)
                Max_Freq = psd.iloc[psd['Power'].idxmax()]['Frequency']
                MDF = calc_mdf(psd)
                MNF = calc_mnf(psd)
                Twitch_Ratio = calc_twitch_ratio(psd)
                Twitch_Index = calc_twitch_index(psd)
                Fast_Twitch_Slope, Slow_Twitch_Slope = calc_twitch_slope(psd)
                Spectral_Centroid = calc_sc(psd)
                Spectral_Flatness = calc_sf(psd)
                Spectral_Spread = calc_ss(psd)
                Spectral_Decrease = calc_sd(psd)
                Spectral_Entropy = calc_se(psd)
                Spectral_Rolloff = calc_sr(psd)
                Spectral_Bandwidth = calc_sbw(psd, 2)
                
                # Append to list of values
                col_vals = [
                    Min,
                    Max,
                    Mean,
                    SD,
                    Skew,
                    Kurtosis,
                    
                    IEMG,
                    MAV,
                    MMAV1,
                    MMAV2,
                    SSI,
                    VAR,
                    VOrder,
                    RMS,
                    WL,
                    LOG,
                    MFL,
                    AP,
                    Spectral_Flux,
                    
                    Max_Freq,
                    MDF,
                    MNF,
                    Twitch_Ratio,
                    Twitch_Index,
                    Fast_Twitch_Slope,
                    Slow_Twitch_Slope,
                    Spectral_Centroid,
                    Spectral_Flatness,
                    Spectral_Spread,
                    Spectral_Decrease,
                    Spectral_Entropy,
                    Spectral_Rolloff,
                    Spectral_Bandwidth
                ]
                
                df_vals = df_vals + col_vals
            
            # Add values to the dataframe
            SignalDF.loc[len(SignalDF.index)] = df_vals
            
    SignalDF.to_csv(os.path.join(out_path, 'Features.csv'), index=False)
    return SignalDF
