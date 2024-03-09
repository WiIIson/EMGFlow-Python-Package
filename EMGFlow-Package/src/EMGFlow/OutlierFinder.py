import pandas as pd
import numpy as np
import scipy.optimize
import os
import re
from scipy.signal import argrelextrema
from tqdm import tqdm

from SignalFilterer import MapFiles, EMG2PSD
from PlotSignals import PlotSpectrum

#
# =============================================================================
#

"""
A collection of functions for finding outliers while testing
"""

#
# =============================================================================
#

def DetectOutliers(in_path, sampling_rate, threshold, cols=None, low=None, high=None, metric=np.median, expression=None, file_ext='csv'):
    """
    Looks at all Signals contained in a filepath, returns a dictionary of file names and locations
    that have outliers.

    Parameters
    ----------
    in_path : str
        Filepath to a directory to read Signal files.
    sampling_rate : float
        Sampling rate of the Signal.
    cols : TYPE
        List of columns of the Signal to search for outliers in. The default is None, in which case outliers are
        searched for in every column except for 'time'.
    threshold : float
        The number of times greater than the metric a value has to be to be considered an outlier.
    low : float, optional
        Lower frequency limit of where to search for outliers. Should be the same as lower limit for bandpass
        filtering, or some value that eliminates the irrelevant lower frequency ranges. The default is None, in which
        case no lower threshold is used.
    high : float, optional
        Upper frequency limit of where to search for outliers. Should be the same as upper limit for bandpass
        filtering, or some value that eliminates the irrelevant upper frequency ranges. The default is None, in which
        case no upper threshold is used.
    metric : function, optional
        Some summary function that defines the metric used for finding outliers. The default is np.median, but others
        such as np.mean can be used instead.
    expression : str, optional
        A regular expression. If provided, will only search for outliers in files whose names match the regular
        expression. The default is None.
    file_ext : str, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.

    Returns
    -------
    dict
        Dictionary of file names/locations as keys/values for each file detected that contains an outlier.

    """
    
    p_deg = 1   # Degree of equation on the top of the fraction
    q_deg = 2   # Degree of equation on the bottom of the fraction
    
    # Set low and high if left none
    if low is None:
        low = 0
    if high is None:
        high = sampling_rate/2
    
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
        in_path = os.path.abspath(in_path) + '\\'
    
    # Get dictionary of files
    filedirs = MapFiles(in_path, file_ext=file_ext, expression=expression)
    
    # Iterate over detected files
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            print('Checking subject ' + file)
            
            # Read file
            data = pd.read_csv(filedirs[file])
            
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
                psd = EMG2PSD(data[col], sampling_rate=sampling_rate)
                psd = ZoomIn(psd, 20, 450)
                
                n = 200     # Width of band to check for local maxima in PSD
                
                # Create column containing local maxima
                psd['max'] = psd.iloc[argrelextrema(psd['Power'].values, np.greater_equal, order=n)[0]]['Power']
                
                # Filter non-maxima
                maxima = psd[psd['max'].notnull()]
    
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
                    print('\tOutlier in: ' + cols[i])
                    isOutlier = True
            
            # If any columns has an outlier, mark as an outlier
            if isOutlier:
                # print('\tOutlier detected...')
                outliers[file] = filedirs[file]
                
    return outliers

#
# =============================================================================
#

"""
if __name__ == '__main__':
    
    raw_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/01_Raw/'
    notch_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/02_Notch/'
    notch_s_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/02_Notch_Special/'
    bandpass_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/03_Bandpass/'
    smooth_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/04_Smooth/'
    feature_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/05_Feature/'
    plot_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/00_Plot/New/'
    
    sampling_rate = 2000
    
    outliers = DetectOutliers(notch_path, sampling_rate, 15, cols=['EMG_zyg', 'EMG_cor'])
    
    PlotSpectrum(outliers, plot_path, sampling_rate, cols=['EMG_zyg', 'EMG_cor'])
"""  