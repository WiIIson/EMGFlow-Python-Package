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

def emg_to_psd(sig_vals, sampling_rate=1000, normalize=True):
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

def apply_notch_filters(Signal, col, sampling_rate, notch_vals):
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

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'col' contains NaN values.
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
        Exception
            An exception is raised if the Hz value in notch is greater than
            sampling_rate/2 or less than 0.

        Returns
        -------
        SignalCol : pd.Series
            A Pandas series of the provided column with the notch filter
            applied.

        """
        
        Signal = Signal.copy()
        (Hz, Q) = notch
        
        # An exception is raised if a Hz value in 'notch_vals' is greater than
        # sampling_rate/2 or less than 0.
        if Hz > sampling_rate / 2 or Hz < 0:
            raise Exception("Notch filter frequency must be between 0 and " + str(sampling_rate / 2) + " (sampling_rate/2)")
        
        # Normalize filtering frequency
        nyq_freq = sampling_rate / 2
        norm_Hz = Hz / nyq_freq
        
        # Check for NaN - warn and remove if found
        if Signal[col].isnull().values.any():
            warnings.warn("Warning: NaN values detected in dataframe. These values will be ignored.")
        
        # Find indices of NaN values
        nan_ind = np.isnan(Signal[col])
        
        # Remove NaN values
        filtered_signal = Signal[col][~nan_ind]
        
        # Use scipy notch filter using normalized frequency
        b, a = scipy.signal.iirnotch(norm_Hz, Q)
        filtered_signal = scipy.signal.lfilter(b, a, filtered_signal)
        
        # Reinsert NaN values
        SignalCol = np.full_like(Signal[col], np.nan)
        SignalCol[~nan_ind] = filtered_signal
        
        return SignalCol
    
    notch_Signal = Signal.copy()
    
    # Applies apply_notch_filter for every notch_val tuple
    for i in range(len(notch_vals)):
        notch_Signal[col] = apply_notch_filter(notch_Signal, col, sampling_rate, notch_vals[i])
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
        Filepath to a directory to read Signal files.
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
        Raises a warning if no files in 'in_path' match with 'expression'.
    Exception
        An exception is raised if any column in 'cols' is not found in any of
        the Signal files read.
    Exception
        An exception is raised if any column in 'cols' in any of the Signal
        files read contain NaN values.
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

def apply_bandpass_filter(Signal, col, sampling_rate, low, high):
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

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'col' contains NaN values.
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
    
    # An exception is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        raise Exception("NaN values found in column: " + str(col))
    
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
    # Here, the "5" is the order of the butterworth filter
    # (how quickly the signal is cut off)
    b, a = scipy.signal.butter(5, [low, high], fs=sampling_rate, btype='band')
    band_Signal[col] = scipy.signal.lfilter(b, a, band_Signal[col])
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
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'col' contains NaN values.

    Returns
    -------
    fwr_Signal : pd.DataFrame
        A copy of 'Signal' after the full wave rectifier filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signals'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
        
    # An exception is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        raise Exception("NaN values found in column: " + str(col))
    
    fwr_Signal = Signal.copy()
    fwr_Signal[col] = np.abs(fwr_Signal[col])
    return fwr_Signal

#
# =============================================================================
#

def apply_boxcar_smooth(Signal, col, window_size):
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
    window_size : int, float
        Size of the window of the filter.
    
    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'col' contains NaN values.
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
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    # An exception is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        raise Exception("NaN values found in column: " + str(col))
    
    # An exception is raised if 'window_size' is less or equal to 0.
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
        
    
    boxcar_Signal = Signal.copy()
    boxcar_Signal = apply_fwr(boxcar_Signal, col)
    
    # Construct kernel
    window = np.ones(window_size) / float(window_size)
    # Convolve
    boxcar_Signal[col] = np.convolve(boxcar_Signal[col], window, 'same')
    return boxcar_Signal

#
# =============================================================================
#

def apply_rms_smooth(Signal, col, window_size):
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
    window_size : int, float
        Size of the window of the filter.

    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'col' contains NaN values.
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
        
    # An exception is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        raise Exception("NaN values found in column: " + str(col))
    
    # An exception is raised if 'window_size' is less or equal to 0.
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    
    
    rms_Signal = Signal.copy()
    # Square
    rms_Signal[col] = np.power(rms_Signal[col], 2)
    # Construct kernel
    window = np.ones(window_size) / float(window_size)
    # Convolve and square root
    rms_Signal[col] = np.sqrt(np.convolve(rms_Signal[col], window, 'same'))
    return rms_Signal

#
# =============================================================================
#

def apply_gaussian_smooth(Signal, col, window_size, sigma=1):
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
    window_size : int, float
        Size of the window of the filter.
    sigma : float, optional
        Parameter of sigma in the Gaussian smoothing. The default is 1.

    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'col' contains NaN values.
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
    
    # An exception is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        raise Exception("NaN values found in column: " + str(col))
    
    # An exception is raised if 'window_size' is less or equal to 0.
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    gauss_Signal = Signal.copy()
    
    gauss_Signal = apply_fwr(gauss_Signal, col)
    # Construct kernel
    window = get_gauss(window_size, sigma)
    # Convolve
    gauss_Signal[col] = np.convolve(gauss_Signal[col], window, 'same')
    return gauss_Signal

#
# =============================================================================
#

def apply_loess_smooth(Signal, col, window_size):
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
    window_size : int, float
        Size of the window of the filter.

    Raises
    ------
    Warning
        A warning is raised if 'window_size' is greater than the length of
        'Signal'.
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
    
    # An exception is raised if 'col' contains NaN values.
    if Signal[col].isnull().values.any():
        raise Exception("NaN values found in column: " + str(col))
    
    # An exception is raised if 'window_size' is less or equal to 0.
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    loess_Signal = Signal.copy()
    
    loess_Signal = apply_fwr(loess_Signal, col)
    # Construct kernel
    window = np.linspace(-1,1,window_size+1,endpoint=False)[1:]
    window = np.array(list(map(lambda x: (1 - np.abs(x) ** 3) ** 3, window)))
    window = window / np.sum(window)
    # Convolve
    loess_Signal[col] = np.convolve(loess_Signal[col], window, 'same')
    return loess_Signal

#
# =============================================================================
#

def smooth_filter_signals(in_path, out_path, window_size, cols=None, expression=None, exp_copy=False, file_ext='csv', method='rms', sigma=1):  
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
    Exception
        An exception is raised if an invalid smoothing method is used. Valid
        methods are one of: 'rms', 'boxcar', 'gauss' or 'loess'.
    Exception
        An exception is raised if any column in 'cols' is not found in any of
        the Signal files read.
    Exception
        An exception is raised if any column in 'cols' in any of the Signal
        files read contain NaN values.
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
                    data = apply_rms_smooth(data, col, window_size)
                elif method == 'boxcar':
                    data = apply_boxcar_smooth(data, col, window_size)
                elif method == 'gauss':
                    data = apply_gaussian_smooth(data, col, window_size, sigma)
                elif method == 'loess':
                    data = apply_loess_smooth(data, col, window_size)
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
    smooth_filter_signals(path_names['Bandpass'], path_names['Smooth'], window_size)
    return