import scipy
import pandas as pd
import numpy as np
import os
import re
from tqdm import tqdm
import warnings

from .access_files import *

#
# =============================================================================
#

"""
A collection of functions for filtering Signals.
"""

#
# =============================================================================
#

def emg_to_psd(Signal, col, sampling_rate=1000, normalize=True, min_gap_ms=30.0, nan_mask=None):
    """
    Creates a PSD graph of a Signal. Uses the Welch method, meaning it can be
    used as a Long Term Average Spectrum (LTAS).

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.
    sampling_rate : float
        Sampling rate of 'sig_vals'. This is the number of entries recorded per
        second, or the inverse of the difference between entries.
    normalize : bool, optional
        If True, will normalize the result. If False, will not. The default is
        True.
    min_gap_ms : float, optional
        
    mask : pd.Series, optional

    Raises
    ------
    Exception
        An exception is raised if 'sig_vals' is a pd.DataFrame, not a column of
        a dataframe.
    Exception
        An exception is raised if 'sig_vals' contains NaN values.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.

    Returns
    -------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column. The
        'Power' column indicates the intensity of each frequency in the Signal
        provided. Results will be normalized if 'normalize' is set to True.
    
    """
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    if sampling_rate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0")
    
    PSD_Signal = Signal.copy()
    
    # Calculate gap parameter
    min_gap = int(min_gap_ms * sampling_rate / 1000.0)
    
    if nan_mask is None:
        
        # Construct list of NaN locations
        data = PSD_Signal[col]
        mask = data.isna()
        group = (mask != mask.shift()).cumsum()
        group_sequences = data[mask].groupby(group[mask])
        nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
        
        # Create NaN mask
        min_nan_mask = pd.Series([True] * len(data))
        for (nan_ind, nan_len) in nan_sequences:
            if nan_len < min_gap:
                min_nan_mask[nan_ind:nan_ind+nan_len] = False
        
        # Use mask to remove small NaN groups, construct list of value locations
        masked_data = PSD_Signal[min_nan_mask]
        masked_data = masked_data.copy()
    else:
        # Construct masked data from provided nan mask        
        if not isinstance(nan_mask, pd.Series):
            raise Exception('NaN mask must be a Pandas series.')
        
        if len(nan_mask) != len(PSD_Signal):
            raise Exception('NaN mask must be the same length as the Signal dataframe.')
        
        masked_data = PSD_Signal[nan_mask]
        masked_data = masked_data.copy()
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Make a PSD from every segment
    PSDs = []
    for i in range(len(val_sequences)):
        (val_ind, val_len) = val_sequences[i]
        temp_dat = masked_data.iloc[val_ind:val_ind+val_len].copy()
        
        N = len(temp_dat)
        min_frequency = (2 * sampling_rate) / (N / 2)
        nperseg = int((2 / min_frequency) * sampling_rate)
        nfft = nperseg * 2
        
        if val_len >= min_gap:
            # Apply welch method with hanning window
            frequency, power = scipy.signal.welch(
                temp_dat[col].values,
                fs=sampling_rate,
                scaling='density',
                detrend=False,
                nfft=nfft,
                average='mean',
                nperseg=nperseg,
                window='hann'
            )
            
            # Normalize if set to true
            if normalize is True:
                power /= np.max(power)
    
            # Create dataframe of results
            psd = pd.DataFrame({'Frequency': frequency, 'Power' + str(i): power})
            
            # Filter given valid range
            psd = psd.loc[np.logical_and(psd['Frequency'] >= min_frequency, psd['Frequency'] <= np.inf)]
            
            PSDs.append(psd)
            
    psd = PSDs[0]
    for i in range(1, len(PSDs)):
        psd = pd.merge(psd, PSDs[i], on='Frequency', how='outer')
        
    # Final cleaning for psd
    psd = psd.fillna(0)
    psd['Power'] = psd.drop(columns='Frequency').mean(axis=1)
    psd = psd[['Frequency', 'Power']]
    psd = psd.sort_values(by='Frequency')
    
    return psd

def emg_to_psd_old(sig_vals, sampling_rate=1000, normalize=True):
    """
    Creates a PSD graph of a Signal. Uses the Welch method, meaning it can be
    used as a Long Term Average Spectrum (LTAS).

    Parameters
    ----------
    sig_vals : list-float
        A list of float values. A column of a signal datframe.
    sampling_rate : float
        Sampling rate of 'sig_vals'. This is the number of entries recorded per
        second, or the inverse of the difference between entries.
    normalize : bool, optional
        If True, will normalize the result. If False, will not. The default is
        True.

    Raises
    ------
    Exception
        An exception is raised if 'sig_vals' is a pd.DataFrame, not a column of
        a dataframe.
    Exception
        An exception is raised if 'sig_vals' contains NaN values.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.

    Returns
    -------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column. The
        'Power' column indicates the intensity of each frequency in the Signal
        provided. Results will be normalized if 'normalize' is set to True.
    
    """
    
    if isinstance(sig_vals, pd.DataFrame):
        raise Exception("sig_vals must be a column of the dataframe, not the entire dataframe.")
    
    # An exception is raised if 'sig_vals' contains NaN values.
    if np.nan in sig_vals:
        raise Exception("NaN values found.")
    
    if sampling_rate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0")
    
    # Initial parameters
    sig_vals = sig_vals - np.mean(sig_vals)
    N = len(sig_vals)
    
    # Calculate minimum frequency given sampling rate
    min_frequency = (2 * sampling_rate) / (N / 2)
    
    # Calculate window size given sampling rate
    nperseg = int((2 / min_frequency) * sampling_rate)
    nfft = nperseg * 2
    
    # Apply welch method with hanning window
    frequency, power = scipy.signal.welch(
        sig_vals,
        fs=sampling_rate,
        scaling='density',
        detrend=False,
        nfft=nfft,
        average='mean',
        nperseg=nperseg,
        window='hann'
    )
    
    # Normalize if set to true
    if normalize is True:
        power /= np.max(power)
        
    # Create dataframe of results
    psd = pd.DataFrame({'Frequency': frequency, 'Power': power})
    # Filter given 
    psd = psd.loc[np.logical_and(psd['Frequency'] >= min_frequency,
                                   psd['Frequency'] <= np.inf)]
    
    return psd

#
# =============================================================================
#

def apply_notch_filters(Signal, col, sampling_rate, notch_vals, min_gap_ms=30.0):
    """
    Apply a list of notch filters for given frequencies and Q-factors to a
    column of the provided data.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.
    sampling_rate : float
        Sampling rate of 'Signal'.
    notch_vals : list-tuple
        A list of (Hz, Q) tuples corresponding to the notch filters being
        applied. Hz is the frequency to apply the filter to, and Q is the
        Q-score (an intensity score where a higher number means a less extreme
        filter).
    min_gap_ms : float
        Minimum length of time (in ms) for missing data. Segments of missing
        data less than this threshold are ignored in the filter calculation,
        and segments greater than this are used to divide the data, with the
        filter applied to each part.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.
    Exception
        An exception is raised if a Hz value in 'notch_vals' is greater than
        sampling_rate/2 or less than 0.

    Returns
    -------
    notch_Signal : pd.DataFrame
        A copy of the 'Signal' dataframe with the notch filters are applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal.")
    
    # A warning is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
    
    # An exception is raised if 'sampling_rate' is less or equal to 0.
    if sampling_rate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0.")
    
    notch_Signal = Signal.copy()
    
    # Calculate gap parameter
    min_gap = int(min_gap_ms * sampling_rate / 1000.0)
    
    # Construct list of NaN locations
    data = notch_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data))
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask[nan_ind:nan_ind+nan_len] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = notch_Signal[min_nan_mask]
    masked_data = masked_data.copy()
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Apply notch filters to each value sequence set sequences that are too
    # small to NaN
    nyq_freq = sampling_rate / 2
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len, col] = np.nan
        else:
            # Apply filters
            for (Hz, Q) in notch_vals:
                 norm_Hz = Hz / nyq_freq
                
                 # Use scipy notch filter using normalized frequency
                 b, a = scipy.signal.iirnotch(norm_Hz, Q)
                 filtered_section = scipy.signal.lfilter(b, a, masked_data.loc[val_ind:val_ind+val_len, col].copy())
                 masked_data.loc[val_ind:val_ind+val_len, col] = filtered_section
    
    # Put masked_data back in band_Signal
    notch_Signal.loc[min_nan_mask, col] = masked_data[col]
    
    return notch_Signal

#
# =============================================================================
#

def notch_filter_signals(in_path, out_path, sampling_rate, notch, cols=None, expression=None, exp_copy=False, file_ext='csv'):
    """
    Apply notch filters to all Signals in a folder. Writes filtered Signals to
    an output folder, and generates a file structure matching the input folder.

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    out_path : str
        Filepath to an output directory.
    sampling_rate : float
        Sampling rate of the signal files.
    notch : list-tuples
        A list of (Hz, Q) tuples corresponding to the notch filters being
        applied. Hz is the frequency to apply the filter to, and Q is the
        Q-score (an intensity score where a higher number means a less
        extreme filter).
    cols : list-str, optional
        List of columns of the signal to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'Time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names
        match the regular expression. The default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    
    Raises
    ------
    Warning
        Raises a warning if no files in 'in_path' match with 'expression'.
    Warning
        A warning is raised if any column in 'cols' in any of the Signal
        files read contain NaN values.
    Exception
        An exception is raised if any column in 'cols' is not found in any of
        the signal files read.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.
    Exception
        An exception is raised if a Hz value in 'notch_vals' is greater than
        sampling_rate/2 or less than 0.
    Exception
        An exception is raised if a file cannot not be read in 'in_path'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
    
    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("Warning: The regular expression " + str(expression) + " did not match with any files.")
        
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
            
            # Apply filter to columns
            for col in cols:
                data = apply_notch_filters(data, col, sampling_rate, notch)
            
            # Construct out path
            out_file = out_path + file_dirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
        elif (file[-len(file_ext):] == file_ext) and exp_copy:
            # Copy the file even if it doesn't match if exp_copy is true
            data = read_file_type(file_dirs[file], file_ext)
            out_file = out_path + file_dirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    
    return

#
# =============================================================================
#

def apply_bandpass_filter(Signal, col, sampling_rate, low, high, min_gap_ms=30.0):
    """
    Apply a bandpass filter to a Signal for a given lower and upper limit.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.
    sampling_rate : float
        Sampling rate of 'Signal'.
    low : float
        Lower frequency limit of the bandpass filter.
    high : float
        Upper frequency limit of the bandpass filter.
    min_gap_ms : float, optional
        Minimum length of time (in ms) for missing data. Segments of missing
        data less than this threshold are ignored in the filter calculation,
        and segments greater than this are used to divide the data, with the
        filter applied to each part. The default is 30.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.
    Exception
        An exception is raised if 'high' or 'low' are higher than 1/2 of
        'sampling_rate'.
    Exception
        An exception is raised if 'high' is not higher than 'low'.

    Returns
    -------
    band_Signal : pd.DataFrame
        A copy of 'Signal' after the bandpass filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal.")
    
    # A warning is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
    
    # An exception is raised if 'sampling_rate' is less or equal to 0.
    if sampling_rate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0.")
    
    # An exception is raised if 'high' or 'low' are higher than 1/2 of
    # 'sampling_rate'.
    if high > sampling_rate/2 or low > sampling_rate/2:
        raise Exception("'high' and 'low' cannot be greater than 1/2 the sampling rate.")
    
    # An exception is raised if 'high' is not higher than 'low'.
    if high <= low:
        raise Exception("'high' must be higher than 'low'.")
    
    band_Signal = Signal.copy()
    
    # Calculate gap parameter
    min_gap = int(min_gap_ms * sampling_rate / 1000.0)
    
    # Construct list of NaN locations
    data = band_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data))
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask[nan_ind:nan_ind+nan_len] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = band_Signal[min_nan_mask]
    masked_data = masked_data.copy()
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Apply notch filters to each value sequence set sequences that are too
    # small to NaN
    b, a = scipy.signal.butter(5, [low, high], fs=sampling_rate, btype='band')
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len, col] = np.nan
        else:
            # Apply filter
            filtered_section = scipy.signal.lfilter(b, a, masked_data.loc[val_ind:val_ind+val_len, col].copy())
            masked_data.loc[val_ind:val_ind+val_len, col] = filtered_section
    
    # Put masked_data back in band_Signal
    band_Signal.loc[min_nan_mask, col] = masked_data[col]
    
    return band_Signal

#
# =============================================================================
#

def bandpass_filter_signals(in_path, out_path, sampling_rate, low=20, high=450, cols=None, expression=None, exp_copy=False, file_ext='csv'):
    """
    Apply bandpass filters to all Signals in a folder. Writes filtered Signals
    to an output folder, and generates a file structure
    matching the input folder.
    
    Parameters
    ----------
    in_path : dict-str
        Filepath to a directory to read Signal files.
    out_path : str
        Filepath to an output directory.
    sampling_rate : float
        Sampling rate of the signal files.
    low : float
        Lower frequency limit of the bandpass filter. The default is 20.
    high : float
        Upper frequency limit of the bandpass filter. The default is 450.
    cols : list, optional
        List of columns of the Signal to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'Time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names
        match the regular expression. The default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    
    Raises
    ------
    Warning
        A warning is raised if no files in 'in_path' match with 'expression'.
    Warning
        A warning is raised if any column in 'cols' in any of the Signal
        files read contain NaN values.
    Exception
        An exception is raised if any column in 'cols' is not found in any of
        the Signal files read.
    Exception
        An exception is raised if any column in 'cols' in any of the Signal
        files read contain NaN values.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.
    Exception
        An exception is raised if 'high' is not higher than 'low'.
    Exception
        An exception is raised if 'high' or 'low' are higher than 1/2 of
        'sampling_rate'.
    Exception
        An exception is raised if a file cannot not be read in 'in_path'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
    
    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("Warning: The regular expression " + str(expression) + " did not match with any files.")
    
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
              
            # Apply filter to columns
            for col in cols:
                data = apply_bandpass_filter(data, col, sampling_rate, low, high)
            
            # Construct out path
            out_file = out_path + file_dirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
        elif (file[-len(file_ext):] == file_ext) and exp_copy:
            # Copy the file even if it doesn't match if exp_copy is true
            data = read_file_type(file_dirs[file], file_ext)
            out_file = out_path + file_dirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
    return

#
# =============================================================================
#

def apply_fwr(Signal, col):
    """
    Apply a Full Wave Rectifier to a Signal.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    fwr_Signal : pd.DataFrame
        A copy of 'Signal' after the full wave rectifier filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signals'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
        
    if Signal[col].isnull().values.any():
        warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
    
    fwr_Signal = Signal.copy()
    fwr_Signal[col] = np.abs(fwr_Signal[col])
    
    return fwr_Signal

#
# =============================================================================
#

def apply_boxcar_smooth(Signal, col, sampling_rate, window_size, min_gap_ms=30.0):
    """
    Apply a boxcar smoothing filter to a Signal. Uses a rolling average with a
    window size.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.
    sampling_rate : float
        Sampling rate of 'Signal'.
    window_size : int, float
        Size of the window of the filter.
    min_gap_ms : float, optional
        Minimum length of time (in ms) for missing data. Segments of missing
        data less than this threshold are ignored in the filter calculation,
        and segments greater than this are used to divide the data, with the
        filter applied to each part. The default is 30.
    
    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'window_size' is less or equal to 0.
    
    Returns
    -------
    boxcar_Signal : pd.DataFrame
        A copy of 'Signal' after the boxcar smoothing filter is applied.

    """
    
    # A warning is raised if 'window_size' is greater than the length of
    # 'Signal'.
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if Signal[col].isnull().values.any():
        warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    # An exception is raised if 'window_size' is less or equal to 0.
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    boxcar_Signal = apply_fwr(Signal, col)
    
    # Calculate gap parameter
    min_gap = int(min_gap_ms * sampling_rate / 1000.0)
    
    # Construct list of NaN locations
    data = boxcar_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data))
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask[nan_ind:nan_ind+nan_len] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = boxcar_Signal[min_nan_mask]
    masked_data = masked_data.copy()
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Apply notch filters to each value sequence set sequences that are too
    # small to NaN
    window = np.ones(window_size) / float(window_size)
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len, col] = np.nan
        else:
            # Apply filter
            filtered_section = np.convolve(masked_data.loc[val_ind:val_ind+val_len, col].copy(), window, 'same')
            masked_data.loc[val_ind:val_ind+val_len, col] = filtered_section
    
    # Put masked_data back in boxcar_Signal
    boxcar_Signal.loc[min_nan_mask, col] = masked_data[col]
    
    return boxcar_Signal

#
# =============================================================================
#

def apply_rms_smooth(Signal, col, sampling_rate, window_size, min_gap_ms=30.0):
    """
    Apply an RMS smoothing filter to a Signal. Uses a rolling average with a
    window size.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.
    sampling_rate : float
        Sampling rate of 'Signal'.
    window_size : int, float
        Size of the window of the filter.
    min_gap_ms : float, optional
        Minimum length of time (in ms) for missing data. Segments of missing
        data less than this threshold are ignored in the filter calculation,
        and segments greater than this are used to divide the data, with the
        filter applied to each part. The default is 30.

    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'window_size' is less or equal to 0.

    Returns
    -------
    rms_Signal : pd.DataFrame
        A copy of 'Signal' after the RMS smoothing filter is applied.

    """
    
    # A warning is raised if 'window_size' is greater than the length of
    # 'Signal'.
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
        
    # Check for NaN - warn and remove if found
    if Signal[col].isnull().values.any():
        warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
    
    # An exception is raised if 'window_size' is less or equal to 0.
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    rms_Signal = Signal.copy()
    
    # Calculate gap parameter
    min_gap = int(min_gap_ms * sampling_rate / 1000.0)
    
    # Construct list of NaN locations
    data = rms_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data))
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask[nan_ind:nan_ind+nan_len] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = rms_Signal[min_nan_mask]
    masked_data = masked_data.copy()
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Apply notch filters to each value sequence set sequences that are too
    # small to NaN
    window = np.ones(window_size) / float(window_size)
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len, col] = np.nan
        else:
            # Apply filter
            filtered_section = np.sqrt(np.convolve(masked_data.loc[val_ind:val_ind+val_len, col].copy() ** 2, window, 'same'))
            masked_data.loc[val_ind:val_ind+val_len, col] = filtered_section
    
    # Put masked_data back in rms_Signal
    rms_Signal.loc[min_nan_mask, col] = masked_data[col]
    
    return rms_Signal

#
# =============================================================================
#

def apply_gaussian_smooth(Signal, col, sampling_rate, window_size, sigma=1, min_gap_ms=30.0):
    """
    Apply a Gaussian smoothing filter to a Signal. Uses a rolling average with
    a window size.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.
    sampling_rate : float
        Sampling rate of 'Signal'.
    window_size : int, float
        Size of the window of the filter.
    sigma : float, optional
        Parameter of sigma in the Gaussian smoothing. The default is 1.
    min_gap_ms : float, optional
        Minimum length of time (in ms) for missing data. Segments of missing
        data less than this threshold are ignored in the filter calculation,
        and segments greater than this are used to divide the data, with the
        filter applied to each part. The default is 30.
        
    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'window_size' is less or equal to 0.

    Returns
    -------
    gauss_Signal : pd.DataFrame
        A copy of 'Signal' after the Gaussian smoothing filter is applied.

    """
    
    # Helper function for creating a Gaussian kernel
    def get_gauss(n, sigma):
        r = range(-int(n/2), int(n/2)+1)
        return [1 / (sigma * np.sqrt(2*np.pi)) * np.exp(-float(x)**2/(2*sigma**2)) for x in r]
    
    # A warning is raised if 'window_size' is greater than the length of
    # 'Signal'.
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + (col) + " not in Signal")
    
    if Signal[col].isnull().values.any():
        warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
    
    # An exception is raised if 'window_size' is less or equal to 0.
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    gauss_Signal = apply_fwr(Signal, col)
    
    # Calculate gap parameter
    min_gap = int(min_gap_ms * sampling_rate / 1000.0)
    
    # Construct list of NaN locations
    data = gauss_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data))
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask[nan_ind:nan_ind+nan_len] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = gauss_Signal[min_nan_mask]
    masked_data = masked_data.copy()
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Apply gaussian filters to each value sequence set sequences that are too
    # small to NaN
    window = get_gauss(window_size, sigma)
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len, col] = np.nan
        else:
            # Apply filter
            filtered_section = np.convolve(masked_data.loc[val_ind:val_ind+val_len, col].copy(), window, 'same')
            masked_data.loc[val_ind:val_ind+val_len, col] = filtered_section
    
    # Put masked_data back in gauss_Signal
    gauss_Signal.loc[min_nan_mask, col] = masked_data[col]
    
    return gauss_Signal

#
# =============================================================================
#

def apply_loess_smooth(Signal, col, sampling_rate, window_size, min_gap_ms=30.0):
    """
    Apply a Loess smoothing filter to a Signal. Uses a rolling average with a
    window size and tri-cubic weight.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.
    sampling_rate : float
        Sampling rate of 'Signal'.
    window_size : int, float
        Size of the window of the filter.
    min_gap_ms : float, optional
        Minimum length of time (in ms) for missing data. Segments of missing
        data less than this threshold are ignored in the filter calculation,
        and segments greater than this are used to divide the data, with the
        filter applied to each part. The default is 30.

    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'window_size' is less or equal to 0.

    Returns
    -------
    loess_Signal : DataFrame
        A copy of 'Signal' after the Loess smoothing filter is applied.

    """
    
    # A warning is raised if 'window_size' is greater than the length of
    # 'Signal'.
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    # A warning is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
    
    # An exception is raised if 'window_size' is less or equal to 0.
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    loess_Signal = apply_fwr(Signal, col)
    
    # Calculate gap parameter
    min_gap = int(min_gap_ms * sampling_rate / 1000.0)
    
    # Construct list of NaN locations
    data = loess_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data))
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask[nan_ind:nan_ind+nan_len] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = loess_Signal[min_nan_mask]
    masked_data = masked_data.copy()
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Apply loess filters to each value sequence set sequences that are too
    # small to NaN
    window = np.linspace(-1,1,window_size+1,endpoint=False)[1:]
    window = np.array(list(map(lambda x: (1 - np.abs(x) ** 3) ** 3, window)))
    window = window / np.sum(window)
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len, col] = np.nan
        else:
            # Apply filter
            filtered_section = np.convolve(masked_data.loc[val_ind:val_ind+val_len, col].copy(), window, 'same')
            masked_data.loc[val_ind:val_ind+val_len, col] = filtered_section
    
    # Put masked_data back in loess_Signal
    loess_Signal.loc[min_nan_mask, col] = masked_data[col]
    
    return loess_Signal

#
# =============================================================================
#

def smooth_filter_signals(in_path, out_path, sampling_rate, window_size, cols=None, expression=None, exp_copy=False, file_ext='csv', method='rms', min_gap_ms=30.0, sigma=1):  
    """
    Apply smoothing filters to all Signals in a folder. Writes filtered Signals
    to an output folder, and generates a file structure matching the input
    folder. The method used to smooth the signals can be specified, but is RMS
    as default.

    Parameters
    ----------
    in_path : dict-str
        Filepath to a directory to read Signal files.
    out_path : str
        Filepath to an output directory.
    sampling_rate : float
        Sampling rate of the signal files.
    window_size : int, float
        Size of the window of the filter.
    cols : list-str, optional
        List of columns of the Signal to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names
        match the regular expression. The default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    method : str, optional
        The smoothing method to use. Can be one of 'rms', 'boxcar', 'gauss' or
        'loess'. The default is 'rms'.
    min_gap_ms : float, optional
        Minimum length of time (in ms) for missing data. Segments of missing
        data less than this threshold are ignored in the filter calculation,
        and segments greater than this are used to divide the data, with the
        filter applied to each part. The default is 30.
    sigma: float, optional
        The value of sigma used for a Gaussian filter. Only affects output when
        using Gaussian filtering.

    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
    Warning
        A warning is raised if 'expression' does not match with any files.
    Warning
        A warning is raised if any column in 'cols' in any of the Signal
        files read contain NaN values.
    Exception
        An exception is raised if an invalid smoothing method is used. Valid
        methods are one of: 'rms', 'boxcar', 'gauss' or 'loess'.
    Exception
        An exception is raised if any column in 'cols' is not found in any of
        the Signal files read.
    Exception
        An exception is raised if 'window_size' is less or equal to 0.
    Exception
        An exception is raised if a file cannot not be read in 'in_path'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("Warning: The regular expression " + str(expression) + " did not match with any files.")
    
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
              
            # Apply filter to columns
            for col in cols:
                if method == 'rms':
                    data = apply_rms_smooth(data, col, sampling_rate, window_size)
                elif method == 'boxcar':
                    data = apply_boxcar_smooth(data, col, sampling_rate, window_size)
                elif method == 'gauss':
                    data = apply_gaussian_smooth(data, col, sampling_rate, window_size, sigma)
                elif method == 'loess':
                    data = apply_loess_smooth(data, col, sampling_rate, window_size)
                else:
                    raise Exception('Invalid smoothing method chosen: ', str(method), ', use "rms", "boxcar", "gauss" or "loess"')
                
            # Construct out path
            out_file = out_path + file_dirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
        
        elif (file[-len(file_ext):] == file_ext) and exp_copy:
            # Copy the file even if it doesn't match if exp_copy is true
            data = read_file_type(file_dirs[file], file_ext)
            out_file = out_path + file_dirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    return

#
# =============================================================================
#

def clean_signals(path_names, sampling_rate=2000):
    """
    Automates the EMG preprocessing workflow, performing notch filtering,
    bandpass filtering and smoothing.

    Parameters
    ----------
    path_names : dict-str
        Dictionary containing path locations for writing and reading Signal
        data between paths.
    sampling_rate : float
        Sampling rate of the signal files.

    Raises
    ------
    Warning
        A warning is raised if any columns of the signal files read contain
        NaN values.
    Exception
        An exception is raised if the provided 'path_names' dictionary doesn't
        contain a 'Raw', 'Notch', 'Bandpass' or 'Smooth' path key.

    Returns
    -------
    None.

    """
    
    # Raise exceptions if paths not found
    if 'Raw' not in path_names:
        raise Exception('Raw path not detected in provided dictionary (path_names)')
    if 'Notch' not in path_names:
        raise Exception('Notch path not detected in provided dictionary (path_names)')
    if 'Bandpass' not in path_names:
        raise Exception('Bandpass path not detected in provided dictionary (path_names)')
    if 'Smooth' not in path_names:
        raise Exception('Smooth path not detected in provided dictionary (path_names)')
    
    # Default values for notch filtering and window size
    notch = [(50,5)]
    window_size = 50
    
    # Automatically runs through workflow
    notch_filter_signals(path_names['Raw'], path_names['Notch'], sampling_rate, notch)
    bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], sampling_rate)
    smooth_filter_signals(path_names['Bandpass'], path_names['Smooth'], sampling_rate, window_size)
    return

#
# =============================================================================
#

def detect_spectral_outliers(in_path, sampling_rate, threshold, cols=None, low=None, high=None, metric=np.median, expression=None, window_size=200, file_ext='csv'):
    """
    Looks at all Signals contained in a filepath, returns a dictionary of file
    names and locations that have outliers.
    
    Works by interpolating an inverse function from the peaks of the signal's
    spectrum. The function then calculates the 'metric' aggregate of the
    differences between the predicted spectrum intensity of the inverse
    function, and the actual spectrum intensity of the peaks. Finally, if the
    largest difference between the predicted and actual values is greater than
    the metric average multiplied by the threshold value, the file is flagged
    for having an outlier and is added to the dictionary.

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read Signal files.
    sampling_rate : float
        Sampling rate of the Signal.
    threshold : float
        The number of times greater than the metric a value has to be to be
        considered an outlier.
    cols : list-str, optional
        List of columns of the Signal to search for outliers in. The default is
        None, in which case outliers are searched for in every column except
        for 'time'.
    low : float, optional
        Lower frequency limit of where to search for outliers. Should be the
        same as lower limit for bandpass filtering, or some value that
        eliminates the irrelevant lower frequency ranges. The default is None,
        in which case no lower threshold is used.
    high : float, optional
        Upper frequency limit of where to search for outliers. Should be the
        same as upper limit for bandpass filtering, or some value that
        eliminates the irrelevant upper frequency ranges. The default is None,
        in which case no upper threshold is used.
    metric : function, optional
        Some summary function that defines the metric used for finding
        outliers. The default is 'np.median', but others such as 'np.mean' can
        be used instead.
    expression : str, optional
        A regular expression. If provided, will only search for outliers in
        files whose names match the regular expression. The default is None.
    window_size : int, optional
        The window size to use when filtering for local maxima. The default is
        200.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.

    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than half the size of
        a file read by the function.
    Exception
        An exception is raised if 'window_size' is not an integer greater than
        0.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.
    Exception
        An exception is raised if 'threshold' is less or equal to 0.
    Exception
        An exception is raised if 'low' is greater than 'high'.
    Exception
        An exception is raised if 'low' or 'high' are negative.
    Exception
        An exception is raised if 'metric' is not a valid summary function.
    Exception
        An exception is raised if a column in 'cols' is not in a data file.
    Exception
        An exception is raised if a file cannot not be read in 'in_path'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.

    Returns
    -------
    outliers : dict-str
        Dictionary of file names/locations as keys/values for each file
        detected that contains an outlier.

    """
    
    if not type(window_size) == int:
        raise Exception("'window_size' must be a valid integer.")
    
    if window_size <= 0:
        raise Exception("'window_size' cannot be 0 or less.")
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided.")
    
    if threshold <= 0:
        raise Exception("'threshold' must be greater than 0.")
    
    try:
        metric([1,2,3,4,5])
    except:
        raise Exception("Invalid summary metric provided, 'metric' must be able to take a single numeric list as input.")
    
    p_deg = 1   # Degree of equation on the top of the fraction
    q_deg = 2   # Degree of equation on the bottom of the fraction
    
    # Set low and high if left none
    if low is None:
        low = 0
    if high is None:
        high = sampling_rate/2
    
    if low >= high:
        raise Exception("'low' (" + str(low) + ") must be greater than 'high' (" + str(high), ").")
    
    if low < 0 or high < 0:
        raise Exception("'low' and 'high' must be positive values.")
    
    # Create rational function equation
    def Rational(x, *params):
        p = params[:p_deg]
        q = params[p_deg:]
        return np.polyval(p, x) / np.polyval(q, x)
    
    # Zooms in on a frequency range in a PSD plot
    def ZoomIn(data, a, b):
        data = data[data['Frequency'] >= a]
        data = data[data['Frequency'] <= b]
        return data
    
    outliers = {}
    
    # Convert path to absolute
    if not os.path.isabs(in_path):
        in_path = os.path.abspath(in_path)
    
    # Get dictionary of files
    file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
    
    # Iterate over detected files
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            if len(data.index)/2 <= window_size:
                warnings.warn("Warning: window_size is greater than 1/2 of data file, results may be poor.")
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
            
            # Set to false
            isOutlier = False
            
            # Iterate over columns
            for i in range(len(cols)):
                col = cols[i]
                
                if col not in list(data.columns.values):
                    raise Exception("Column " + str(col) + " is not in 'Signal': " + str(file))
                
                psd = emg_to_psd(data, col, sampling_rate=sampling_rate)
                psd = ZoomIn(psd, low, high)
                
                # Create column containing local maxima
                psd['max'] = psd.iloc[scipy.signal.argrelextrema(psd['Power'].values, np.greater_equal, order=window_size)[0]]['Power']
                
                # Filter non-maxima
                maxima = psd[psd['max'].notnull()]
                
                if len(maxima.index) == 1:
                    raise Exception("Not enough maxima to create approximation - reduce 'window_size' or use a larger data file.")
    
                # Initialize rational function parameters
                p_init = np.poly1d(np.ones(p_deg))
                q_init = np.poly1d(np.ones(q_deg))
                params_init = np.hstack((p_init.coeffs, q_init.coeffs))
                
                # Fit rational equation
                params_best, params_cov = scipy.optimize.curve_fit(
                    Rational, maxima['Frequency'], maxima['Power'], p0=params_init)
                
                # Get y-values
                y_vals = Rational(maxima['Frequency'], *params_best)
                
                # Get differences between predicted and actual power levels
                diffs = abs(y_vals - maxima['Power'])
                
                # Get metric of data
                data_metric = metric(diffs)
                
                # Find biggest difference between predicted and actual values
                max_fit = np.max(maxima['Power'] - y_vals)
                
                if (max_fit > data_metric * threshold):
                    isOutlier = True
            
            # If any columns have an outlier, mark as an outlier
            if isOutlier:
                outliers[file] = file_dirs[file]
                
    return outliers

#
# =============================================================================
#

def apply_screen_artefacts(Signal, col, method='robust'):
    """
    Creates a NaN mask for a column of a signal dataframe.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the NaN mask is created from.
    method : str, optional
        The outlier detection method being used. Valid options are 'robust',
        'normal', or None. The default is 'robust'.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'method' is an invalid screening method.

    Returns
    -------
    masked_Signal : pd.DataFrame
        A copy of the 'Signal' dataframe with an added column for the NaN mask.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    masked_Signal = Signal.copy()
    
    # Identify outlier parameters
    if method=='robust':
        # Set high and low with robust method
        high = np.nanmedian(masked_Signal[col]) + 5*(1.482*scipy.stats.median_abs_deviation(masked_Signal[col], nan_policy='omit'))
        low = np.nanmedian(masked_Signal[col]) - 5*(1.482*scipy.stats.median_abs_deviation(masked_Signal[col], nan_policy='omit'))
    elif method=='normal':
        # Set high and low with normal method
        high = np.nanmean(masked_Signal[col]) + 5*np.nanstd(masked_Signal[col])
        low = np.nanmean(masked_Signal[col]) - 5*np.nanstd(masked_Signal[col])
    elif method is None:
        pass
    else:
        raise Exception('Invalid outlier detection method chosen: ' + str(method) + ', use "robust", "normal" or None.')
    
    # Create NaN mask and add to masked_Signal
    mask = (masked_Signal[col] > low) & (masked_Signal[col] < high) & (~masked_Signal[col].isna())
    masked_Signal['mask_' + str(col)] = mask
    
    return masked_Signal

#
# =============================================================================
#

def screen_artefact_signals(in_path, out_path, sampling_rate, method='robust', cols=None, expression=None, exp_copy=False, file_ext='csv'):
    """
    

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    out_path : str
        Filepath to an output directory.
    sampling_rate : float
        Sampling rate of the signal files.
    method : str, optional
        The outlier detection method being used. Valid options are 'robust',
        'normal', or None. The default is 'robust'.
    cols : list-str, optional
        List of columns of the signal to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'Time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names
        match the regular expression. The default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.

    Raises
    ------
    Warning
        Raises a warning if no files in 'in_path' match with 'expression'.
    Warning
        A warning is raised if any column in 'cols' in any of the Signal
        files read contain NaN values.
    Exception
        An exception is raised if any column in 'cols' is not found in any of
        the signal files read.
    Exception
        An exception is raised if 'sampling_rate' is less or equal to 0.
    Exception
        An exception is raised if 'method' is an invalid screening method.
    Exception
        An exception is raised if a file cannot not be read in 'in_path'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.

    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("Warning: The regular expression " + str(expression) + " did not match with any files.")
        
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
            
            # Apply filter to columns
            for col in cols:
                data = apply_screen_artefacts(data, col, method=method)
            
            # Construct out path
            out_file = out_path + file_dirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
        elif (file[-len(file_ext):] == file_ext) and exp_copy:
            # Copy the file even if it doesn't match if exp_copy is true
            data = read_file_type(file_dirs[file], file_ext)
            out_file = out_path + file_dirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    
    return