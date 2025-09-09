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
A collection of functions for preprocessing signals and EMG data.
"""

#
# =============================================================================
#

def emg_to_psd(Signal:pd.DataFrame, col:str, sampling_rate:float=1000.0, max_segment:float=2.5, normalize:bool=True, nan_mask=None):
    """
    Creates a Power Spectrum Density (PSD) dataframe from a signal, showing the
    intensity of each frequency detected in the signal. Uses the Welch method,
    meaning it can be used as a Long Term Average Spectrum (LTAS).
    
    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the PSD is calculated from.
    sampling_rate : float, optional
        The sampling rate of 'Signal'. The default is 1000.0.
    max_segment : float, optional
        The maximum length (in ms) of NaN values to fill. If a length of
        invalid data is longer than this threshold, it will not be
        interpolated. The default is 2.5.
    normalize : bool, optional
        If True, will normalize the result. If False, will not. The default is
        True.
    nan_mask : pd.Series, optional
        Optional series that controls the calculation of the function. Can be
        a True/False mask that is the same size as the selected column, and
        will set all associated False values in the column to NaN in the
        calculation. The default is None, in which case no NaN masking will be
        done.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'nan_mask' is not the same length as 'col'.
    Exception
        An exception is raised if there are too many NaN values to make a valid
        window.

    Returns
    -------
    psd : pd.DataFrame
        A Pandas dataframe containing a 'Frequency' and 'Power' column. The
        'Power' column indicates the intensity of each frequency in 'Signal'.
        Results will be normalized if 'normalize' is set to True.
    
    """
    
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    PSD_Signal = Signal.copy().reset_index(drop=True)
    
    # Use 'nan_mask' to set additional values to NaN
    if nan_mask is not None:
        # Clean 'nan_mask'
        nan_mask = np.asarray(nan_mask, dtype=bool).ravel()
        
        # Raise exception if length mismatch
        if len(nan_mask) != len(PSD_Signal):
            raise Exception('NaN mask must be the same length as the Signal dataframe.')
        
        # Set values to NaN
        PSD_Signal.loc[~nan_mask, col] = np.nan
    
    # Apply interpolation
    PSD_Signal = apply_fill_missing(PSD_Signal, col, sampling_rate, max_segment=max_segment)
    
    # Define Welch parameters
    N = len(PSD_Signal[col].values)
    min_frequency = (2.0 * sampling_rate) / (N / 2.0)
    max_frequency = sampling_rate / 2.0
    nperseg = int((2.0 / min_frequency) * sampling_rate)
    if nperseg >= N/2.0:
        nperseg = int(N/2.0)
    nfft = int(nperseg * 2.0) # 50% overlap
    step = int(nperseg // 2)
    
    PSDs = []
    freqs = None
    
    nan_found = False
    
    for start in range(0, N - nperseg + 1, step):
        end = start + nperseg
        
        # Skip window if NaN detected
        if PSD_Signal.loc[start:end, col].isna().any():
            nan_found = True
            continue
        
        segment = PSD_Signal.loc[start:end, col].values
        
        frequency, power = scipy.signal.welch(
                segment,
                fs=sampling_rate,
                scaling='density',
                detrend=False,
                nfft=nfft,
                average='mean',
                nperseg=nperseg,
                window='hann'
            )
        
        if freqs is None:
            freqs = frequency
        PSDs.append(power)
        
    if not PSDs:
        raise Exception('All windows contained NaN data.')
    
    if nan_found:
        warnings.warn("NaN values detected in 'Signal'.")
    
    total_power = np.mean(PSDs, axis=0)
    
    # Final cleaning for psd
    psd = pd.DataFrame({'Frequency':freqs, 'Power':total_power})
    psd = psd.loc[np.logical_and(psd['Frequency'] >= min_frequency, psd['Frequency'] <= max_frequency)].reset_index(drop=True)
    
    # Normalize the psd
    if normalize and psd['Power'].max() > 0:
        psd['Power'] /= psd['Power'].max()
    
    return psd
    

#
# =============================================================================
#
#
# NOTCH
#
#
# =============================================================================
#

def apply_notch_filters(Signal:pd.DataFrame, col:str, sampling_rate:float, notch_vals=[(50,5)], min_segment:float=30.0):
    """
    Apply a list of notch filters ('notch_vals') to a column of 'Signal'.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the notch filter is applied to.
    sampling_rate : float
        The sampling rate of 'Signal'.
    notch_vals : list-tuple, optional
        A list of (Hz, Q) tuples corresponding to the notch filters being
        applied. Hz is the frequency the filter is applied to, and Q is the
        Q-score (an intensity score where a higher number means a less extreme
        filter). The default is [(50, 5)].
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.
        
    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than the recording of
        'Signal'.
    Exception
        An exception is raised if a Hz value in 'notch_vals' is greater than
        'sampling_rate'/2 or less than 0.

    Returns
    -------
    notch_Signal : pd.DataFrame
        A copy of 'Signal' after the notch filters are applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', and a
    # warning is raised if it contains NaNs.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if Signal[col].isnull().values.any():
        warnings.warn("NaN values detected in 'Signal'.")
    
    # An exception is raised if 'sampling_rate' is less than or equal to 0.
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    # An exception is raised if the length created by 'min_segment' is greater
    # than the length of 'Signal'.
    min_gap = int(min_segment * sampling_rate / 1000.0)
    if min_gap > len(Signal):
        raise Exception("Minimum length created by 'min_segment' is greater than 'Signal' length.")
    
    notch_Signal = Signal.copy().reset_index(drop=True)
    
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
            min_nan_mask.loc[nan_ind:nan_ind+nan_len-1] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = notch_Signal[min_nan_mask].copy().reset_index(drop=True)
    
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
            masked_data.loc[val_ind:val_ind+val_len-1, col] = np.nan
        else:
            # Apply filters
            for (Hz, Q) in notch_vals:
                
                if Hz > sampling_rate/2 or Hz <= 0:
                    raise Exception("'notch_vals' must be between 0 and" + str(sampling_rate/2) + ".")
                
                norm_Hz = Hz / nyq_freq
                
                # Use scipy notch filter using normalized frequency
                b, a = scipy.signal.iirnotch(norm_Hz, Q)
                filtered_section = scipy.signal.lfilter(b, a, masked_data.loc[val_ind:val_ind+val_len-1, col].copy())
                
                masked_data.loc[val_ind:val_ind+val_len-1, col] = filtered_section
    
    # Put masked_data back in band_Signal
    notch_Signal.loc[min_nan_mask, col] = masked_data[col].values
    
    return notch_Signal

#
# =============================================================================
#

def notch_filter_signals(in_path:str, out_path:str, sampling_rate:float, notch_vals=[(50,5)], cols=None, min_segment:float=30.0, expression:str=None, exp_copy:bool=False, file_ext:str='csv'):
    """
    Apply a list of notch filters ('notch_vals') to all signal files in a
    folder and its subfolders. Writes filtered signal files to an output
    folder, and generates a file structure matching the input folder.

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    out_path : str
        Filepath to a directory to write filtered signals.
    sampling_rate : float
        The sampling rate of the signal files.
    notch_vals : list-tuples, optional
        A list of (Hz, Q) tuples corresponding to the notch filters being
        applied. Hz is the frequency the filter is applied to, and Q is the
        Q-score (an intensity score where a higher number means a less extreme
        filter). The default is [(50, 5)].
    cols : list-str, optional
        List of columns of the signals to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'Time' and columns that start with 'mask_'.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.
    expression : str, optional
        A regular expression. If provided, will only apply the filter to files
        whose local paths inside of 'in_path' match the regular expression. The
        default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        The file extension for files to read. Only filters files with this
        extension. The default is 'csv'.
    
    Raises
    ------
    Warning
        A warning is raised if no files in 'in_path' match with 'expression'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
        
    Warning
        A warning is raised if a column from 'cols' contains NaN values.
    Exception
        An exception is raised if a column from 'cols' is not a column of a
        signal file.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than a signal
        recording.
    Exception
        An exception is raised if a Hz value in 'notch_vals' is greater than
        'sampling_rate'/2 or less than 0.
        
    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
        
    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("The regular expression '" + str(expression) + "' did not compile.")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("The regular expression '" + str(expression) + "' did not match with any files.")
        
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file)!=None)):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
            
            # Apply filter to columns
            for col in cols:
                data = apply_notch_filters(data, col, sampling_rate, notch_vals=notch_vals, min_segment=min_segment)
            
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
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    
    return

#
# =============================================================================
#
#
# BANDPASS
#
#
# =============================================================================
#

def apply_bandpass_filter(Signal:pd.DataFrame, col:str, sampling_rate:float, low:float=20.0, high:float=450.0, min_segment:float=30.0):
    """
    Apply a bandpass filter ('low', 'high') to a column of 'Signal'.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the bandpass filter is applied to.
    sampling_rate : float
        The sampling rate of 'Signal'.
    low : float, optional
        Lower frequency limit (Hz) of the bandpass filter. The default is 20.0.
    high : float
        Upper frequency limit (Hz) of the bandpass filter. The default is
        450.0.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'high' or 'low' are higher than 1/2 of
        'sampling_rate'.
    Exception
        An exception is raised if 'high' is not higher than 'low'.
    Exception
        An exception is raised if 'min_segment' is longer than the recording of
        'Signal'.

    Returns
    -------
    band_Signal : pd.DataFrame
        A copy of 'Signal' after the bandpass filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', and a
    # warning is raised if it contains NaNs.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if Signal[col].isnull().values.any():
        warnings.warn("NaN values detected in 'Signal'.")
    
    # An exception is raised if 'sampling_rate' is less or equal to 0.
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    # An exception is raised if 'high' or 'low' are higher than 1/2 of
    # 'sampling_rate', and if low is greater than or equal to high.
    if high > sampling_rate/2 or low > sampling_rate/2:
        raise Exception("'high' and 'low' cannot be greater than 1/2 the sampling rate.")
    if high <= low:
        raise Exception("'high' must be higher than 'low'.")
        
    # An exception is raised if the length created by 'min_segment' is greater
    # than the length of 'Signal'.
    min_gap = int(min_segment * sampling_rate / 1000.0)
    if min_gap > len(Signal):
        raise Exception("'min_segment' cannot be longer than the recording of 'Signal'.")
    
    band_Signal = Signal.copy().reset_index(drop=True)
    
    # Construct list of NaN locations
    data = band_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data), index=data.index)
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask.loc[nan_ind:nan_ind+nan_len-1] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = band_Signal[min_nan_mask].copy().reset_index(drop=True)
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Apply notch filters to each value sequence set sequences that are too
    # small to NaN
    sos = scipy.signal.butter(5, [low, high], fs=sampling_rate, btype='band', output='sos')
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len-1, col] = np.nan
        else:
            # Apply filter
            filtered_section = scipy.signal.sosfiltfilt(sos, masked_data.loc[val_ind:val_ind+val_len-1, col].copy())
            masked_data.loc[val_ind:val_ind+val_len-1, col] = filtered_section
    
    # Put masked_data back in band_Signal
    band_Signal.loc[min_nan_mask, col] = masked_data[col].values
    
    return band_Signal

#
# =============================================================================
#

def bandpass_filter_signals(in_path:str, out_path:str, sampling_rate:float, low:float=20.0, high:float=450.0, cols=None, min_segment:float=30.0, expression:str=None, exp_copy:bool=False, file_ext:str='csv'):
    """
    Apply a bandpass filter ('low', 'high') to all signal files in a folder and
    its subfolders. Writes filtered signal files to an output folder, and
    generates a file structure matching the input folder.
    
    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    out_path : str
        Filepath to a directory to write filtered signals.
    sampling_rate : float
        The sampling rate of the signal files.
    low : float, optional
        Lower frequency limit (Hz) of the bandpass filter. The default is 20.0.
    high : float
        Upper frequency limit (Hz) of the bandpass filter. The default is
        450.0.
    cols : list-str, optional
        List of columns of the signals to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'Time' and columns that start with 'mask_'.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.
    expression : str, optional
        A regular expression. If provided, will only apply the filter to files
        whose local paths inside of 'in_path' match the regular expression. The
        default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        The file extension for files to read. Only filters files with this
        extension. The default is 'csv'.
    
    Raises
    ------
    Warning
        A warning is raised if no files in 'in_path' match with 'expression'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.

    Warning
        A warning is raised if a column from 'cols' contains NaN values.
    Exception
        An exception is raised if a column from 'cols' is not a column of a
        signal file.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'high' or 'low' are higher than 1/2 of
        'sampling_rate'.
    Exception
        An exception is raised if 'high' is not higher than 'low'.
    Exception
        An exception is raised if 'min_segment' is longer than a signal
        recording.
        
    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    
    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("The regular expression '" + str(expression) + "' did not compile.")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("The regular expression '" + str(expression) + "' did not match with any files.")
    
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file)!=None)):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
              
            # Apply filter to columns
            for col in cols:
                data = apply_bandpass_filter(data, col, sampling_rate, low, high, min_segment=min_segment)
            
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
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
    return

#
# =============================================================================
#
#
# FWR
#
#
# =============================================================================
#

def apply_rectify(Signal:pd.DataFrame, col:str):
    """
    Apply a Full Wave Rectifier (FWR) to a column of 'Signal'.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the FWR filter is applied to.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.

    Returns
    -------
    fwr_Signal : pd.DataFrame
        A copy of 'Signal' after the FWR filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', and a
    # warning is raised if it contains NaNs.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if Signal[col].isnull().values.any():
        warnings.warn("NaN values detected in 'Signal'.")
    
    fwr_Signal = Signal.copy().reset_index(drop=True)
    fwr_Signal[col] = np.abs(fwr_Signal[col])
    
    return fwr_Signal

#
# =============================================================================
#

def rectify_signals(in_path:str, out_path:str, cols=None, expression:str=None, exp_copy:bool=False, file_ext:str='csv'):
    """
    Apply a Full Wave Rectifier (FWR) to all signal files in a folder and its
    subfolders. Writes filtered signal files to an output folder, and generates
    a file structure matching the input folder.
    
    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    out_path : str
        Filepath to a directory to write filtered signals.
    cols : list-str, optional
        List of columns of the signals to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'Time' and columns that start with 'mask_'.
    expression : str, optional
        A regular expression. If provided, will only apply the filter to files
        whose local paths inside of 'in_path' match the regular expression. The
        default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        The file extension for files to read. Only filters files with this
        extension. The default is 'csv'.
    
    Raises
    ------
    Warning
        A warning is raised if no files in 'in_path' match with 'expression'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
        
    Warning
        A warning is raised if a column from 'cols' contains NaN values.
    Exception
        An exception is raised if a column from 'cols' is not a column of a
        signal file.
        
    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    
    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("The regular expression '" + str(expression) + "' did not compile.")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("The regular expression '" + str(expression) + "' did not match with any files.")
    
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file)!=None)):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
              
            # Apply filter to columns
            for col in cols:
                data = apply_rectify(data, col)
            
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
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
            
    return

#
# =============================================================================
#
#
# HAMPEL FILTER
#
#
# =============================================================================
#

def apply_screen_artefacts(Signal:pd.DataFrame, col:str, sampling_rate:float, window_ms:float=100.0, n_sigma:float=10.0, min_segment:float=30.0):
    """
    Apply a Hampel filter ('window_ms', 'n_sigma') to a column of 'Signal'.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the Hampel filter is applied to.
    sampling_rate : float
        The sampling rate of 'Signal'.
    window_ms : float, optional
        The size of the outlier detection window in ms. The default is 100.0.
    n_sigma : float, optional
        The number of standard deviations away for a value to be considered an
        outlier. The default is 10.0.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Warning
        A warning is raised if 'window_ms' is longer than half the recording of
        'Signal'.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'window_ms' results in a window size less
        than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than the recording of
        'Signal'.

    Returns
    -------
    hamp_Signal : pd.DataFrame
        A copy of 'Signal' after the Hampel filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', and a
    # warning is raised if it contains NaNs.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if Signal[col].isnull().values.any():
        warnings.warn("NaN values detected in 'Signal'.")
    
    # An exception is raised if 'sampling_rate' is less or equal to 0.
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    # A warning is raised if the length created by 'window_ms' is greater than
    # the length of 'Signal', and an exception is raised if it is less than or
    # equal to 0.
    window_size = int(window_ms * sampling_rate / 1000.0)
    if window_size > len(Signal)/2:
        warnings.warn("'window_ms' is longer than 1/2 the recording of 'Signal', results may be poor.")
    if window_size <= 0:
        raise Exception("'window_size' must be greater than 0.")
    
    # An exception is raised if the length created by 'min_segment' is greater
    # than the length of 'Signal'.
    min_gap = int(min_segment * sampling_rate / 1000.0)
    if min_gap > len(Signal):
        raise Exception("'min_segment' cannot be longer than the recording of 'Signal'.")
    
    hamp_Signal = Signal.copy().reset_index(drop=True)
        
    # Internal function for applying the Hampel filter
    def hampel_filter(data, window_size:int=50, n_sigma:float=5.0):
        n = len(data)
        half_window=int(window_size//2)
        
        filtered_data=data.copy()
        mask=np.full(n,True)
        
        for i in range(n):
            # Handle edge cases with slicing
            start = max(0, i-half_window)
            end = min(n, i+half_window+1)
            window=data[start:end]
            
            median=np.nanmedian(window)
            mad = np.nanmedian(np.abs(window-median))
            threshold=n_sigma*1.4826*mad
            
            if abs(data[i]-median) > threshold:
                filtered_data[i] = median
                mask[i] = False
            
        return filtered_data, mask
    
    # Construct list of NaN locations
    data = hamp_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data))
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask.loc[nan_ind:nan_ind+nan_len-1] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = hamp_Signal[min_nan_mask].copy().reset_index(drop=True)
    
    # Construct list of value locations
    data = masked_data[col]
    mask = data.notna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    val_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create a mask for masked_data
    hamp_mask = pd.Series(np.full(len(masked_data), True))
    
    # Apply Hampel filters to each value sequence set sequences that are too
    # small to NaN
    for (val_ind, val_len) in val_sequences:
        if val_len < min_gap:
            # Set value to NaN
            masked_data.loc[val_ind:val_ind+val_len-1, col] = np.nan
        else:
            # Apply filter
            filtered_section, mask = hampel_filter(masked_data.loc[val_ind:val_ind+val_len-1, col].to_numpy(), window_size=window_size, n_sigma=n_sigma)
            masked_data.loc[val_ind:val_ind+val_len-1, col] = filtered_section
            hamp_mask.loc[val_ind:val_ind+val_len-1] = mask
    
    # Put masked_data back in hamp_Signal
    hamp_Signal.loc[min_nan_mask, col] = masked_data[col].values
    
    # Create a mask for the full column and add the masked values
    full_mask = pd.Series(np.full(len(hamp_Signal), True))
    full_mask[min_nan_mask] = hamp_mask.values
    
    # Merge with the mask column if it exists
    mask_col = 'mask_' + col
    if mask_col not in list(hamp_Signal.columns.values):
        hamp_Signal[mask_col] = full_mask.values
    else:
        hamp_Signal[mask_col] = hamp_Signal[mask_col] & full_mask.values
    
    return hamp_Signal

#
# =============================================================================
#

def screen_artefact_signals(in_path:str, out_path:str, sampling_rate:float, window_ms:float=100.0, n_sigma:float=10.0, cols=None, min_segment:float=30.0, expression:str=None, exp_copy:bool=False, file_ext:str='csv'):
    """
    Apply a hampel filter ('window_ms', 'n_sigma') to all signal files in a
    folder and its subfolders. Writes filtered signal files to an output
    folder, and generates a file structure matching the input folder.

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    out_path : str
        Filepath to a directory to write filtered signals.
    sampling_rate : float
        The sampling rate of the signal files.
    window_ms : float, optional
        The size of the outlier detection window in ms. The default is 100.0.
    n_sigma : float, optional
        The number of standard deviations away for a value to be considered an
        outlier. The default is 10.0.
    cols : list-str, optional
        List of columns of the signals to apply the filter to. The default is
        None, in which case the filter is applied to every column except for
        'Time' and columns that start with 'mask_'.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.
    expression : str, optional
        A regular expression. If provided, will only apply the filter to files
        whose local paths inside of 'in_path' match the regular expression. The
        default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without filtering. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        The file extension for files to read. Only filters files with this
        extension. The default is 'csv'.

    Raises
    ------
    Warning
        A warning is raised if no files in 'in_path' match with 'expression'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
        
    Warning
        A warning is raised if a column from 'cols' contains NaN values.
    Warning
        A warning is raised if 'window_ms' is longer than half a signal
        recording.
    Exception
        An exception is raised if a column from 'cols' is not a column of a
        signal file.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'window_ms' results in a 'window_size' less
        than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than a signal
        recording.
          
    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.

    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("The regular expression '" + str(expression) + "' did not compile.")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("The regular expression '" + str(expression) + "' did not match with any files.")
        
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file)!=None)):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
            
            # Apply filter to columns
            for col in cols:
                data = apply_screen_artefacts(data, col, sampling_rate, window_ms=window_ms, n_sigma=n_sigma, min_segment=min_segment)
            
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
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    
    return

#
# =============================================================================
#
#
# FILL MISSING
#
#
# =============================================================================
#

def apply_fill_missing(Signal:pd.DataFrame, col:str, sampling_rate:float, method:str='pchip', max_segment:float=500.0):
    """
    Apply an interpolation method ('method') to a column of 'Signal'. Fills NaN
    values with interpolated results.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the interpolation is applied to.
    sampling_rate : float
        The sampling rate of 'Signal'.
    method : str, optional
        The interpolation method to use. Valid methods are 'pchip' and
        'spline'. The default is 'pchip'.
    max_segment : float, optional
        The maximum length (in ms) of NaN values to fill. If a length of
        invalid data is longer than this threshold, it will not be
        interpolated. The default is 500.0.

    Raises
    ------
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'col' is 'Time'.
    Exception
        An exception is raised if 'Time' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'method' is an invalid interpolation method.
    Exception
        An exception is raised if there aren't enough valid points to perform
        interpolation.

    Returns
    -------
    filled_Signal : pd.DataFrame
        A copy of 'Signal' after the NaN values are filled.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', or is
    # 'Time'.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if col == 'Time':
        raise Exception("Column cannot be 'Time'.")
    
    # An exception is raised if 'Signal' does not have a 'Time' column
    if 'Time' not in list(Signal.columns.values):
        raise Exception("Column 'Time' not found in 'Signal'.")
        
    # An exception is raised if 'sampling_rate' is less or equal to 0.
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    max_gap = int(max_segment * sampling_rate / 1000.0)
    if max_gap <= 0:
        raise Exception("'max_segment' cannot result in a gap size less than 0.")
    
    filled_Signal = Signal.copy().reset_index(drop=True)
    
    # Construct list of NaN locations
    data = filled_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Drop NaN sequences less than 'max_gap'
    nan_sequences = [seq for seq in nan_sequences if seq[1] > max_gap]
    
    # Get valid values by dropping NaNs
    view_sig = filled_Signal[['Time', col]].copy()
    view_sig = view_sig.dropna(subset=[col])
    
    valid_values = view_sig[col]
    valid_index = view_sig['Time']
    
    # Ensure values are sorted properly
    valid_index, valid_values = zip(*sorted(zip(valid_index, valid_values)))
    
    # Create NaN mask
    full_mask = filled_Signal[col].notna()
    
    # Merge with the mask column if it exists
    mask_col = 'mask_' + col
    if mask_col not in list(filled_Signal.columns.values):
        filled_Signal[mask_col] = full_mask
    else:
        filled_Signal[mask_col] = filled_Signal[mask_col] & full_mask
    
    # Perform interpolation
        
    if method=='pchip':
        
        if len(valid_values) < 2:
            raise Exception('Not enough valid points for PCHIP interpolation.')
        else:
            # Perform interpolation
            pchip = scipy.interpolate.PchipInterpolator(valid_index, valid_values, extrapolate=False)
            filled_Signal[col] = filled_Signal[col].combine_first(pd.Series(pchip(filled_Signal['Time']), index=filled_Signal.index))
        
    elif method=='spline':
        
        if len(valid_index) < 4:
            raise Exception('Not enough valid points for cubic spline interpolation.')
        else:
            # Perform interpolation
            cs = scipy.interpolate.CubicSpline(valid_index, valid_values, extrapolate=False)
            filled_Signal[col] = filled_Signal[col].combine_first(pd.Series(cs(filled_Signal['Time']), index=filled_Signal.index))
    
    else:
        raise Exception("Invalid interpolation method chosen: " + str(method), ", use 'pchip' or 'spline'.")
    
    # Reinsert filtered NaNs
    for (nan_ind, nan_len) in nan_sequences:
        filled_Signal.loc[nan_ind:nan_ind+nan_len-1,col] = np.nan
    
    return filled_Signal

#
# =============================================================================
#

def fill_missing_signals(in_path:str, out_path:str, sampling_rate:float, method:str='pchip', max_segment:float=500.0, cols=None, expression:str=None, exp_copy:bool=False, file_ext:str='csv'):
    """
    Apply an interpolation method ('method') to all signal files in a folder
    and its subfolders. Writes interpolated signal files to an output folder,
    and generates a file structure matching the input structure.

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    out_path : str
        Filepath to a directory to write filtered signals.
    sampling_rate : float
        The sampling rate of the signal files.
    method : str, optional
        The interpolation method to use. Valid methods are 'pchip' and
        'spline'. The default is 'pchip'.
    max_segment : float, optional
        The maximum length (in ms) of NaN values to fill. If a length of
        invalid data is longer than this threshold, it will not be
        interpolated. The default is 500.0
    cols : list-str, optional
        List of columns of the signals to apply the interpolation to. The
        default is None, in which case the interpolation is applied to every
        column except for 'Time' and columns that start with 'mask_'.
    expression : str, optional
        A regular expression. If provided, will only apply the interpolation to
        files whose local paths inside of 'in_path' match the regular
        expression. The default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without interpolating. The default is False, which
        ignores files that don't match.
    file_ext : str, optional
        The file extension for files to read. Only interpolates files with this
        extension. The default is 'csv'.

    Raises
    ------
    Warning
        A warning is raised if no files in 'in_path' match with 'expression'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
    
    Exception
        An exception is raised if a column from 'cols' is not a column of a
        signal file.
    Exception
        An exception is raised if 'Time' is in 'cols'.
    Exception
        An exception is raised if 'Time' is not a column of a signal file.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'method' is an invalid interpolation method.
    Exception
        An exception is raised if there aren't enough valid points to perform
        interpolation on a signal file.
    
    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.

    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("The regular expression '" + str(expression) + "' did not compile.")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("The regular expression '" + str(expression) + "' did not match with any files.")
        
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file)!=None)):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
            
            # Apply filter to columns
            for col in cols:
                data = apply_fill_missing(data, col, sampling_rate=sampling_rate, method=method, max_segment=max_segment)
            
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
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    
    return

#
# =============================================================================
#
#
# SMOOTH
#
#
# =============================================================================
#

def apply_boxcar_smooth(Signal:pd.DataFrame, col:str, sampling_rate:float, window_ms:float=50.0, min_segment:float=30.0):
    """
    Apply a boxcar smoothing filter to a column of 'Signal'.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the boxcar smoothing filter is applied to.
    sampling_rate : float
        The sampling rate of 'Signal'.
    window_ms : float, optional.
        The size of the smoothing window in ms. The default is 50.0.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.
    
    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Warning
        A warning is raised if 'window_ms' is longer than half the recording of
        'Signal'.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0
    Exception
        An exception is raised if 'window_ms' results in a window size less
        than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than the recording of
        'Signal'.
    
    Returns
    -------
    boxcar_Signal : pd.DataFrame
        A copy of 'Signal' after the boxcar smoothing filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', and a
    # warning is raised if it contains NaNs.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if Signal[col].isnull().values.any():
        warnings.warn("NaN values detected in 'Signal'.")
    
    # An exception is raised if 'sampling_rate' is less than or equal to 0.
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    # A warning is raised if the length created by 'window_ms' is greater than
    # the length of 'Signal', and an exception is raised if it is less than or
    # equal to 0.
    window_size = int(window_ms * sampling_rate / 1000.0)
    if window_size > len(Signal)/2:
        warnings.warn("'window_ms' is longer than 1/2 the recording of 'Signal', results may be poor.")
    if window_size <= 0:
        raise Exception("'window_size' must be greater than 0.")
    
    # An exception is raised if the length created by 'min_segment' is greater
    # than the length of 'Signal'.
    min_gap = int(min_segment * sampling_rate / 1000.0)
    if min_gap > len(Signal):
        raise Exception("Minimum length created by 'min_segment' is greater than 'Signal' length.")
    
    boxcar_Signal = apply_rectify(Signal, col)
    
    # Construct list of NaN locations
    data = boxcar_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data), index=data.index).copy()
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask.loc[nan_ind:nan_ind+nan_len-1] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = boxcar_Signal[min_nan_mask].copy().reset_index(drop=True)
    
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
            masked_data.loc[val_ind:val_ind+val_len-1, col] = np.nan
        else:
            # Apply filter
            filtered_section = np.convolve(masked_data.loc[val_ind:val_ind+val_len-1, col].copy(), window, 'same')
            masked_data.loc[val_ind:val_ind+val_len-1, col] = filtered_section
    
    # Put masked_data back in boxcar_Signal
    boxcar_Signal.loc[min_nan_mask, col] = masked_data[col].values
    
    return boxcar_Signal

#
# =============================================================================
#

def apply_rms_smooth(Signal:pd.DataFrame, col:str, sampling_rate:float, window_ms:float=50.0, min_segment:float=30.0):
    """
    Apply a Root Mean Square (RMS) smoothing filter to a column of 'Signal'.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the RMS smoothing filter is applied to.
    sampling_rate : float
        The sampling rate of 'Signal'.
    window_ms : float, optional.
        The size of the smoothing window in ms. The default is 50.0.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Warning
        A warning is raised if 'window_ms' is longer than half the recording of
        'Signal'.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0
    Exception
        An exception is raised if 'window_ms' results in a window size less
        than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than the recording of
        'Signal'.

    Returns
    -------
    rms_Signal : pd.DataFrame
        A copy of 'Signal' after the RMS smoothing filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', and a
    # warning is raised if it contains NaNs.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if Signal[col].isnull().values.any():
        warnings.warn("NaN values detected in 'Signal'.")
    
    # An exception is raised if 'sampling_rate' is less than or equal to 0.
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    # A warning is raised if the length created by 'window_ms' is greater than
    # the length of 'Signal', and an exception is raised if it is less than or
    # equal to 0.
    window_size = int(window_ms * sampling_rate / 1000.0)
    if window_size > len(Signal)/2:
        warnings.warn("'window_ms' is longer than 1/2 the recording of 'Signal', results may be poor.")
    if window_size <= 0:
        raise Exception("'window_size' must be greater than 0.")
    
    # An exception is raised if the length created by 'min_segment' is greater
    # than the length of 'Signal'.
    min_gap = int(min_segment * sampling_rate / 1000.0)
    if min_gap > len(Signal):
        raise Exception("Minimum length created by 'min_segment' is greater than 'Signal' length.")
    
    rms_Signal = Signal.copy().reset_index(drop=True)
    
    # Construct list of NaN locations
    data = rms_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data), index=data.index).copy()
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask.loc[nan_ind:nan_ind+nan_len-1] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = rms_Signal[min_nan_mask].copy().reset_index(drop=True)
    
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
            masked_data.loc[val_ind:val_ind+val_len-1, col] = np.nan
        else:
            # Apply filter
            filtered_section = np.sqrt(np.convolve(masked_data.loc[val_ind:val_ind+val_len-1, col].copy() ** 2, window, 'same'))
            masked_data.loc[val_ind:val_ind+val_len-1, col] = filtered_section
    
    # Put masked_data back in rms_Signal
    rms_Signal.loc[min_nan_mask, col] = masked_data[col].values
    
    return rms_Signal

#
# =============================================================================
#

def apply_gaussian_smooth(Signal:pd.DataFrame, col:str, sampling_rate:float, window_ms:float=50.0, sigma:float=1.0, min_segment:float=30.0):
    """
    Apply a Gaussian smoothing filter to a column of 'Signal'.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the Gaussian smoothing filter is applied to.
    sampling_rate : float
        The sampling rate of 'Signal'.
    window_ms : float, optional.
        The size of the smoothing window in ms. The default is 50.0.
    sigma : float, optional
        Parameter of sigma in the Gaussian smoothing. The default is 1.0.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.
        
    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Warning
        A warning is raised if 'window_ms' is longer than half the recording of
        'Signal'.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0
    Exception
        An exception is raised if 'window_ms' results in a window size less
        than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than the recording of
        'Signal'.

    Returns
    -------
    gauss_Signal : pd.DataFrame
        A copy of 'Signal' after the Gaussian smoothing filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', and a
    # warning is raised if it contains NaNs.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if Signal[col].isnull().values.any():
        warnings.warn("NaN values detected in 'Signal'.")
    
    # An exception is raised if 'sampling_rate' is less than or equal to 0.
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    # A warning is raised if the length created by 'window_ms' is greater than
    # the length of 'Signal', and an exception is raised if it is less than or
    # equal to 0.
    window_size = int(window_ms * sampling_rate / 1000.0)
    if window_size > len(Signal)/2:
        warnings.warn("'window_ms' is longer than 1/2 the recording of 'Signal', results may be poor.")
    if window_size <= 0:
        raise Exception("'window_size' must be greater than 0.")
    
    # An exception is raised if the length created by 'min_segment' is greater
    # than the length of 'Signal'.
    min_gap = int(min_segment * sampling_rate / 1000.0)
    if min_gap > len(Signal):
        raise Exception("Minimum length created by 'min_segment' is greater than 'Signal' length.")
    
    gauss_Signal = apply_rectify(Signal, col)
    
    # Helper function for creating a Gaussian kernel
    def get_gauss(n, sigma):
        r = range(-int(n/2), int(n/2)+1)
        return [1 / (sigma * np.sqrt(2*np.pi)) * np.exp(-float(x)**2/(2*sigma**2)) for x in r]
    
    # Construct list of NaN locations
    data = gauss_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data), index=data.index)
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask.loc[nan_ind:nan_ind+nan_len-1] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = gauss_Signal[min_nan_mask].copy().reset_index(drop=True)
    
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
            masked_data.loc[val_ind:val_ind+val_len-1, col] = np.nan
        else:
            # Apply filter
            filtered_section = np.convolve(masked_data.loc[val_ind:val_ind+val_len-1, col].copy(), window, 'same')
            masked_data.loc[val_ind:val_ind+val_len-1, col] = filtered_section
    
    # Put masked_data back in gauss_Signal
    gauss_Signal.loc[min_nan_mask, col] = masked_data[col].values
    
    return gauss_Signal

#
# =============================================================================
#

def apply_loess_smooth(Signal:pd.DataFrame, col:str, sampling_rate:float, window_ms:float=50.0, min_segment:float=30.0):
    """
    Apply a Loess smoothing filter to a column of 'Signal'.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        The column of 'Signal' the Loess smoothing filter is applied to.
    sampling_rate : float
        The sampling rate of 'Signal'.
    window_ms : float, optional.
        The size of the smoothing window in ms. The default is 50.0.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.

    Raises
    ------
    Warning
        A warning is raised if 'col' contains NaN values.
    Warning
        A warning is raised if 'window_ms' is longer than half the recording of
        'Signal'.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0
    Exception
        An exception is raised if 'window_ms' results in a window size less
        than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than the recording of
        'Signal'.

    Returns
    -------
    loess_Signal : DataFrame
        A copy of 'Signal' after the Loess smoothing filter is applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal', and a
    # warning is raised if it contains NaNs.
    if col not in list(Signal.columns.values):
        raise Exception("Column '" + str(col) + "' not found in 'Signal'.")
    if Signal[col].isnull().values.any():
        warnings.warn("NaN values detected in 'Signal'.")
    
    # An exception is raised if 'sampling_rate' is less than or equal to 0.
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    # A warning is raised if the length created by 'window_ms' is greater than
    # the length of 'Signal', and an exception is raised if it is less than or
    # equal to 0.
    window_size = int(window_ms * sampling_rate / 1000.0)
    if window_size > len(Signal)/2:
        warnings.warn("'window_ms' is longer than 1/2 the recording of 'Signal', results may be poor.")
    if window_size <= 0:
        raise Exception("'window_size' must be greater than 0.")
    
    # An exception is raised if the length created by 'min_segment' is greater
    # than the length of 'Signal'.
    min_gap = int(min_segment * sampling_rate / 1000.0)
    if min_gap > len(Signal):
        raise Exception("Minimum length created by 'min_segment' is greater than 'Signal' length.")
    
    loess_Signal = apply_rectify(Signal, col)
    
    # Construct list of NaN locations
    data = loess_Signal[col]
    mask = data.isna()
    group = (mask != mask.shift()).cumsum()
    group_sequences = data[mask].groupby(group[mask])
    nan_sequences = [(group.index[0], len(group)) for _, group in group_sequences]
    
    # Create NaN mask
    min_nan_mask = pd.Series([True] * len(data), index=data.index)
    for (nan_ind, nan_len) in nan_sequences:
        if nan_len < min_gap:
            min_nan_mask.loc[nan_ind:nan_ind+nan_len-1] = False
    
    # Use mask to remove small NaN groups, construct list of value locations
    masked_data = loess_Signal[min_nan_mask].copy().reset_index(drop=True)
    
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
            masked_data.loc[val_ind:val_ind+val_len-1, col] = np.nan
        else:
            # Apply filter
            filtered_section = np.convolve(masked_data.loc[val_ind:val_ind+val_len-1, col].copy(), window, 'same')
            masked_data.loc[val_ind:val_ind+val_len-1, col] = filtered_section
    
    # Put masked_data back in loess_Signal
    loess_Signal.loc[min_nan_mask, col] = masked_data[col].values
    
    return loess_Signal

#
# =============================================================================
#

def smooth_signals(in_path:str, out_path:str, sampling_rate:float, method:str='rms', window_ms:float=50.0, sigma:float=1.0, cols=None, min_segment:float=30.0, expression:str=None, exp_copy:bool=False, file_ext:str='csv'):
    """
    Apply a smoothing filter ('method') to all signal files in a folder and its
    subfolders. Writes filtered signal files to an output folder, and generates
    a file structure matching the input folder.

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    out_path : str
        Filepath to a directory to write filtered signals.
    sampling_rate : float
        The sampling rate of the signal files.
    method : str, optional
        The smoothing method to use. Valid methods are 'rms', 'boxcar', 'gauss'
        and 'loess'. The default is 'rms'.
    window_ms : float, optional
        The size of the smoothing window in ms. The default is 50.0.
    sigma: float, optional
        The value of sigma used for a Gaussian filter. Only affects output when
        using a Gaussian filter. The default is 1.0.
    cols : list-str, optional
        List of columns of the signals to apply the smoothing filter to. The
        default is None, in which case the smoothing filter is applied to every
        column except for 'Time' and columns that start with 'mask_'.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.
    expression : str, optional
        A regular expression. If provided, will only apply the smoothing filter
        to files whose local paths inside of 'in_path' match the regular
        expression. The default is None.
    exp_copy : bool, optional
        If True, copies files that don't match the regular expression to the
        output folder without smoothing. The default is False, which ignores
        files that don't match.
    file_ext : str, optional
        The file extension for files to read. Only smooths files with this
        extension. The default is 'csv'.

    Raises
    ------
    Warning
        A warning is raised if no files in 'in_path' match with 'expression'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
    Exception
        An exception is raised if 'method' is an invalid smoothing method.
        
    Warning
        A warning is raised if a column from 'cols' contains NaN values.
    Warning
        A warning is raised if 'window_ms' is longer than half a signal
        recording.
    Exception
        An exception is raised if a column from 'cols' is not a column of a
        signal file.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'window_ms' results in a 'window_size' less
        than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than a signal
        recording.
    
    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.

    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("The regular expression '" + str(expression) + "' did not compile.")
    
    # Convert out_path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    
    # Get dictionary of file locations
    if exp_copy:
        file_dirs = map_files(in_path, file_ext=file_ext)
    else:
        file_dirs = map_files(in_path, file_ext=file_ext, expression=expression)
        if len(file_dirs) == 0:
            warnings.warn("Warning: The regular expression '" + str(expression) + "' did not match with any files.")
    
    # Apply transformations
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file)!=None)):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
              
            # Apply filter to columns
            for col in cols:
                if method == 'rms':
                    data = apply_rms_smooth(data, col, sampling_rate, window_ms, min_segment)
                elif method == 'boxcar':
                    data = apply_boxcar_smooth(data, col, sampling_rate, window_ms, min_segment)
                elif method == 'gauss':
                    data = apply_gaussian_smooth(data, col, sampling_rate, window_ms, sigma, min_segment)
                elif method == 'loess':
                    data = apply_loess_smooth(data, col, sampling_rate, window_ms, min_segment)
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
            out_folder = out_file[:len(out_file) - len(os.path.basename(out_file)) - 1]
            
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    return

#
# =============================================================================
#
# OTHER
#
# =============================================================================
#

def clean_signals(path_names:dict, sampling_rate:float=1000.0, min_segment:float=30.0, do_screen=False, do_fill=True, do_smooth=False, file_ext:str='csv'):
    """
    Apply all EMG preprocessing filters to all signal files in a folder and its
    subfolders. Uses the 'path_names' dictionary, starting with files in the
    'Raw' path, and moving through 'Notch', 'Bandpass', and 'FWR' as the
    filters are applied.
    
    Optionally, 'do_screen', 'do_fill' and 'do_smooth' can be set to True to do
    the associated step.
    
    Parameters
    ----------
    path_names : dict-str
        A dictionary of file locations with keys for stage in the processing
        pipeline. Required paths are: 'Raw', 'Notch', 'Bandpass', and 'FWR'.
        The dictionary can be created with the 'make_paths' function.
    sampling_rate : float, optional
        The sampling rate of the signal files. The default is 1000.0.
    min_segment : float, optional
        The minimum length (in ms) for data to be considered valid. If a length
        of data is less than this time, it is set to NaN. If a length of
        invalid data is less than this time, it is ignored in calculations. The
        default is 30.0.
    do_screen : bool, optional
        An option to use the optional processing step of artefact screening.
        The default is False.
    do_fill : bool, optional
        An option to use the optional processing step of filling missing
        values. The default is True.
    do_smooth : boool, optional
        An option to use the optional processing step of smoothing. The default
        is False.
    use_optional : bool, optional
        An option to use the non-required preprocessing steps (artefact
        screening, fill missing data, smooth filter). The default is False.
    file_ext : str, optional
        The file extension for files to read. Only processes files with this
        extension. The default is 'csv'.

    Raises
    ------
    Exception
        An exception is raised if 'Raw', 'Notch', 'Bandpass', or 'FWR' are not
        keys of the 'path_names' dictionary provided.
    Exception
        An exception is raised if 'Screened', 'Filled', or 'Smooth' are not
        keys of the 'path_names' dictionary provided if the associated
        parameter is set to True

    Warning
        A warning is raised if a column from the signal files contains NaN
        values.
    Exception
        An exception is raised if 'sampling_rate' is less than or equal to 0.
    Exception
        An exception is raised if 'min_segment' is longer than the recording of
        'Signal'.

    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.

    Returns
    -------
    None.

    """
    
    # Raise exceptions if paths not found
    if 'Raw' not in path_names:
        raise Exception('Raw path not detected in provided dictionary (path_names).')
    if 'Notch' not in path_names:
        raise Exception('Notch path not detected in provided dictionary (path_names).')
    if 'Bandpass' not in path_names:
        raise Exception('Bandpass path not detected in provided dictionary (path_names).')
    if 'FWR' not in path_names:
        raise Exception('FWR path not detected in provided dictionary (path_names).')
        
    # Run required preprocessing steps
    notch_filter_signals(path_names['Raw'], path_names['Notch'], sampling_rate, min_segment=min_segment, file_ext=file_ext)
    bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], sampling_rate, min_segment=min_segment, file_ext=file_ext)
    rectify_signals(path_names['Bandpass'], path_names['FWR'], file_ext=file_ext)
    
    last = 'FWR'
    
    if do_screen:
        if 'Screened' not in path_names:
            raise Exception("'Screened' path not detected in provided dictionary ('path_names').")
        screen_artefact_signals(path_names[last], path_names['Screened'], sampling_rate, min_segment=min_segment, file_ext=file_ext)
        last = 'Screened'
    
    if do_fill:
        if 'Filled' not in path_names:
            raise Exception("'Filled' path not detected in provided dictionary ('path_names').")
        fill_missing_signals(path_names[last], path_names['Filled'], sampling_rate, file_ext=file_ext)
        last = 'Filled'
    
    if do_smooth:
        if 'Smooth' not in path_names:
            raise Exception("'Smooth' path not detected in provided dictionary ('path_names').")
        smooth_signals(path_names[last], path_names['Smooth'], sampling_rate, min_segment=min_segment, file_ext=file_ext)
    
    return

#
# =============================================================================
#

def detect_spectral_outliers(in_path:str, sampling_rate:float, window_ms:float=50.0, threshold:float=5.0, metric=np.median, low:float=None, high:float=None, cols=None, expression:str=None, file_ext:str='csv'):
    """
    Detect outliers in all signal files in a folder. Returns a dictionary of
    files that contain outliers.
    
    Determines outliers by interpolating an inverse function from the peaks of
    the signal's spectrum, then finding the 'metric' aggregate (median by
    default) of the differences between the predicted spectrum, and the actual
    spectrum. Files are labelled as having outliers if any points are
    'threshold' times greater than the predicted value.

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read signal files.
    sampling_rate : float
        The sampling rate of the signal files.
    window_ms : float, optional
        The size of the outlier detection window in ms. The default is 50.0.
    threshold : float, optional
        The number of times greater than the metric a value has to be for
        classification as an outlier. The default is 5.0.
    metric : function, optional
        The aggregation method to use. Valid methods are any aggregation
        function that works with a list or array (e.g., np.mean). The default
        is np.median.
    low : float, optional
        Lower frequency limit (Hz) of the outlier detection. The default is
        None, in which case no lower threshold is used.
    high : float, optional
        Upper frequency limit (Hz) of the outlier detection. The default is
        None, in which case no upper threshold is used.
    cols : list-str, optional
        List of columns of the signals to apply the outlier detection to. The
        default is None, in which case the outlier detection is applied to
        every column except for 'Time' and columns that start with 'mask_'.
    expression : str, optional
        A regular expression. If provided, will only apply the outlier
        detection to files whose local paths inside of 'in_path' match the
        regular expression. The default is None.
    file_ext : str, optional
        The file extension for files to read. Only detects outliers in files
        with this extension. The default is 'csv'.

    Raises
    ------
    Warning
        A warning is raised if no files in 'in_path' match with 'expression'.
    Warning
        A warning is raised if 'window_ms' is longer than half a signal
        recording.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.
    Exception
        An exception is raised if 'sampling_rate' is not greater than 0.
    Exception
        An exception is raised if 'window_size' is not greater than 0.
    Exception
        An exception is raised if 'threshold' is not greater than 0.
    Exception
        An exception is raised if 'metric' is not a valid summary function.
    Exception
        An exception is raised if 'low' or 'high' are not between 0 and
        'sampling_rate'/2.
    Exception
        An exception is raised if 'low' is greater than 'high'.
    Exception
        An exception is raised if a column from 'cols' is not a column of a
        signal file.
    Exception
        An exception is raised if there is not enough maxima to create an
        interpolation.
    
    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.

    Returns
    -------
    outliers : dict-str
        Dictionary of file names/locations as keys/values for each file
        detected that contains an outlier.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("The regular expression '" + str(expression) + "' did not compile.")
    
    if sampling_rate <= 0:
        raise Exception("'sampling_rate' must be greater than 0.")
    
    # An exception is raised if the length created by 'window_ms' is less than
    # or equal to 0.
    window_size = int(window_ms * sampling_rate / 1000.0)
    if window_size <= 0:
        raise Exception("'window_size' must be greater than 0.")
    
    if threshold <= 0:
        raise Exception("'threshold' must be greater than 0.")
    
    try:
        metric([1,2,3,4,5])
    except:
        raise Exception("Invalid summary metric provided, 'metric' must be able to take a single numeric list as input.")
    
    # Set low and high if left none
    if low is None:
        low = 0
    if high is None:
        high = sampling_rate/2
    
    
    if low < 0 or high < 0:
        raise Exception("'low' and 'high' must be greater than 0.")
    if high > sampling_rate/2 or low > sampling_rate/2:
        raise Exception("'high' and 'low' cannot be greater than 1/2 the sampling rate.")
    if low >= high:
        raise Exception("'high' must be higher than 'low'.")
    
    p_deg = 1   # Degree of equation on the top of the fraction
    q_deg = 2   # Degree of equation on the bottom of the fraction
    
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
    if len(file_dirs) == 0:
        warnings.warn("The regular expression '" + str(expression) + "' did not match with any files.")
    
    # Iterate over detected files
    for file in tqdm(file_dirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file)!=None)):
            
            # Read file
            data = read_file_type(file_dirs[file], file_ext)
            
            if len(data.index)/2 <= window_size:
                warnings.warn("'window_ms' is longer than 1/2 the recording of a signal, results may be poor.")
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
            
            # Set to false
            isOutlier = False
            
            # Iterate over columns
            for i in range(len(cols)):
                col = cols[i]
                
                if col not in list(data.columns.values):
                    raise Exception("Column '" + str(col) + "' not found in 'Signal': " + str(file) + ".")
                
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