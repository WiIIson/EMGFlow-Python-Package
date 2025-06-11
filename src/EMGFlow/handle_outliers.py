import pandas as pd
import numpy as np
import scipy
import scipy.interpolate
import scipy.signal
import scipy.stats
import os
import re
import warnings
from tqdm import tqdm

from .preprocess_signals import emg_to_psd
from .access_files import *

#
# =============================================================================
#

"""
A collection of functions for finding outliers while testing.
"""

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
                
                psd = emg_to_psd(data[col], sampling_rate=sampling_rate)
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

def apply_fill_missing(Signal, col, method='robust', interpolation='pchip', maxgap=100):
    """
    Removes outlier artifacts from a column of the provided data. Works in two
    stages:
        1. Identifies outliers using 'method', sets them to NaN.
        2. Fills in NaN values using 'interpolation'.
    
    Either stage can be skipped by setting the parameter to None.

    Parameters
    ----------
    Signal : pd.DataFrame
        A Pandas dataframe containing a 'Time' column, and additional columns
        for signal data.
    col : str
        Column of 'Signal' the filter is applied to.
    method : str, optional
        The outlier detection method being used. Valid options are 'robust',
        'normal', or None. The default is 'robust'.
    interpolation : str, optional
        The interpolation method being used to fill outliers. Valid options are
        'pchip', 'spline' or None. The default is 'pchip'.
    maxgap : int, optional
        The maximum number of NaN values that can be present for the
        interpolation method to trigger. If more than this number of NaN values
        are present (including those flagged as outliers), a warning will raise
        and the interpolation step will be skipped. The default is 100.

    Raises
    ------
    Warning
        A warning is raised if more than 'maxgap' NaN values are detected in
        Signal at the interpolation stage.
    Exception
        An exception is raised if 'col' is not a column of 'Signal'.
    Exception
        An exception is raised if 'Time' is not a column of 'Signal'.
    Exception
        An exception is raised if 'method' is not a valid outlier detection
        method.
    Exception
        An exception is raised if 'interpolation' is not a valid interpolation
        method.
    Exception
        An exception is raised if not enough valid values are present to
        perform interpolation.

    Returns
    -------
    Signal : pd.DataFrame
        A copy of the 'Signal' dataframe with the artifact screening applied.

    """
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception("Column " + str(col) + " not in Signal")
    
    # An exception is raised if 'Signal' does not have a 'Time' column
    if 'Time' not in list(Signal.columns.values):
        raise Exception('Signal is missing a "Time" column.')
    
    Signal = Signal.copy()
    Signal = Signal.set_index('Time')
    
    # 1. Identify outlier parameters
    if method=='robust':
        # Set high and low with robust method
        high = np.nanmedian(Signal[col]) + 5*(1.482*scipy.stats.median_abs_deviation(Signal[col], nan_policy='omit'))
        low = np.nanmedian(Signal[col]) - 5*(1.482*scipy.stats.median_abs_deviation(Signal[col], nan_policy='omit'))
    elif method=='normal':
        # Set high and low with normal method
        high = np.nanmean(Signal[col]) + 5*np.nanstd(Signal[col])
        low = np.nanmean(Signal[col]) - 5*np.nanstd(Signal[col])
    elif method is None:
        pass
    else:
        raise Exception('Invalid outlier detection method chosen: ' + str(method) + ', use "robust", "normal" or None.')
    
    # 2. Set outliers to NaN
    Signal.loc[(Signal[col] < low) | (Signal[col] > high), col] = np.nan
    
    # 3. Gap fill with interpolation method
    total_gap = Signal[col].isna.sum()
    if total_gap > maxgap:
        warnings.warn("Warning: " + str(total_gap) + " NaN values detected, aborting interpolation.")
        
    elif interpolation=='pchip':
        
        # Remove NA entries
        valid_index = Signal[col].dropna().index.astype(float)
        valid_values = Signal[col].dropna().values
        
        if len(valid_index) < 2:
            raise Exception('Not enough valid points for PCHIP interpolation.')
        else:
            # Perform interpolation
            pchip = scipy.interpolate.PchipInterpolator(valid_index, valid_values)
            Signal[col] = Signal[col].combine_first(pd.Series(pchip(Signal.index.astype(float)), index=Signal.index))
        
    elif interpolation=='spline':
        
        # Remove NA entries
        valid_index = Signal[col].dropna().index.astype(float)
        valid_values = Signal[col].dropna().values
        
        if len(valid_index) < 4:
            raise Exception('Not enough valid points for cubic spline interpolation')
        else:
            # Perform interpolation
            cs = scipy.interpolate.CubicSpline(valid_index, valid_values)
            Signal[col] = Signal[col].combine_first(pd.Series(cs(Signal.index.astype(float)), index=Signal.index))
    
    elif interpolation is None:
        pass
    else:
        raise Exception('Invalid interpolation method chosen: ' + str(interpolation), ', use "pchip", "spline" or None.')
    
    return Signal

#
# =============================================================================
#

def fill_missing_signals(in_path, out_path, method='robust', interpolation='pchip', maxgap=100, cols=None, expression=None, exp_copy=False, file_ext='csv'):
    
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
            
            # Apply artifact screening to columns
            for col in cols:
                data = apply_fill_missing(data, col, method=method, interpolation=interpolation, maxgap=maxgap)
            
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