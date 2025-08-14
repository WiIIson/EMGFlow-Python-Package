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


def calc_iemg(Signal:pd.DataFrame, col:str, sampling_rate:float):
    """
    Calculate the Integreated EMG (IEMG) of a column of 'Signal'. Ignores NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.
    sampling_rate : float
        Sampling rate of the Signal.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.

    Returns
    -------
    IEMG : float
        The calculated IEMG.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    if sampling_rate <= 0:
        raise Exception("Sampling rate cannot be less or equal to 0.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    IEMG = np.nansum(np.abs(col_vals) * sampling_rate)
    return IEMG

#
# =============================================================================
#

def calc_mav(Signal:pd.DataFrame, col:str):
    """
    Calculate the Mean Absolute Value (MAV) of a column of 'Signal'. Ignores
    NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    MAV : float
        The calculated MAV.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    MAV = np.sum(np.abs(col_vals)) / N
    return MAV

#
# =============================================================================
#

def calc_mmav1(Signal:pd.DataFrame, col:str):
    """
    Calculate the Modified Mean Absolute Value 1 (MMAV1) of a column of
    'Signal'. Ignores NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    MMAV1 : float
        The calculated MMAV1.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    vals = list(np.abs(col_vals))
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

def calc_mmav2(Signal:pd.DataFrame, col:str):
    """
    Calculate the Modified Mean Absolute Value 2 (MMAV2) of a column of
    'Signal'. Ignores NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    MMAV2 : float
        The calculated MMAV2'.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    vals = list(np.abs(col_vals))
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

def calc_ssi(Signal:pd.DataFrame, col:str, sampling_rate:float):
    """
    Calculate the Simple Square Integral (SSI) of a column of 'Signal'.
    Ignores NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.
    sampling_rate : float
        Sampling rate of the Signal.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if sampling_rate is less or equal to 0.

    Returns
    -------
    SSI : float
        The calculated SSI.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    if sampling_rate <= 0:
        raise Exception("Sampling rate cannot be 0 or negative")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    SSI = np.sum((np.abs(col_vals) * sampling_rate) ** 2)
    return SSI

#
# =============================================================================
#

def calc_var(Signal:pd.DataFrame, col:str):
    """
    Calculate the Variance (VAR) of a column of 'Signal'. Ignores NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    VAR : float
        The calculated VAR.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    VAR = 1/(N - 1) * np.sum((col_vals - np.mean(col_vals)) ** 2)
    return VAR

#
# =============================================================================
#

def calc_vorder(Signal:pd.DataFrame, col:str):
    """
    Calculate the V-Order of a column of 'Signal'. Ignores NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    vOrder : float
        The calculated V-Order.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    vOrder = np.sqrt(calc_var(Signal, col))
    return vOrder

#
# =============================================================================
#

def calc_rms(Signal:pd.DataFrame, col:str):
    """
    Calculate the Root Mean Square (RMS) of a column of 'Signal'. Ignores NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    RMS : float
        The calculated RMS.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    RMS = np.sqrt((1/N) * np.sum(col_vals ** 2))
    return RMS

#
# =============================================================================
#

def calc_wl(Signal:pd.DataFrame, col:str):
    """
    Calculate the Waveform Length (WL) of a column of 'Signal'. Ignores NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    WL : float
        The calculated WL.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    diff = np.array([np.abs(col_vals[i + 1] - col_vals[i]) for i in range(N - 1)])
    WL = np.sum(diff)
    return WL

#
# =============================================================================
#

def calc_wamp(Signal:pd.DataFrame, col:str, threshold:float):
    """
    Calculate the Willison Amplitude (WAMP) of a column of 'Signal'. Ignores
    NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.
    threshold : float
        Threshold of the WAMP.
        
    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    WAMP : int
        The calculated WAMP.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    diff = np.array([np.abs(col_vals[i + 1] - col_vals[i]) for i in range(N - 1)])
    WAMP = np.sum(diff > threshold)
    return WAMP

#
# =============================================================================
#

def calc_log(Signal:pd.DataFrame, col:str):
    """
    Calculate the Log Detector (LOG) of a column of 'Signal'. Ignores NaNs.
    
    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    LOG : float
        The calculated LOG.
    
    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    ex = (1/N) * np.sum(np.log(col_vals))
    LOG = np.e ** ex
    return LOG

#
# =============================================================================
#

def calc_mfl(Signal:pd.DataFrame, col:str):
    """
    Calculate the Maximum Fractal Length (MFL) of a column of 'Signal'. Ignores
    NaNs.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    MFL : float
        The calculated MFL.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    N = len(col_vals)
    diff = np.array([np.abs(col_vals[i + 1] - col_vals[i]) for i in range(N - 1)])
    MFL = np.log(np.sqrt(np.sum(diff ** 2)))
    return MFL

#
# =============================================================================
#

def calc_ap(Signal:pd.DataFrame, col:str):
    """
    Calculate the Average Power (AP) of a column of 'Signal'. Ignores NaNs

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the feature is calculated from.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    AP : float
        The calculated AP.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in the Signal.")
    
    # Get valid values
    col_vals = Signal[col].dropna().values
    
    AP = np.sum(col_vals ** 2) / len(col_vals)
    return AP

#
# =============================================================================
#

def calc_mdf(psd:pd.DataFrame):
    """
    Calculate the Median Frequency (MDF) of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.
    
    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    med_freq : int, float
        The MDF of 'psd'.
    
    """
    
    if not {'Frequency', 'Power'}.issubset(psd.columns):
        raise Exception("psd must contain columns 'Frequency' and 'Power'.")
    
    if psd['Power'].isna().any() or psd['Frequency'].isna().any():
        raise Exception("psd contains NaN values.")
    
    freq = psd['Frequency'].to_numpy(dtype=float)
    power = psd['Power'].to_numpy(dtype=float)
    
    ind = np.searchsorted(np.cumsum(power), np.sum(power) / 2.0)
    
    if ind == 0:
        return freq[0]
    elif ind >= len(freq):
        return freq[-1]
    else:
        return freq[ind]
    
#
# =============================================================================
#

def calc_mnf(psd:pd.DataFrame):
    """
    Calculate the Mean Frequency (MNF) of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.
    
    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    mean_freq : int, float
        The MNF of 'psd'.
    
    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    mean_freq = np.sum(psd['Frequency'] * psd['Power']) / np.sum(psd['Power'])
    return mean_freq

#
# =============================================================================
#

def calc_twitch_ratio(psd:pd.DataFrame, freq:float=60.0):
    """
    Calculate the Twitch Ratio of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.
    freq : float, optional
        Frequency threshold of the Twitch Ratio separating fast-twitching
        (high-frequency) muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if 'freq' is less or equal to 0.
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    twitch_ratio : float
        Twitch Ratio of 'psd'.

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

def calc_twitch_index(psd:pd.DataFrame, freq:float=60.0):
    """
    Calculate the Twitch Index of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.
    freq : float, optional
        Frequency threshold of the Twitch Index separating fast-twitching
        (high-frequency) muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if 'freq' is less or equal to 0.
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    twitch_index : float
        Twitch Index of 'psd'.

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

def calc_twitch_slope(psd:pd.DataFrame, freq:float=60.0):
    """
    Calculate the Twitch Slope of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.
    freq : float, optional
        Frequency threshold of the Twitch Slope separating fast-twitching
        (high-frequency) muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if 'freq' is less or equal to 0.
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    fast_slope : float
        Twitch Slope of the fast-twitching muscles of 'psd'.
    slow_slope : float
        Twitch Slope of the slow-twitching muscles of 'psd'.

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

def calc_sc(psd:pd.DataFrame):
    """
    Calculate the Spectral Centroid (SC) of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    SC : float
        SC of 'psd'.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    SC = np.sum(psd['Power']*psd['Frequency']) / np.sum(psd['Power'])
    return SC

#
# =============================================================================
#

def calc_sflt(psd:pd.DataFrame):
    """
    Calculate the Spectral Flatness (SFlt) of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    SF : float
        SF of 'psd'.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    N = psd.shape[0]
    SF = np.prod(psd['Power'] ** (1/N)) / ((1/N) * np.sum(psd['Power']))
    return SF

#
# =============================================================================
#

def calc_sflx(Signal1:pd.DataFrame, diff, col:str, sampling_rate:float, diff_sr:float=None):
    """
    Calculate the Spectral Flux (SFlx) of 'Signal1'. Ignores NaNs.

    Parameters
    ----------
    Signal1 : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    diff : float, pd.DataFrame
        The divisor of the calculation. If a percentage is provided, it will
        calculate the spectral flux of 'Signal1', divided into two different
        parts (diff and 1-diff). If 'diff' is instead a Pandas dataframe, it
        will claculate the spectral flux of 'Signal1' and 'diff'.
    col : str
        Column of 'Signal1' the feature is calculated from. If a second signal
        is provided for 'diff', a column of the same name should be available
        for use.
    sampling_rate : float
        Sampling rate of 'Signal1'.
    diff_sr : float, optional
        Sampling rate for 'diff' if it is a dataframe. The default is None,
        in which case if 'diff' is a dataframe, it is assumed to have the same
        sampling rate as 'Signal1'.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal1'.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.
    Exception
        An exception is raised if 'diff' is a float, but isn't between 0 and 1.
    Exception
        An exception is raised if 'diff' is a dataframe and does not contain
        'col'.
    Exception
        An exception is raised if 'diff_sr' is less or equal to 0.
    Exception
        An exception is raised if 'diff' is an invalid data type.

    Returns
    -------
    flux : float
        Spectral flux of 'Signal1' and 'diff'.

    """
    
    if col not in list(Signal1.columns.values):
        raise Exception("Column " + str(col) + " not in Signal1")
        
    if sampling_rate <= 0:
        raise Exception("Sampling rate cannot be 0 or negative")
    
    # Separate Signal1 by div and find spectral flux
    if isinstance(diff, float):
        if diff >= 1 or diff <= 0:
            raise Exception("diff must be a float between 0 and 1")
        
        # Find column divider index
        diff_ind = int(len(Signal1[col]) * diff)
        # Take the PSD of each signal
        psd1 = emg_to_psd(Signal1.iloc[:diff_ind].reset_index(), col, sampling_rate=sampling_rate)
        psd2 = emg_to_psd(Signal1.iloc[diff_ind:].reset_index(), col, sampling_rate=sampling_rate)
        # Calculate the spectral flux
        flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
        
    # Find spectral flux of Signal1 by div
    elif isinstance(diff, pd.DataFrame):
        if col not in list(diff.columns.values):
            raise Exception("Column " + str(col) + " not in diff")
        
        # If no second sampling rate, assume same sampling rate as first Signal
        if diff_sr == None:
            diff_sr = sampling_rate
        elif diff_sr <= 0:
            raise Exception("Sampling rate cannot be 0 or negative")
        
        # Take the PSD of each signal
        psd1 = emg_to_psd(Signal1, col, sampling_rate=sampling_rate)
        psd2 = emg_to_psd(diff, col, sampling_rate=diff_sr)
        # Calculate the spectral flux
        flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
    
    else:
        raise Exception("Invalid data type given for diff: " + str(type(diff)))
    
    return flux

#
# =============================================================================
#

def calc_ss(psd:pd.DataFrame):
    """
    Calculate the Spectral Spread (SS) of a 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    SS : float
        The SS of 'psd'.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    SC = calc_sc(psd)
    SS = np.sum(((psd['Frequency'] - SC) ** 2) * psd['Power']) / np.sum(psd['Power'])
    return SS

#
# =============================================================================
#

def calc_sd(psd:pd.DataFrame):
    """
    Calculate the Spectral Decrease (SDec) of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    SD : float
        The SDec of 'psd'.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    N = psd.shape[0]
    vals = np.array(psd['Power'])
    SD = np.sum((vals[1:] - vals[0])/N) / np.sum(vals[1:])
    return SD

#
# =============================================================================
#

def calc_se(psd:pd.DataFrame):
    """
    Calculate the Spectral Entropy (SE) of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.

    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.

    Returns
    -------
    SE : float
        The SE of 'psd'.

    """
    
    if set(psd.columns.values) != {'Frequency', 'Power'}:
        raise Exception("psd must be a Power Spectrum Density dataframe with only a 'Frequency' and 'Power' column")
    
    prob = psd['Power'] / np.sum(psd['Power'])
    SE = -np.sum(prob * np.log(prob))
    return SE

#
# =============================================================================
#

def calc_sr(psd:pd.DataFrame, percent:float=0.85):
    """
    Calculate the Spectral Rolloff (SR) of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.
    percent : float, optional
        The percentage of power to look for the Spectral Rolloff after. The
        default is 0.85.

    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.
    Exception
        An exception is raised if 'percent' is not between 0 and 1.

    Returns
    -------
    SRoll : float
        The SRoll of 'psd'.

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
            SRoll = psdCalc.loc[i, 'Frequency']
            return SRoll

#
# =============================================================================
#

def calc_sbw(psd:pd.DataFrame, p:int=2):
    """
    Calculate the Spectral Bandwidth (SBW) of 'psd'. Ignores NaNs.

    Parameters
    ----------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column.
    p : int, optional
        Order of the SBW. The default is 2, which gives the standard deviation
        around the centroid.

    Raises
    ------
    Exception
        An exception is raised if 'psd' does not only have columns 'Frequency'
        and 'Power'.
    Exception
        An exception is raised if p is not greater than 0.

    Returns
    -------
    SBW : float
        The SBW of 'psd'.

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

def extract_features(path_names:dict, sampling_rate:float, cols=None, expression:str=None, file_ext:str='csv', short_name:bool=True):
    """
    Extracts features from signals by running a series of feature extraction
    functions and saving the output to a feature file.
    
    The input and output locations are controlled by the 'path_names'
    dictionary. The input data is taken from the 'Filled' and 'Bandpass' paths.
    The 'Filled' path is an optional step, so 'Smooth' is used if 'Filled' is
    unused. All files within these folders and subfolders are assumed to be
    signal files if they match the file extension, and the optional regular
    expression. Files of the same name should exist in both the
    'Filled'/'Smooth' and 'Bandpass' folders, being the same file at different
    stages in processing pipeline.

    The 'Filled' or 'Smooth' path is used to calculate time-series features,
    while the 'Bandpass' path is used to calculate spectral features.

    Columns of these files that begin with 'mask_' are assumed to be NaN mask
    columns, and are ignored unless specified in cols.

    The output is written as a 'Features.csv' file to the 'Feature' path.

    Parameters
    ----------
    path_names : dict-str
        A dictionary of path names for reading data. Required paths are:
        'Bandpass', 'Smooth' and 'Feature'. The dictionary can be created with
        the 'make_paths' function.
    sampling_rate : float
        Sampling rate for all Signals being read.
    cols : list-str, optional
        List of columns to analyze in each Signal. The default is None, in
        which case all columns except for 'Time' will be analyzed. All files
        should have at least these columns in common. If None is used, all
        files will be assumed to have the same colums as the first file read.
    expression : str, optional
        A regular expression. If provided, will only analyze files whose local
        paths inside of 'path_names' match the regular expression. The default
        is None.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    short_name : bool, optional
        If true, makes the key column of the feature files the relative path of
        the file. If false, uses the full system path. The default is True.

    Raises
    ------
    Warning
        A warning is raised if 'expression' does not match with any files in
        the folders provided.
    Exception
        An exception is raised if 'Bandpass', 'Smooth' or 'Feature' are not
        keys of the path_names dictionary provided.
    Exception
        An exception is raised if the 'Bandpass' and 'Smooth' filepaths do not
        contain the same files.
    Exception
        An exception is raised if a file cannot not be read in the 'Bandpass'
        or 'Smooth'/'Filled' filepaths.
    Exception
        An exception is raised if a file does not contain one of the columns
        from 'cols'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.

    Returns
    -------
    Features : pd.DataFrame
        A Pandas dataframe of feature data for each file read. Each row is a
        different file analyzed, marked by the 'File_ID' column. Additional
        columns show the values of the features extracted by the function.

    """
    
    if 'Bandpass' not in path_names:
        raise Exception('Bandpass path not detected in provided dictionary (path_names)')
    if 'FWR' not in path_names:
        raise Exception('FWR path not detected in provided dictionary (path_names)')
    if 'Feature' not in path_names:
        raise Exception('Feature path not detected in provided dictionary (path_names)')
    
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
    file_dirs_b = map_files(path_names['Bandpass'], file_ext=file_ext, expression=expression)
    
    try:
        file_dirs_s = map_files(path_names['Filled'], file_ext=file_ext, expression=expression)
        if (len(file_dirs_s)) != (len(file_dirs_b)):
            raise Exception('Filled files not detected...')
    except:
        try:
            file_dirs_s = map_files(path_names['Smooth'], file_ext=file_ext, expression=expression)
            if (len(file_dirs_s)) != (len(file_dirs_b)):
                raise Exception('Filled files not detected...')
        except:
            file_dirs_s = map_files(path_names['FWR'], file_ext=file_ext, expression=expression)
            if (len(file_dirs_s)) != (len(file_dirs_b)):
                raise Exception('Data not detected in "Filled", "Smooth" and "FWR" paths. Feature extraction could not be completed.')
            
    
    if len(file_dirs_b) == 0 or len(file_dirs_s) == 0:
        warnings.warn("Warning: The regular expression " + str(expression) + " did not match with any files.")
    
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
        'Timeseries_Pmissing',
        
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
        'Spec_Flux',
        'Spec_Spread',
        'Spec_Decrease',
        'Spec_Entropy',
        'Spec_Rolloff',
        'Spec_Bandwidth',
        'Spec_Pmissing'
    ]
    
    # Read the first file to get column names
    if cols == None:
        path1 = next(iter(file_dirs_s.values()))
        data1 = read_file_type(path1, file_ext)
        cols = list(data1.columns)
        cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
    
    
    # Create row labels
    df_names = ['File_ID']
    for col in cols:
        for measure in measure_names:
            df_names.append(col + '_' + measure)
    
    Features = pd.DataFrame(columns=df_names)
    
    # Apply transformations
    for file in tqdm(file_dirs_b):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            try:
                data_b = read_file_type(file_dirs_b[file], file_ext)
                data_s = read_file_type(file_dirs_s[file], file_ext)
            except:
                raise Exception("Could not find file: " + str(file))
            
            if col not in list(data_b.columns.values):
                raise Exception("Bandpass file " + str(file) + " does not contain column " + str(col))
            if col not in list(data_s.columns.values):
                raise Exception("Smooth file " + str(file) + " does not contain column " + str(col))
            
            # Calculate ID
            if short_name:
                File_ID = file
            else:
                File_ID = file_dirs_s[file]
             
            df_vals = [File_ID]
           
            # Evaluate the measures of each column
            for col in cols:
                
                # Use the mask if it is there (smooth mask for both dataframes)
                mask_col = 'mask_' + str(col)
                if mask_col in data_s.columns.values:
                    data_b.loc[~data_s[mask_col], col] = np.nan
                    Timeseries_Pmissing = (~data_s[mask_col]).mean()
                    Spectral_Pmissing = data_b[col].isna().mean()
                else:
                    Timeseries_Pmissing = data_s[col].isna().mean()
                    Spectral_Pmissing = data_b[col].isna().mean()
                
                # Calculate time-series measures
                Min = np.min(data_s[col])
                Max = np.max(data_s[col])
                Mean = np.mean(data_s[col])
                SD = np.std(data_s[col])
                Skew = scipy.stats.skew(data_s[col].dropna())
                Kurtosis = scipy.stats.kurtosis(data_s[col].dropna())
                IEMG = calc_iemg(data_s, col, sampling_rate)
                MAV = calc_mav(data_s, col)
                MMAV1 = calc_mmav1(data_s, col)
                MMAV2 = calc_mmav2(data_s, col)
                SSI = calc_ssi(data_s, col, sampling_rate)
                VAR = calc_var(data_s, col)
                VOrder = calc_vorder(data_s, col)
                RMS = calc_rms(data_s, col)
                WL = calc_wl(data_s, col)
                LOG = calc_log(data_s, col)
                MFL = calc_mfl(data_s, col)
                AP = calc_ap(data_s, col)
    
                # Calculate spectral features
                psd = emg_to_psd(data_b, col, sampling_rate=sampling_rate)
                Max_Freq = psd.iloc[psd['Power'].idxmax()]['Frequency']
                MDF = calc_mdf(psd)
                MNF = calc_mnf(psd)
                Twitch_Ratio = calc_twitch_ratio(psd)
                Twitch_Index = calc_twitch_index(psd)
                Fast_Twitch_Slope, Slow_Twitch_Slope = calc_twitch_slope(psd)
                Spectral_Centroid = calc_sc(psd)
                Spectral_Flatness = calc_sflt(psd)
                Spectral_Flux = calc_sflx(data_b, 0.5, col, sampling_rate)
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
                    Timeseries_Pmissing,
                    
                    Max_Freq,
                    MDF,
                    MNF,
                    Twitch_Ratio,
                    Twitch_Index,
                    Fast_Twitch_Slope,
                    Slow_Twitch_Slope,
                    Spectral_Centroid,
                    Spectral_Flatness,
                    Spectral_Flux,
                    Spectral_Spread,
                    Spectral_Decrease,
                    Spectral_Entropy,
                    Spectral_Rolloff,
                    Spectral_Bandwidth,
                    Spectral_Pmissing
                ]
                
                df_vals = df_vals + col_vals
            
            # Add values to the dataframe
            Features.loc[len(Features.index)] = df_vals
            
    Features.to_csv(os.path.join(out_path, 'Features.csv'), index=False)
    return Features
