import scipy
import pandas as pd
import numpy as np
import os
import re
import cv2
from tqdm import tqdm
import warnings

#
# =============================================================================
#

"""
A collection of functions for filtering Signals.
"""

#
# =============================================================================
#

def EMG2PSD(Sig_vals, sr=1000, normalize=True):
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
        If True, will normalize the result. If False, will not. The default is True.

        Raises
    ------
    Exception
        An exception is raised if the sampling rate is less or equal to 0

    Returns
    -------
    psd : DataFrame
        A DataFrame containing a 'Frequency' and 'Power' column. The Power column
        indicates the intensity of each frequency in the Signal provided. Results
        will be normalized if 'normalize' is set to True.
    """
    
    if sr <= 0:
        raise Exception("Sampling rate must be greater or equal to 0")
    
    # Initial parameters
    Sig_vals = Sig_vals - np.mean(Sig_vals)
    N = len(Sig_vals)
    
    # Calculate minimum frequency given sampling rate
    min_frequency = (2 * sr) / (N / 2)
    
    # Calculate window size givern sampling rate
    nperseg = int((2 / min_frequency) * sr)
    nfft = nperseg * 2
    
    # Apply welch method with hanning window
    frequency, power = scipy.signal.welch(
        Sig_vals,
        fs=sr,
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

def ReadFileType(path, file_ext):
    """
    Safe wrapper for reading files of a given extension.

    Parameters
    ----------
    path : str
        Path of file to read.
    file_ext : str
        File extension to read.

    Raises
    ------
    Exception
        Raises an exception if the file could not be read.
    Exception
        Raises an exception if an unsupported file format was provided for
        file_ext.

    Returns
    -------
    file : pd.DataFrame
        Returns a Pandas data frame of the file contents.

    """
    
    if file_ext == 'csv':
        try:
            file = pd.read_csv(path)
        except:
            raise Exception("CSV file could not be read: " + path)
    else:
        raise Exception("Unsupported file format provided: " + file_ext)
        
    return file

#
# =============================================================================
#

def MapFiles(in_path, file_ext='csv', expression=None):
    """
    Generate a dictionary of file names and locations from the subfiles of a folder.
    
    Parameters
    ----------
    in_path : str
        The filepath to a directory to read Signal files.
    file_ext : str, optional
        File extension for files to read. The default is 'csv'.
    expression : str, optional
        A regular expression. If provided, will only count files whose names match the regular expression. The default is None.

    Returns
    -------
    filedirs : dict
        A dictionary of file name keys and file path location values.

    """
    
    filedirs = {}
    for file in os.listdir(in_path):
        if os.path.exists(in_path + file + '\\'):
            subDir = MapFiles(in_path + file + '\\')
            filedirs.update(subDir)
        elif (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            filedirs[file] = in_path + file
    return filedirs

#
# =============================================================================
#

def ConvertMapFiles(fileObj, file_ext='csv', expression=None):
    """
    Generate a dictionary of file names and locations from different forms of
    input.

    Parameters
    ----------
    fileObj : str
        The file location object. This can be a string to a file location, or
        an already formed dictionary of file locations.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    expression : str, optional
        A regular expression. If provided, will only count files whose names
        match the regular expression. The default is None.

    Raises
    ------
    Exception
        An exception is raised if an unsupported file location format is
        provided.

    Returns
    -------
    filedirs : dict
        A dictionary of file name keys and file path location values.
    
    """
    
    # User provided a path to a folder
    if type(fileObj) is str:
        if not os.path.isabs(fileObj):
            fileObj = os.path.abspath(fileObj) + '\\'
        filedirs = MapFiles(in_path=fileObj, file_ext=file_ext, expression=expression)
    # User provided a processed file directory
    elif type(fileObj) is dict:
        # If expression is provided, filters the dictionary
        # for all entries matching it
        fd = fileObj.copy()
        if expression != None:
            for file in fd:
                if not (re.match(expression, fd[file])):
                    del fd[file]
        filedirs = fd
    # Provided file location format is unsupported
    else:
        raise Exception("Unsupported file location format:", type(fileObj))
    
    return filedirs

#
# =============================================================================
#


def MapFilesFuse(filedirs, names):
    """
    Generate a dictionary of file names and locations from different forms of
    input. Each directory should contain the same file at different stages with
    the same name, and will create a dataframe of the location of this file in
    each of the directories provided.

    Parameters
    ----------
    filedirs : dict list
        List of file location directories
    names : str
        List of names to use for file directory columns. Same order as file
        directories.

    Raises
    ------
    Exception
        An exception is raised if a file contained in the first file directory
        is not found in the other file directories.

    Returns
    -------
    filedirs : pd.DataFrame
        A DataFrame of file names, and their locations in each file directory.
    
    """
    
    data = []
    # Assumes all files listed in first file directory
    # exists in the others
    for file in filedirs[0].keys():
        # Create row
        row = [file, file]
        for i, filedir in enumerate(filedirs):
            if file not in filedir:
                # Raise exception if file does not exist
                raise Exception('File ' + file + ' does not exist in file directory ' + names[i])
            row.append(filedir[file])
        # Add row to data frame
        data.append(row)
    # Create data frame
    df = pd.DataFrame(data, columns=['ID', 'File'] + names)
    df.set_index('ID',inplace=True)
    
    return df

#
# =============================================================================
#

def ApplyNotchFilters(Signal, col, sampling_rate, notch_vals):
    """
    Apply a list of notch filters for given frequencies and Q-factors to a column of the provided data.

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
            A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
        col : str
            Column of the Signal to apply the filter to.
        sampling_rate : float
            Sampling rate of the Signal.
        notch : (int, int) tuple
            Notch filter data. Should be a (Hz, Q) tuple where Hz is the frequency to apply the filter to, and Q.
            is the Q-score (an intensity score where a higher number means a less extreme filter).

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
    Apply notch filters to all Signals in a folder. Writes filtered Signals to an output folder, and generates a file structure
    matching the input folder.

    Parameters
    ----------
    in_path : dict
        Filepath to a directory to read Signal files.
    out_path : str
        Filepath to an output directory.
    sampling_rate : float
        Sampling rate of the Signal.
    notch : list
        A list of (Hz, Q) tuples corresponding to the notch filters being applied. Hz is the frequency to
        apply the filter to, and Q is the Q-score (an intensity score where a higher number means a less extreme filter).
    cols : list, optional
        List of columns of the Signal to apply the filter to. The default is None, in which case the filter is applied to
        every column except for 'Time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names match the regular expression. The default is None.
    exp_copy : TYPE, optional
        If true, copies files that don't match the regular expression to the output folder without filtering. The default is False,
        which ignores files that don't match.
    file_ext : TYPE, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.

    Raises
    ------
    Exception
        An exception is raised if the column is not found in any of the Signal files found.
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

    Returns
    -------
    None.

    """
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path) + '\\'
    
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
    Apply bandpass filters to all Signals in a folder. Writes filtered Signals to an output folder, and generates a file structure
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
        List of columns of the Signal to apply the filter to. The default is None, in which case the filter is applied to
        every column except for 'Time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names match the regular expression. The default is None.
    exp_copy : bool, optional
        If true, copies files that don't match the regular expression to the output folder without filtering. The default is False,
        which ignores files that don't match.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.
    
    Raises
    ------
    Exception
        An exception is raised if the column is not found in any of the Signal files found.
    Exception
        An exception is raised if the sampling rate is less or equal to 0.
    Exception
        An exception is raised if high is not higher than low.
    Exception
        Raises an exception if a file cannot not be read in in_path.
    Exception
        Raises an exception if an unsupported file format was provided for
        file_ext.
    
    Returns
    -------
    None.

    """
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path) + '\\'
    
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
    Apply a boxcar smoothing filter to a Signal. Uses a rolling average with a window size.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
    Apply an RMS smoothing filter to a Signal. Uses a rolling average with a window size.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
    Apply a Gaussian smoothing filter to a Signal. Uses a rolling average with a window size.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
    
    if window_size > len(Signal.index):
        warnings.warn("Warning: Selected window size is greater than Signal file.")
    
    if col not in list(Signal.columns.values):
        raise Exception("Column " + col + " not in Signal")
    
    if window_size <= 0:
        raise Exception("window_size cannot be 0 or negative")
    
    Signal = Signal.copy()
    
    Signal = ApplyFWR(Signal, col)
    # Construct kernel
    window = cv2.getGaussianKernel(window_size, sigma).transpose()[0]
    # Convolve
    Signal[col] = np.convolve(Signal[col], window, 'same')
    return Signal

#
# =============================================================================
#

def ApplyLoessSmooth(Signal, col, window_size):
    """
    Apply a Loess smoothing filter to a Signal. Uses a rolling average with a window size and tri-cubic weight.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
    Apply smoothing filters to all Signals in a folder. Writes filtered Signals to an output folder, and generates a file structure
    matching the input folder. The method used to smooth the signals can be specified, but is RMS as default.

    Parameters
    ----------
    in_path : dict
        Filepath to a directory to read Signal files.
    out_path : str
        Filepath to an output directory.
    window_size : int, float
        Size of the window of the filter.
    cols : list, optional
        List of columns of the Signal to apply the filter to. The default is None, in which case the filter is applied to
        every column except for 'time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names match the regular expression. The default is None.
    exp_copy : bool, optional
        If true, copies files that don't match the regular expression to the output folder without filtering. The default is False,
        which ignores files that don't match.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.
    method : str, optional
        The smoothing method to use. Can be one of 'rms', 'boxcar', 'gauss' or 'loess'. The default is 'rms'.
    sigma: float, optional
        The value of sigma used for a Gaussian filter. Only affects output when using Gaussian filtering.

    Raises
    ------
    Exception
        An exception is raised if an invalid smoothing method is used. Valid methods are one of: 'rms', 'boxcar', 'gauss' or 'loess'.
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

    Returns
    -------
    None.

    """
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path) + '\\'
    
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
                elif method == 'guass':
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

def CalcIEMG(Signal, col, sr):
    """
    Calculate the Integreated EMG (IEMG) of a Signal.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
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
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
    diff : float, DataFrame
        The divisor of the calculation. If a percentage is provided, it will calculate the
        spectral flux of the percentage of the Signal with one minus the percentage of the Signal.
    col : str
        Column of the Signal to apply the summary to. If a second signal is provided for diff, a column
        of the same name should be available for use.
    sr : float
        Sampling rate of the Signal.
    diff_sr : float, optional
        Sampling rate for the second Signal if provided. The default is None, in which case if
        a second Signal is provided, the sampling rate is assumed to be the same as the first.

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

def CalcTwitchRatio(psd, freq=60):
    """
    Calculate the Twitch Ratio of a PSD.

    Parameters
    ----------
    psd : DataFrame
        A Pandas DataFrame containing a 'Frequency' and 'Power' column.
    freq : float, optional
        Frequency threshold of the Twitch Ratio separating fast-twitching (high-frequency)
        muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if freq is less or equal to 0.
    Exception
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'

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
        Frequency threshold of the Twitch Index separating fast-twitching (high-frequency)
        muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if freq is less or equal to 0.
    Exception
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'

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
        Frequency threshold of the Twitch Slope separating fast-twitching (high-frequency)
        muscles from slow-twitching (low-frequency) muscles.

    Raises
    ------
    Exception
        An exception is raised if freq is less or equal to 0.
    Exception
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'

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
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'

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
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'

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
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'

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
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'

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
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'

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
        The percentage of power to look for the Spectral Rolloff after. The default is 0.85.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'
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
        Order of the SBW. The default is 2, which gives the standard deviation around the centroid.

    Raises
    ------
    Exception
        An exception is raised if psd does not only have columns 'Frequency' and 'Power'
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

def ExtractFeatures(in_bandpass, in_smooth, out_path, sampling_rate, cols=None, expression=None, file_ext='csv', short_name=True):
    """
    Analyze Signals by performing a collection of analyses on them and saving a
    feature file.

    Parameters
    ----------
    in_bandpass : str
        File location for reading in bandpass files. These files are used for
        generating spectral features, as smoothed files can impact the
        accuracy. If no bandpass files are available, the same file location
        can be used as for in_smooth.
    in_smooth : str
        File location for reading in smoothed files.
    out_path : str
        Output location for feature file.
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

    Returns
    -------
    None.

    """
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path) + '\\'
    
    
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
            
    SignalDF.to_csv(out_path + 'Features.csv', index=False)
    return SignalDF