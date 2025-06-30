import scipy
import itertools
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
        raise Exception("Column " + str(col) + " not in Signal")
        
    # A warning is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
    
    # An exception is raised if 'sampling_rate' is less or equal to 0.
    if sampling_rate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0")

    def apply_notch_filter(Signal, col, sampling_rate, notch):
        """
        Apply a notch filter to a signal.

        Parameters
        ----------
        Signal : pd.DataFrame
            A Pandas dataframe containing a 'Time' column, and additional
            columns for signal data.
        col : str
            Column of 'Signal' the filter is applied to.
        sampling_rate : float
            Sampling rate of 'Signal'.
        notch : tuple
            Notch filter data. Should be a (Hz, Q) tuple where Hz is the
            frequency to apply the filter to, and Q. is the Q-score (an
            intensity score where a higher number means a less extreme filter).

        Raises
        ------
        Warning
            A warning is raised if 'col' contains NaN values.
        Exception
            An exception is raised if the Hz value in notch is greater than
            sampling_rate/2 or less than 0.

        Returns
        -------
        notch_signal_col : pd.Series
            A Pandas series of the provided column with the notch filter
            applied.

        """
        
        Signal = Signal.copy()
        (Hz, Q) = notch
        
        if Signal[col].isnull().values.any():
            raise Exception("NaN values were detected in the dataframe.")
        
        # An exception is raised if 'col' is not a column of 'Signal'.
        if col not in list(Signal.columns.values):
            raise Exception("Column " + str(col) + " not in Signal")
        
        # An exception is raised if a Hz value in 'notch_vals' is greater than
        # sampling_rate/2 or less than 0.
        if Hz > sampling_rate / 2 or Hz < 0:
            raise Exception("Notch filter frequency must be between 0 and " + str(sampling_rate / 2) + " (sampling_rate/2)")
        
        # Normalize filtering frequency
        nyq_freq = sampling_rate / 2
        norm_Hz = Hz / nyq_freq
        
        # Remove NaN values
        notch_signal_col = Signal[col]
        
        # Use scipy notch filter using normalized frequency
        b, a = scipy.signal.iirnotch(norm_Hz, Q)
        notch_signal_col = scipy.signal.lfilter(b, a, notch_signal_col)
        
        return notch_signal_col
    
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
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len, col] = np.nan
        else:
            # Apply filter
            for notch_val in notch_vals:
                filtered_section = apply_notch_filter(masked_data.loc[val_ind:val_ind+val_len].copy(), col, sampling_rate, notch_val)
                masked_data.loc[val_ind:val_ind+val_len, col] = filtered_section
    
    # Put masked_data back in notch_Signal
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