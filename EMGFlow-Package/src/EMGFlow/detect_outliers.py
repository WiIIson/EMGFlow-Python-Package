import pandas as pd
import numpy as np
import scipy.optimize
import os
import re
import warnings
from scipy.signal import argrelextrema
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

def detect_outliers(in_path, sampling_rate, threshold, cols=None, low=None, high=None, metric=np.median, expression=None, window_size=200, file_ext='csv'):
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
                psd['max'] = psd.iloc[argrelextrema(psd['Power'].values, np.greater_equal, order=window_size)[0]]['Power']
                
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