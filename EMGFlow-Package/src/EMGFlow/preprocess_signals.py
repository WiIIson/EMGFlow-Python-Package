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

def emg_to_psd(sigVals, samplingRate=1000, normalize=True):
    """
    Creates a PSD graph of a Signal. Uses the Welch method, meaning it can be
    used as a Long Term Average Spectrum (LTAS).

    Parameters
    ----------
    sigVals : list-float
        A list of float values. A column of a Signal.
    samplingRate : float
        Sampling rate of the Signal.
    normalize : bool, optional
        If True, will normalize the result. If False, will not. The default is
        True.

    Raises
    ------
    Exception
        An exception is raised if 'samplingRate' is less or equal to 0

    Returns
    -------
    psd : pd.DataFrame
        A dataframe containing a 'Frequency' and 'Power' column. The 'Power'
        column indicates the intensity of each frequency in the Signal
        provided. Results will be normalized if 'normalize' is set to True.
    
    """
    
    if samplingRate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0")
    
    # Initial parameters
    sigVals = sigVals - np.mean(sigVals)
    N = len(sigVals)
    
    # Calculate minimum frequency given sampling rate
    min_frequency = (2 * samplingRate) / (N / 2)
    
    # Calculate window size givern sampling rate
    nperseg = int((2 / min_frequency) * samplingRate)
    nfft = nperseg * 2
    
    # Apply welch method with hanning window
    frequency, power = scipy.signal.welch(
        sigVals,
        fs=samplingRate,
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

def apply_notch_filters(Signal, col, samplingRate, notchVals):
    """
    Apply a list of notch filters for given frequencies and Q-factors to a
    column of the provided data.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.
    samplingRate : float
        Sampling rate of the Signal.
    notchVals : list-tuple
        A list of (Hz, Q) tuples corresponding to the notch filters being
        applied. Hz is the frequency to apply the filter to, and Q is the
        Q-score (an intensity score where a higher number means a less extreme
        filter).

    Raises
    ------
    Exception
        An exception is raised if the column 'col' is not found in the Signal.
    Exception
        An exception is raised if 'samplingRate' is less or equal to 0.
    Exception
        An exception is raised if a Hz value in 'notchVals' is greater than
        samplingRate/2 or less than 0

    Returns
    -------
    Signal : pd.DataFrame
        A copy of the 'Signal' dataframe with the notch filters are applied.

    """

    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    if samplingRate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0")

    def apply_notch_filter(Signal, col, samplingRate, notch):
        """
        Apply a notch filter to a signal.

        Parameters
        ----------
        Signal : pd.DataFrame
            A Pandas dataframe containing a 'Time' column, and additional
            columns for signal data.
        col : str
            Column of the Signal to apply the filter to.
        samplingRate : float
            Sampling rate of the Signal.
        notch : tuple
            Notch filter data. Should be a (Hz, Q) tuple where Hz is the
            frequency to apply the filter to, and Q. is the Q-score (an
            intensity score where a higher number means a less extreme filter).

        Raises
        ------
        Exception
            An exception is raised if the Hz value in notch is greater than
            samplingRate/2 or less than 0.

        Returns
        -------
        SignalCol : Series
            A Pandas series of the provided column with the notch filter
            applied.

        """
        
        Signal = Signal.copy()
        
        (Hz, Q) = notch
        
        if Hz > samplingRate / 2 or Hz < 0:
            raise Exception("Notch filter frequency must be between 0 and " + str(samplingRate / 2) + " (samplingRate/2)")
        
        # Normalize filtering frequency
        nyq_freq = samplingRate / 2
        norm_Hz = Hz / nyq_freq
        
        # Use scipy notch filter using normalized frequency
        b, a = scipy.signal.iirnotch(norm_Hz, Q)
        SignalCol = scipy.signal.lfilter(b, a, Signal[col])
        
        return SignalCol
    
    Signal = Signal.copy()
    
    # Applies apply_notch_filter for every notch_val tuple
    for i in range(len(notchVals)):
        Signal[col] = apply_notch_filter(Signal, col, samplingRate, notchVals[i])
    return Signal

#
# =============================================================================
#

def notch_filter_signals(inPath, outPath, samplingRate, notch, cols=None, expression=None, expCopy=False, fileExt='csv'):
    """
    Apply notch filters to all Signals in a folder. Writes filtered Signals to
    an output folder, and generates a file structure matching the input folder.

    Parameters
    ----------
    inPath : str
        Filepath to a directory to read Signal files.
    outPath : str
        Filepath to an output directory.
    samplingRate : float
        Sampling rate of the Signal.
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
    expCopy : bool, optional
        If true, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    fileExt : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.

    Raises
    ------
    Warning
        Raises a warning if no files in 'inPath' match with 'expression'.
    Exception
        An exception is raised if any column in 'cols' is not found in any of
        the Signal files read.
    Exception
        An exception is raised if 'samplingRate' is less or equal to 0.
    Exception
        An exception is raised if a Hz value in 'notchVals' is greater than
        samplingRate/2 or less than 0
    Exception
        An exception is raised if a file cannot not be read in 'inPath'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'fileExt'.
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
    
    # Convert outPath to absolute
    if not os.path.isabs(outPath):
        outPath = os.path.abspath(outPath)
    
    # Get dictionary of file locations
    if expCopy:
        filedirs = map_files(inPath, fileExt=fileExt)
    else:
        filedirs = map_files(inPath, fileExt=fileExt, expression=expression)
        if len(filedirs) == 0:
            warnings.warn("Warning: The regular expression " + str(expression) + " did not match with any files.")
        
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(fileExt):] == fileExt) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = read_file_type(filedirs[file], fileExt)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
            
            # Apply filter to columns
            for col in cols:
                data = apply_notch_filters(data, col, samplingRate, notch)
            
            # Construct out path
            out_file = outPath + filedirs[file][len(inPath):]
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
        elif (file[-len(fileExt):] == fileExt) and expCopy:
            # Copy the file even if it doesn't match if expCopy is true
            data = read_file_type(filedirs[file], fileExt)
            out_file = outPath + filedirs[file][len(inPath):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    
    return

#
# =============================================================================
#

def apply_bandpass_filter(Signal, col, samplingRate, low, high):
    """
    Apply a bandpass filter to a Signal for a given lower and upper limit.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of the Signal to apply the filter to.
    samplingRate : float
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
        raise Exception("Column " + str(col) + " not in Signal.")
    
    if samplingRate <= 0:
        raise Exception("Sampling rate must be greater or equal to 0.")
    
    if high > samplingRate/2 or low > samplingRate/2:
        raise Exception("'high' and 'low' cannot be greater than 1/2 the sampling rate.")
    
    if high <= low:
        raise Exception("'high' must be higher than 'low'.")
    
    
    Signal = Signal.copy()
    # Here, the "5" is the order of the butterworth filter
    # (how quickly the signal is cut off)
    b, a = scipy.signal.butter(5, [low, high], fs=samplingRate, btype='band')
    Signal[col] = scipy.signal.lfilter(b, a, Signal[col])
    return Signal

#
# =============================================================================
#

def bandpass_filter_signals(inPath, outPath, samplingRate, low=20, high=450, cols=None, expression=None, expCopy=False, fileExt='csv'):
    """
    Apply bandpass filters to all Signals in a folder. Writes filtered Signals
    to an output folder, and generates a file structure
    matching the input folder.
    
    Parameters
    ----------
    inPath : dict
        Filepath to a directory to read Signal files.
    outPath : str
        Filepath to an output directory.
    samplingRate : float
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
    expCopy : bool, optional
        If true, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    fileExt : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    
    Raises
    ------
    Warning
        A warning is raised if no files in 'inPath' match with 'expression'.
    Exception
        An exception is raised if the column is not found in any of the Signal
        files found.
    Exception
        An exception is raised if the sampling rate is less or equal to 0.
    Exception
        An exception is raised if high is not higher than low.
    Exception
        An exception is raised if a file cannot not be read in inPath.
    Exception
        An exception is raised if an unsupported file format was provided for
        fileExt.
    Exception
        An exception is raised if expression is not None or a valid regular
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
    
    # Convert outPath to absolute
    if not os.path.isabs(outPath):
        outPath = os.path.abspath(outPath)
    
    # Get dictionary of file locations
    if expCopy:
        filedirs = map_files(inPath, fileExt=fileExt)
    else:
        filedirs = map_files(inPath, fileExt=fileExt, expression=expression)
        if len(filedirs) == 0:
            warnings.warn("Warning: The regular expression " + str(expression) + " did not match with any files.")
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(fileExt):] == fileExt) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = read_file_type(filedirs[file], fileExt)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
              
            # Apply filter to columns
            for col in cols:
                data = apply_bandpass_filter(data, col, samplingRate, low, high)
            
            # Construct out path
            out_file = outPath + filedirs[file][len(inPath):]
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
        elif (file[-len(fileExt):] == fileExt) and expCopy:
            # Copy the file even if it doesn't match if expCopy is true
            data = read_file_type(filedirs[file], fileExt)
            out_file = outPath + filedirs[file][len(inPath):]
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
        raise Exception("Column " + str(col) + " not in Signal")
    
    Signal = Signal.copy()
    Signal[col] = np.abs(Signal[col])
    return Signal

#
# =============================================================================
#

def apply_boxcar_smooth(Signal, col, windowSize):
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
    windowSize : int, float
        Size of the window of the filter.
    
    Raises
    ------
    Warning
        A warning is raised if windowSize is greater than Signal length.
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if windowSize is less or equal to 0.
    
    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the boxcar smoothing filter is applied.

    """
    
    if windowSize > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    if windowSize <= 0:
        raise Exception("windowSize cannot be 0 or negative")
        
    
    Signal = Signal.copy()
    
    Signal = apply_fwr(Signal, col)
    # Construct kernel
    window = np.ones(windowSize) / float(windowSize)
    # Convolve
    Signal[col] = np.convolve(Signal[col], window, 'same')
    return Signal

#
# =============================================================================
#

def apply_rms_smooth(Signal, col, windowSize):
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
    windowSize : int, float
        Size of the window of the filter.

    Raises
    ------
    Warning
        A warning is raised if windowSize is greater than Signal length.
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if windowSize is less or equal to 0.

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the RMS smoothing filter is applied.

    """
    
    if windowSize > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    if windowSize <= 0:
        raise Exception("windowSize cannot be 0 or negative")
    
    
    
    Signal = Signal.copy()
    # Square
    Signal[col] = np.power(Signal[col], 2)
    # Construct kernel
    window = np.ones(windowSize) / float(windowSize)
    # Convolve and square root
    Signal[col] = np.sqrt(np.convolve(Signal[col], window, 'same'))
    return Signal

#
# =============================================================================
#

def apply_gaussian_smooth(Signal, col, windowSize, sigma=1):
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
    windowSize : int, float
        Size of the window of the filter.
    sigma : float, optional
        Parameter of sigma in the Gaussian smoothing. The default is 1.

    Raises
    ------
    Warning
        A warning is raised if windowSize is greater than Signal length.
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if windowSize is less or equal to 0.

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the Gaussian smoothing filter is applied.

    """
    
    # Helper function for creating a Gaussian kernel
    def get_gauss(n, sigma):
        r = range(-int(n/2), int(n/2)+1)
        return [1 / (sigma * np.sqrt(2*np.pi)) * np.exp(-float(x)**2/(2*sigma**2)) for x in r]
    
    if windowSize > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + (col) + " not in Signal")
    
    if windowSize <= 0:
        raise Exception("windowSize cannot be 0 or negative")
    
    Signal = Signal.copy()
    
    Signal = apply_fwr(Signal, col)
    # Construct kernel
    window = get_gauss(windowSize, sigma)
    # Convolve
    Signal[col] = np.convolve(Signal[col], window, 'same')
    return Signal

#
# =============================================================================
#

def apply_loess_smooth(Signal, col, windowSize):
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
    windowSize : int, float
        Size of the window of the filter.

    Raises
    ------
    Warning
        A warning is raised if windowSize is greater than Signal length.
    Exception
        An exception is raised if col is not found in Signal.
    Exception
        An exception is raised if windowSize is less or equal to 0.

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the Loess smoothing filter is applied.

    """
    
    if windowSize > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    if windowSize <= 0:
        raise Exception("windowSize cannot be 0 or negative")
    
    Signal = Signal.copy()
    
    Signal = apply_fwr(Signal, col)
    # Construct kernel
    window = np.linspace(-1,1,windowSize+1,endpoint=False)[1:]
    window = np.array(list(map(lambda x: (1 - np.abs(x) ** 3) ** 3, window)))
    window = window / np.sum(window)
    # Convolve
    Signal[col] = np.convolve(Signal[col], window, 'same')
    return Signal

#
# =============================================================================
#

def smooth_filter_signals(inPath, outPath, windowSize, cols=None, expression=None, expCopy=False, fileExt='csv', method='rms', sigma=1):  
    """
    Apply smoothing filters to all Signals in a folder. Writes filtered Signals
    to an output folder, and generates a file structure matching the input
    folder. The method used to smooth the signals can be specified, but is RMS
    as default.

    Parameters
    ----------
    inPath : dict
        Filepath to a directory to read Signal files.
    outPath : str
        Filepath to an output directory.
    windowSize : int, float
        Size of the window of the filter.
    cols : list, optional
        List of columns of the Signal to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names
        match the regular expression. The default is None.
    expCopy : bool, optional
        If true, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    fileExt : str, optional
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
        A warning is raised if windowSize is greater than Signal length.
    Exception
        An exception is raised if an invalid smoothing method is used. Valid
        methods are one of: 'rms', 'boxcar', 'gauss' or 'loess'.
    Exception
        An exception is raised if col is not found in any of the Signal files.
    Exception
        An exception is raised if windowSize is less or equal to 0.
    Exception
        An exception is raised if a file cannot not be read in inPath.
    Exception
        An exception is raised if an unsupported file format was provided for
        fileExt.
    Exception
        An exception is raised if expression is not None or a valid regular
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
    
    # Convert outPath to absolute
    if not os.path.isabs(outPath):
        outPath = os.path.abspath(outPath)
    
    # Get dictionary of file locations
    if expCopy:
        filedirs = map_files(inPath, fileExt=fileExt)
    else:
        filedirs = map_files(inPath, fileExt=fileExt, expression=expression)
        if len(filedirs) == 0:
            warnings.warn("Warning: The regular expression " + str(expression) + " did not match with any files.")
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(fileExt):] == fileExt) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = read_file_type(filedirs[file], fileExt)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                if 'Time' in cols:
                    cols.remove('Time')
              
            # Apply filter to columns
            for col in cols:
                if method == 'rms':
                    data = apply_rms_smooth(data, col, windowSize)
                elif method == 'boxcar':
                    data = apply_boxcar_smooth(data, col, windowSize)
                elif method == 'gauss':
                    data = apply_gaussian_smooth(data, col, windowSize, sigma)
                elif method == 'loess':
                    data = apply_loess_smooth(data, col, windowSize)
                else:
                    raise Exception('Invalid smoothing method used: ', str(method), ', use "rms", "boxcar", "gauss" or "loess"')
                
            # Construct out path
            out_file = outPath + filedirs[file][len(inPath):]
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
        
        elif (file[-len(fileExt):] == fileExt) and expCopy:
            # Copy the file even if it doesn't match if expCopy is true
            data = read_file_type(filedirs[file], fileExt)
            out_file = outPath + filedirs[file][len(inPath):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    return

#
# =============================================================================
#

def clean_signals(path_names, samplingRate=2000):
    """
    Automates the EMG preprocessing workflow, performing notch filtering,
    bandpass filtering and smoothing.

    Parameters
    ----------
    path_names : dict
        Dictionary containing path locations for writing and reading Signal
        data between paths.
    samplingRate : float
        Sampling rate of the Signal.

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
    windowSize = 50
    
    # Automatically runs through workflow
    notch_filter_signals(path_names['Raw'], path_names['Notch'], samplingRate, notch)
    bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], samplingRate)
    smooth_filter_signals(path_names['Bandpass'], path_names['Smooth'], windowSize)
    return