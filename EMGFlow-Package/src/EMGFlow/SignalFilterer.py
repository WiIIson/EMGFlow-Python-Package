import scipy
import pandas as pd
import numpy as np
import neurokit2 as nk
import os
import re
import cv2
from tqdm import tqdm

#
# =============================================================================
#

"""
A collection of functions for filtering Signals.
"""

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
    Generate a dictionary of file names and locations from different forms of input.

    Parameters
    ----------
    fileObj : str
        The file location object. This can be a string to a file location, or an already formed dictionary of file locations.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.
    expression : str, optional
        A regular expression. If provided, will only count files whose names match the regular expression. The default is None.

    Raises
    ------
    Exception
        If an unsupported file location format is provided, an exception is raised.

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
        filedirs = fileObj
    # Provided file location format is unsupported
    else:
        raise Exception("Unsupported file location format:", type(fileObj))
    
    return filedirs

#
# =============================================================================
#

def ApplyNotchFilters(Signal, col, sampling_rate, notch_vals):
    """
    Apply a list of notch filters for given frequencies and Q-factors to a column of the provided data.

    Parameters
    ----------
    Signal : DataFrame
        A Pandas DataFrame containing a 'Time' column, and additional columns for signal data.
    col : str
        Column of the Signal to apply the filter to.
    sampling_rate : float
        Sampling rate of the Signal.
    notch_vals : list
        A list of (Hz, Q) tuples corresponding to the notch filters being applied. Hz is the frequency to
        apply the filter to, and Q is the Q-score (an intensity score where a higher number means a less extreme filter).

    Returns
    -------
    DataFrame
        A copy of Signal after the notch filters are applied.

    """

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

        Returns
        -------
        Signal_col : Series
            A Pandas Series of the provided column with the notch filter applied

        """
        
        Signal = Signal.copy()
        
        (Hz, Q) = notch
        
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
        every column except for 'time'.
    expression : str, optional
        A regular expression. If provided, will only filter files whose names match the regular expression. The default is None.
    exp_copy : TYPE, optional
        If true, copies files that don't match the regular expression to the output folder without filtering. The default is False,
        which ignores files that don't match.
    file_ext : TYPE, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.

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
        
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            # Read file
            data = pd.read_csv(filedirs[file])
            
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
            data = pd.read_csv(filedirs[file])
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

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the bandpass filter is applied.

    """
    
    Signal = Signal.copy()
    # Here, the "5" is the order of the butterworth filter
    # (how quickly the signal is cut off)
    b, a = scipy.signal.butter(5, [low, high], fs=sampling_rate, btype='band')
    Signal[col] = scipy.signal.lfilter(b, a, Signal[col])
    return Signal

#
# =============================================================================
#

def BandpassFilterSignals(in_path, out_path, sampling_rate, low, high, cols=None, expression=None, exp_copy=False, file_ext='csv'):
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
        Lower frequency limit of the bandpass filter.
    high : float
        Upper frequency limit of the bandpass filter.
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
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = pd.read_csv(filedirs[file])
            
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
            data = pd.read_csv(filedirs[file])
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

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the full wave rectifier filter is applied.

    """
    
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
    
    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the boxcar smoothing filter is applied.

    """
    
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

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the RMS smoothing filter is applied.

    """
    
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

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the Gaussian smoothing filter is applied.

    """
    
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

    Returns
    -------
    Signal : DataFrame
        A copy of Signal after the Loess smoothing filter is applied.

    """
    
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

def SmoothFilterSignals(in_path, out_path, sampling_rate, window_size, cols=None, expression=None, exp_copy=False, file_ext='csv', method='rms'):  
    """
    Apply smoothing filters to all Signals in a folder. Writes filtered Signals to an output folder, and generates a file structure
    matching the input folder. The method used to smooth the signals can be specified, but is RMS as default.

    Parameters
    ----------
    in_path : dict
        Filepath to a directory to read Signal files.
    out_path : str
        Filepath to an output directory.
    sampling_rate : float
        Sampling rate of the Signal.
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

    Raises
    ------
    Exception
        An exception is raised if an invalid smoothing method is used. Valid methods are one of: 'rms', 'boxcar', 'gauss' or 'loess'.

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
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = pd.read_csv(filedirs[file])
            
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
                    data = ApplyGaussianSmooth(data, col, window_size)
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
            data = pd.read_csv(filedirs[file])
            out_file = out_path + filedirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    return

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

    Returns
    -------
    flux : float
        Spectral flux of the Signal.

    """
    
    # Separate Signal1 by div and find spectral flux
    if isinstance(diff, float):
        # Find column divider index
        diff_ind = int(len(Signal1[col]) * diff)
        # Take the PSD of each signal
        psd1 = nk.signal_psd(Signal1[col][:diff_ind], sampling_rate=sr)
        psd2 = nk.signal_psd(Signal1[col][diff_ind:], sampling_rate=sr)
        # Calculate the spectral flux
        flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
        
    # Find spectral flux of Signal1 by div
    elif isinstance(diff, pd.DataFrame):
        
        # If no second sampling rate, assume same sampling rate as first Signal
        if diff_sr == None: diff_sr = sr
        # Take the PSD of each signal
        psd1 = nk.signal_psd(Signal1[col], sampling_rate=sr)
        psd2 = nk.signal_psd(diff[col], sampling_rate=diff_sr)
        # Calculate the spectral flux
        flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
    
    return flux

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

    Returns
    -------
    IEMG : float
        IEMG of the Signal.

    """
    
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

    Returns
    -------
    MAV : float
        MAV of the Signal.

    """
    
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

    Returns
    -------
    MMAV : float
        MMAV of the Signal.

    """
    
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

    Returns
    -------
    SSI : float
        SSI of the Signal.

    """
    
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

    Returns
    -------
    VAR : float
        VAR of the Signal.

    """
    
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

    Returns
    -------
    vOrder : float
        V-Order of the Signal.

    """
    
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

    Returns
    -------
    RMS : float
        RMS of the Signal.

    """
    
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

    Returns
    -------
    WL : float
        WL of the Signal.

    """
    
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

    Returns
    -------
    WAMP : int
        WAMP of the Signal.

    """
    
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

    Returns
    -------
    LOG : float
        LOG of the Signal.
    
    """
    
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

    Returns
    -------
    MFL : float
        MFL of the Signal.

    """
    
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

    Returns
    -------
    AP : float
        AP of the Signal.

    """
    
    AP = np.sum(Signal[col] ** 2) / len(Signal[col])
    return AP

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

    Returns
    -------
    twitch_ratio : float
        Twitch Ratio of the PSD.

    """
    
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

    Returns
    -------
    twitch_index : float
        Twitch Index of the PSD.

    """
    
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

    Returns
    -------
    fast_slope : float
        Twitch Slope of the fast-twitching muscles.
    slow_slope : float
        Twitch Slope of the slow-twitching muscles.

    """
    
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

    Returns
    -------
    SC : float
        SC of the PSD.

    """
    
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

    Returns
    -------
    SF : float
        SF of the PSD.

    """
    
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

    Returns
    -------
    SS : float
        SS of the PSD.

    """
    
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

    Returns
    -------
    SDec : float
        SDec of the PSD.

    """
    
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

    Returns
    -------
    SEntropy : float
        Spectral Entropy of the PSD.

    """
    
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

    Returns
    -------
    float
        Spectral Rolloff of the PSD.

    """
    
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

    Returns
    -------
    SBW : float
        The SBW of the PSD.

    """
    
    cent = CalcSC(psd)
    SBW = (np.sum(psd['Power'] * (psd['Frequency'] - cent) ** p)) ** (1/p)
    return SBW

#
# =============================================================================
#

def AnalyzeSignals(in_bandpass, in_smooth, out_path, sampling_rate, cols=None, expression=None, file_ext='csv', short_name=True):
    """
    Analyze Signals by performing a collection of analyses on them and saving a feature file.

    Parameters
    ----------
    in_bandpass : str
        File location for reading in bandpass files. These files are used for generating spectral features, as smoothed files can
        impact the accuracy. If no bandpass files are available, the same file location can be used as for in_smooth.
    in_smooth : str
        File location for reading in smoothed files.
    out_path : str
        Output location for feature file.
    sampling_rate : float
        Sampling rate for all Signals read (all files in in_bandpass and in_smooth).
    cols : [str] list, optional
        List of columns to analyze in each Signal (all files in in_bandpass and in_smooth). The default is None, in which case
        all columns except for "Time" will be analyzed. All Signals should have the columns listed, or if None is used, all
        Signals should have the same columns.
    expression : str, optional
        A regular expression. If provided, will only count files whose names match the regular expression. The default is None.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.
    short_name : bool, optional
        If true, makes the key column of the feature files the name of the file. If false, uses the file path to ensure unique
        keys. The default is True.

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
    
    # List of measure names
    measure_names = [
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
        data1 = pd.read_csv(path1)
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
            data_b = pd.read_csv(filedirs_b[file])
            data_s = pd.read_csv(filedirs_s[file])
                    
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
                psd = nk.signal_psd(data_b[col], sampling_rate=sampling_rate)
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
    return
#
# =============================================================================
#    

if __name__ == '__main__':
    
    # The folders listed in in_data and out_data must exist before
    # running the script, and should not have any subdirectories.
    # The output will be generated in the
    # out_data (output) folder listed, with the same file format
    # contained in the in_data (input) folder
    
    test_file = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/01_Raw/Raw_PID_01-10/01/01-01-01.csv'
    
    raw_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/01_Raw/'
    notch_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/02_Notch/'
    notch_s_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/02_Notch_Special/'
    bandpass_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/03_Bandpass/'
    smooth_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/04_Smooth/'
    feature_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/05_Feature/'
    
    sampling_rate = 2000            # Sampling rate
    notch_vals = [(50,5), (150,25), (250,25), (350,25), (400,25), (450,25), (550,25), (650,25), (750,25), (850,25), (950,25)]
    notch_sc = [(317, 25)]
    reg = "^(08|11)"
    
    cols = ['EMG_zyg', 'EMG_cor']
    
    # Old PADS pipeline
    #MergePerceptual(perceptual_path, feature_path)
    #PADS_RMSFilterSignals(bandpass_path, smooth_path, sampling_rate, 50)
    #PADS_AnalyzeSignals(bandpass_path, smooth_path, perceptual_file, feature_path, sampling_rate)
    
    # PADS pipeline
    #NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols, exp_copy=True)
    #NotchFilterSignals(notch_path, notch_s_path, sampling_rate, notch_sc, cols, expression=reg, exp_copy=True)
    #BandpassFilterSignals(notch_s_path, bandpass_path, sampling_rate, 20, 450, cols, exp_copy=True)
    #SmoothFilterSignals(bandpass_path, smooth_path, sampling_rate, 50, exp_copy=True)
    #AnalyzeSignals(bandpass_path, smooth_path, feature_path, sampling_rate, cols=cols)
    
    