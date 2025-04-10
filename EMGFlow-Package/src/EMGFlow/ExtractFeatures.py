import scipy
import pandas as pd
import numpy as np
import os
import re
from tqdm import tqdm
import warnings

from .FileAccess import *
from .PreprocessSignals import EMG2PSD

#
# =============================================================================
#

"""
A collection of functions for extracting features.
"""

#
# =============================================================================
#


def CalcIEMG(Signal, col, sr):
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
def CalcMAV(Signal, col):
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

def CalcMMAV(Signal, col):
    """
    Calculate the Modified Mean Absolute Value (MMAV) of a Signal.

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
    MMAV : float
        MMAV of the Signal.

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
    MMAV = total/N
    return MMAV

#
# =============================================================================
#

def CalcSSI(Signal, col, sr):
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

def CalcVAR(Signal, col):
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

def CalcVOrder(Signal, col):
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
    
    vOrder = np.sqrt(CalcVAR(Signal, col))
    return vOrder

#
# =============================================================================
#

def CalcRMS(Signal, col):
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

def CalcWL(Signal, col):
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

def CalcWAMP(Signal, col, threshold):
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

def CalcLOG(Signal, col):
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

def CalcMFL(Signal, col):
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

def CalcAP(Signal, col):
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

def CalcSpecFlux(Signal1, diff, col, sr, diff_sr=None):
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
    diff_sr : float, optional
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
        An exception is raised if diff_sr is less or equal to 0.

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
        psd1 = EMG2PSD(Signal1[col][:diff_ind], sampling_rate=sr)
        psd2 = EMG2PSD(Signal1[col][diff_ind:], sampling_rate=sr)
        # Calculate the spectral flux
        flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
        
    # Find spectral flux of Signal1 by div
    elif isinstance(diff, pd.DataFrame):
        if col not in list(diff.columns.values):
            raise Exception("Column " + col + " not in diff")
        
        # If no second sampling rate, assume same sampling rate as first Signal
        if diff_sr == None: diff_sr = sr
        
        if diff_sr <= 0:
            raise Exception("Sampling rate cannot be 0 or negative")
        # Take the PSD of each signal
        psd1 = EMG2PSD(Signal1[col], sampling_rate=sr)
        psd2 = EMG2PSD(diff[col], sampling_rate=diff_sr)
        # Calculate the spectral flux
        flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
    
    return flux

#
# =============================================================================
#

def CalcMDF(psd):
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

def CalcMNF(psd):
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

def CalcTwitchRatio(psd, freq=60):
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

def CalcTwitchIndex(psd, freq=60):
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

def CalcTwitchSlope(psd, freq=60):
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

def CalcSC(psd):
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

def CalcSF(psd):
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

def CalcSS(psd):
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
    
    SC = CalcSC(psd)
    SS = np.sum(((psd['Frequency'] - SC) ** 2) * psd['Power']) / np.sum(psd['Power'])
    return SS

#
# =============================================================================
#

def CalcSDec(psd):
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

def CalcSEntropy(psd):
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

def CalcSRoll(psd, percent=0.85):
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

def CalcSBW(psd, p=2):
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
    
    cent = CalcSC(psd)
    SBW = (np.sum(psd['Power'] * (psd['Frequency'] - cent) ** p)) ** (1/p)
    return SBW

#
# =============================================================================
#

def ExtractFeatures(path_names, sampling_rate, cols=None, expression=None, file_ext='csv', short_name=True):
    """
    Analyze Signals by performing a collection of analyses on them and saving a
    feature file.

    Parameters
    ----------
    path_names : [str] dict
        A dictionary of path names for reading data. Required paths are: Notch,
        Bandpass and Feature. The dictionary can be created with the
        make_path_dict function.
    sampling_rate : float
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
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    short_name : bool, optional
        If true, makes the key column of the feature files the name of the
        file. If false, uses the file path to ensure unique keys. The default
        is True.

    Raises
    ------
    Exception
        An exception is raised if in_bandpass and in_smooth do not contain the
        same files
    Exception
        An exception is raised if p is not greater than 0
    Exception
        Raises an exception if a file cannot not be read in in_bandpass or
        in_smooth.
    Exception
        Raises an exception if an unsupported file format was provided for
        file_ext.
    Exception
        Raises an exception if expression is not None or a valid regular
        expression.

    Returns
    -------
    None.

    """
    
    in_bandpass = path_names['Bandpass']
    in_smooth = path_names['Smooth']
    out_path = path_names['Feature']
    
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
    filedirs_b = MapFiles(in_bandpass, file_ext=file_ext, expression=expression)
    filedirs_s = MapFiles(in_smooth, file_ext=file_ext, expression=expression)
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
        'MMAV',
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
        data1 = ReadFileType(path1, file_ext)
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
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data_b = ReadFileType(filedirs_b[file], file_ext)
            data_s = ReadFileType(filedirs_s[file], file_ext)
            
            if col not in list(data_b.columns.values):
                raise Exception("Bandpass file " + file + " does not contain column " + col)
            if col not in list(data_s.columns.values):
                raise Exception("Smooth file " + file + " does not contain column " + col)
            
            # Calculate ID
            if short_name:
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
                IEMG = CalcIEMG(data_s, col, sampling_rate)
                MAV = CalcMAV(data_s, col)
                MMAV = CalcMMAV(data_s, col)
                SSI = CalcSSI(data_s, col, sampling_rate)
                VAR = CalcVAR(data_s, col)
                VOrder = CalcVOrder(data_s, col)
                RMS = CalcRMS(data_s, col)
                WL = CalcWL(data_s, col)
                LOG = CalcLOG(data_s, col)
                MFL = CalcMFL(data_s, col)
                AP = CalcAP(data_s, col)
                Spectral_Flux = CalcSpecFlux(data_s, 0.5, col, sampling_rate)
    
                # Calculate spectral features
                psd = EMG2PSD(data_b[col], sampling_rate=sampling_rate)
                Max_Freq = psd.iloc[psd['Power'].idxmax()]['Frequency']
                MDF = CalcMDF(psd)
                MNF = CalcMNF(psd)
                Twitch_Ratio = CalcTwitchRatio(psd)
                Twitch_Index = CalcTwitchIndex(psd)
                Fast_Twitch_Slope, Slow_Twitch_Slope = CalcTwitchSlope(psd)
                Spectral_Centroid = CalcSC(psd)
                Spectral_Flatness = CalcSF(psd)
                Spectral_Spread = CalcSS(psd)
                Spectral_Decrease = CalcSDec(psd)
                Spectral_Entropy = CalcSEntropy(psd)
                Spectral_Rolloff = CalcSRoll(psd)
                Spectral_Bandwidth = CalcSBW(psd, 2)
                
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
                    MMAV,
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
