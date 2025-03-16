import importlib.resources as resources
import scipy
import pandas as pd
import numpy as np
import os
import re
from tqdm import tqdm
import warnings

from .FileAccess import *

#
# =============================================================================
#

"""
A collection of functions for filtering Signals.
"""

#
# =============================================================================
#

def EMG2PSD(Sig_vals, sampling_rate=1000, normalize=True):
    """
    Creates a PSD graph of a Signal. Uses the Welch method, meaning it can be
    used as a Long Term Average Spectrum (LTAS).

    Parameters
    ----------
    Sig_vals : float list
        A list of float values. A column of a Signal.
    sampling_rate : float
        Sampling rate of the Signal.
    normalize : bool, optional
        If True, will normalize the result. If False, will not. The default is
        True.

    Raises
    ------
    Exception
        An exception is raised if the sampling rate is less or equal to 0

    Returns
    -------
    psd : DataFrame
        A DataFrame containing a 'Frequency' and 'Power' column. The Power
        column indicates the intensity of each frequency in the Signal
        provided. Results will be normalized if 'normalize' is set to True.
    
    """
    
    if sampling_rate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0")
    
    # Initial parameters
    Sig_vals = Sig_vals - np.mean(Sig_vals)
    N = len(Sig_vals)
    
    # Calculate minimum frequency given sampling rate
    min_frequency = (2 * sampling_rate) / (N / 2)
    
    # Calculate window size givern sampling rate
    nperseg = int((2 / min_frequency) * sampling_rate)
    nfft = nperseg * 2
    
    # Apply welch method with hanning window
    frequency, power = scipy.signal.welch(
        Sig_vals,
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

def ApplyNotchFilters(Signal, col, sampling_rate, notch_vals):
    """
    Apply a list of notch filters for given frequencies and Q-factors to a
    column of the provided data.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.
    sampling_rate : float
        Sampling rate of the Signal.
    notch_vals : list
        A list of (Hz, Q) tuples corresponding to the notch filters being
        applied. Hz is the frequency to apply the filter to, and Q is the
        Q-score (an intensity score where a higher number means a less extreme
        filter).

    Raises
    ------
    Exception
        An exception is raised if the column is not found in the Signal.
    Exception
        An exception is raised if the sampling rate is less or equal to 0.
    Exception
        An exception is raised if a Hz value in notch_vals is greater than
        sampling_rate/2 or less than 0

    Returns
    -------
    DataFrame
        A copy of Signal after the notch filters are applied.

    """

    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    if sampling_rate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0")

    def ApplyNotchFilter(Signal, col, sampling_rate, notch):
        """
        Apply a notch filter to a signal

        Parameters
        ----------
        Signal : DataFrame
            A Pandas DataFrame containing a 'Time' column, and additional
            columns for signal data.
        col : str
            Column of the Signal to apply the filter to.
        sampling_rate : float
            Sampling rate of the Signal.
        notch : (int, int) tuple
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
        Signal_col : Series
            A Pandas Series of the provided column with the notch filter applied

        """
        
        Signal = Signal.copy()
        
        (Hz, Q) = notch
        
        if Hz > sampling_rate / 2 or Hz < 0:
            raise Exception("Notch filter frequency must be between 0 and " + str(sampling_rate / 2) + " (sampling_rate/2)")
        
        # Normalize filtering frequency
        nyq_freq = sampling_rate / 2
        norm_Hz = Hz / nyq_freq
        
        # Use scipy notch filter using normalized frequency
        b, a = scipy.signal.iirnotch(norm_Hz, Q)
        Signal_col = scipy.signal.lfilter(b, a, Signal[col])
        
        return Signal_col
    
    Signal = Signal.copy()
    
    # Applies ApplyNotchFilter for every notch_val tuple
    for i in range(len(notch_vals)):
        Signal[col] = ApplyNotchFilter(Signal, col, sampling_rate, notch_vals[i])
    return Signal

#
# =============================================================================
#

def NotchFilterSignals(in_path, out_path, sampling_rate, notch, cols=None, expression=None, exp_copy=False, file_ext='csv'):
    """
    Apply notch filters to all Signals in a folder. Writes filtered Signals to
    an output folder, and generates a file structure matching the input folder.

    Parameters
    ----------
    in_path : dict
        Filepath to a directory to read Signal files.
    out_path : str
        Filepath to an output directory.
    sampling_rate : float
        Sampling rate of the Signal.
    notch : list
        A list of (Hz, Q) tuples corresponding to the notch filters being
        applied. Hz is the frequency to apply the filter to, and Q is the
        Q-score (an intensity score where a higher number means a less
        extreme filter).
    cols : list, optional
        List of columns of the Signal to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'Time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names
        match the regular expression. The default is None.
    exp_copy : TYPE, optional
        If true, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : TYPE, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.

    Raises
    ------
    Exception
        An exception is raised if the column is not found in any of the Signal
        files found.
    Exception
        An exception is raised if the sampling rate is less or equal to 0.
    Exception
        An exception is raised if a Hz value in notch_vals is greater than
        sampling_rate/2 or less than 0
    Exception
        Raises an exception if a file cannot not be read in in_path.
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
        filedirs = MapFiles(in_path, file_ext=file_ext)
    else:
        filedirs = MapFiles(in_path, file_ext=file_ext, expression=expression)
        if len(filedirs) == 0:
            warnings.warn("Warning: The regular expression " + expression + " did not match with any files.")
        
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            # Read file
            data = ReadFileType(filedirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
            
            # Apply filter to columns
            for col in cols:
                data = ApplyNotchFilters(data, col, sampling_rate, notch)
            
            # Construct out path
            out_file = out_path + filedirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
        elif (file[-len(file_ext):] == file_ext) and exp_copy:
            # Copy the file even if it doesn't match if exp_copy is true
            data = ReadFileType(filedirs[file], file_ext)
            out_file = out_path + filedirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    
    return

#
# =============================================================================
#

def ApplyBandpassFilter(Signal, col, sampling_rate, low, high):
    """
    Apply a bandpass filter to a Signal for a given lower and upper limit.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.
    sampling_rate : float
        Sampling rate of the Signal.
    low : float
        Lower frequency limit of the bandpass filter.
    high : float
        Upper frequency limit of the bandpass filter.

    Raises
    ------
    Exception
        An exception is raised if the column is not found in the Signal.
    Exception
        An exception is raised if the sampling rate is less or equal to 0.
    Exception
        An exception is raised if high is not higher than low.

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the bandpass filter is applied.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal.")
    
    if sampling_rate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0.")
    
    if high > sampling_rate/2 or low > sampling_rate/2:
        raise Exception("'high' and 'low' cannot be greater than 1/2 the sampling rate.")
    
    if high <= low:
        raise Exception("'high' must be higher than 'low'.")
    
    
    Signal = Signal.copy()
    # Here, the "5" is the order of the butterworth filter
    # (how quickly the signal is cut off)
    b, a = scipy.signal.butter(5, [low, high], fs=sampling_rate, btype='band')
    Signal[col] = scipy.signal.lfilter(b, a, Signal[col])
    return Signal

#
# =============================================================================
#

def BandpassFilterSignals(in_path, out_path, sampling_rate, low=20, high=450, cols=None, expression=None, exp_copy=False, file_ext='csv'):
    """
    Apply bandpass filters to all Signals in a folder. Writes filtered Signals
    to an output folder, and generates a file structure
    matching the input folder.
    
    Parameters
    ----------
    in_path : dict
        Filepath to a directory to read Signal files.
    out_path : str
        Filepath to an output directory.
    sampling_rate : float
        Sampling rate of the Signal.
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
        If true, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    
    Raises
    ------
    Exception
        An exception is raised if the column is not found in any of the Signal
        files found.
    Exception
        An exception is raised if the sampling rate is less or equal to 0.
    Exception
        An exception is raised if high is not higher than low.
    Exception
        Raises an exception if a file cannot not be read in in_path.
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
        filedirs = MapFiles(in_path, file_ext=file_ext)
    else:
        filedirs = MapFiles(in_path, file_ext=file_ext, expression=expression)
        if len(filedirs) == 0:
            warnings.warn("Warning: The regular expression " + expression + " did not match with any files.")
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = ReadFileType(filedirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
              
            # Apply filter to columns
            for col in cols:
                data = ApplyBandpassFilter(data, col, sampling_rate, low, high)
            
            # Construct out path
            out_file = out_path + filedirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
        elif (file[-len(file_ext):] == file_ext) and exp_copy:
            # Copy the file even if it doesn't match if exp_copy is true
            data = ReadFileType(filedirs[file], file_ext)
            out_file = out_path + filedirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
    return

#
# =============================================================================
#

def ApplyFWR(Signal, col):
    """
    Apply a Full Wave Rectifier to a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.

    Raises
    ------
    Exception
        An exception is raised if the column is not found in the Signal.

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the full wave rectifier filter is applied.

    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    Signal = Signal.copy()
    Signal[col] = np.abs(Signal[col])
    return Signal

#
# =============================================================================
#

def ApplyBoxcarSmooth(Signal, col, window_size):
    """
    Apply a boxcar smoothing filter to a Signal. Uses a rolling average with a
    window size.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.
    window_size : int, float
        Size of the window of the filter.
    
    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if window_size is less or equal to 0.
    Warning
        A warning is raised if window_size is greater than Signal length.
    
    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the boxcar smoothing filter is applied.

    """
    
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
        
    
    Signal = Signal.copy()
    
    Signal = ApplyFWR(Signal, col)
    # Construct kernel
    window = np.ones(window_size) / float(window_size)
    # Convolve
    Signal[col] = np.convolve(Signal[col], window, 'same')
    return Signal

#
# =============================================================================
#

def ApplyRMSSmooth(Signal, col, window_size):
    """
    Apply an RMS smoothing filter to a Signal. Uses a rolling average with a
    window size.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.
    window_size : int, float
        Size of the window of the filter.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if window_size is less or equal to 0.
    Warning
        A warning is raised if window_size is greater than Signal length.

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the RMS smoothing filter is applied.

    """
    
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    
    
    Signal = Signal.copy()
    # Square
    Signal[col] = np.power(Signal[col], 2)
    # Construct kernel
    window = np.ones(window_size) / float(window_size)
    # Convolve and square root
    Signal[col] = np.sqrt(np.convolve(Signal[col], window, 'same'))
    return Signal

#
# =============================================================================
#

def ApplyGaussianSmooth(Signal, col, window_size, sigma=1):
    """
    Apply a Gaussian smoothing filter to a Signal. Uses a rolling average with
    a window size.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.
    window_size : int, float
        Size of the window of the filter.
    sigma : float, optional
        Parameter of sigma in the Gaussian smoothing. The default is 1.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if window_size is less or equal to 0.
    Warning
        A warning is raised if window_size is greater than Signal length.

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the Gaussian smoothing filter is applied.

    """
    
    # Helper function for creating a Gaussian kernel
    def getGauss(n, sigma):
        r = range(-int(n/2), int(n/2)+1)
        return [1 / (sigma * np.sqrt(2*np.pi)) * np.exp(-float(x)**2/(2*sigma**2)) for x in r]
    
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    Signal = Signal.copy()
    
    Signal = ApplyFWR(Signal, col)
    # Construct kernel
    window = getGauss(window_size, sigma)
    # Convolve
    Signal[col] = np.convolve(Signal[col], window, 'same')
    return Signal

#
# =============================================================================
#

def ApplyLoessSmooth(Signal, col, window_size):
    """
    Apply a Loess smoothing filter to a Signal. Uses a rolling average with a
    window size and tri-cubic weight.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.
    window_size : int, float
        Size of the window of the filter.

    Raises
    ------
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if window_size is less or equal to 0.
    Warning
        A warning is raised if window_size is greater than Signal length.

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the Loess smoothing filter is applied.

    """
    
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    Signal = Signal.copy()
    
    Signal = ApplyFWR(Signal, col)
    # Construct kernel
    window = np.linspace(-1,1,window_size+1,endpoint=False)[1:]
    window = np.array(list(map(lambda x: (1 - np.abs(x) ** 3) ** 3, window)))
    window = window / np.sum(window)
    # Convolve
    Signal[col] = np.convolve(Signal[col], window, 'same')
    return Signal

#
# =============================================================================
#

def SmoothFilterSignals(in_path, out_path, window_size, cols=None, expression=None, exp_copy=False, file_ext='csv', method='rms', sigma=1):  
    """
    Apply smoothing filters to all Signals in a folder. Writes filtered Signals
    to an output folder, and generates a file structure matching the input
    folder. The method used to smooth the signals can be specified, but is RMS
    as default.

    Parameters
    ----------
    in_path : dict
        Filepath to a directory to read Signal files.
    out_path : str
        Filepath to an output directory.
    window_size : int, float
        Size of the window of the filter.
    cols : list, optional
        List of columns of the Signal to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names
        match the regular expression. The default is None.
    exp_copy : bool, optional
        If true, copies files that don't match the regular expression to the
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
    Exception
        An exception is raised if an invalid smoothing method is used. Valid
        methods are one of: 'rms', 'boxcar', 'gauss' or 'loess'.
    Exception
        An exception is raised if col is not found in any of the Signal files.
    Exception
        An exception is raised if window_size is less or equal to 0.
    Warning
        A warning is raised if window_size is greater than Signal length.
    Exception
        Raises an exception if a file cannot not be read in in_path.
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
        filedirs = MapFiles(in_path, file_ext=file_ext)
    else:
        filedirs = MapFiles(in_path, file_ext=file_ext, expression=expression)
        if len(filedirs) == 0:
            warnings.warn("Warning: The regular expression " + expression + " did not match with any files.")
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = ReadFileType(filedirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
              
            # Apply filter to columns
            for col in cols:
                if method == 'rms':
                    data = ApplyRMSSmooth(data, col, window_size)
                elif method == 'boxcar':
                    data = ApplyBoxcarSmooth(data, col, window_size)
                elif method == 'gauss':
                    data = ApplyGaussianSmooth(data, col, window_size, sigma)
                elif method == 'loess':
                    data = ApplyLoessSmooth(data, col, window_size)
                else:
                    raise Exception('Invalid smoothing method used: ', method, ', use "rms", "boxcar", "gauss" or "loess"')
                
            # Construct out path
            out_file = out_path + filedirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
        
        elif (file[-len(file_ext):] == file_ext) and exp_copy:
            # Copy the file even if it doesn't match if exp_copy is true
            data = ReadFileType(filedirs[file], file_ext)
            out_file = out_path + filedirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    return

#
# =============================================================================
#

# Create a sample_data variable with sample data for the package.
with resources.open_text('EMGFlow', 'sample_data.csv') as file:
    sample_data = pd.read_csv(file)