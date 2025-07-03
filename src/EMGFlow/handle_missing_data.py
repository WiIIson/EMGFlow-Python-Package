import pandas as pd
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

def apply_fill_missing(Signal, col, method='pchip', use_nan_mask=True):
    
    # An exception is raised if 'col' is not a column of 'Signal'.
    if col not in list(Signal.columns.values):
        raise Exception('Column "' + str(col) + '" not in Signal')
    
    if col == 'Time':
        raise Exception('Column cannot be "Time".')
    
    # An exception is raised if 'Signal' does not have a 'Time' column
    if 'Time' not in list(Signal.columns.values):
        raise Exception('Signal is missing a "Time" column.')
    
    filled_Signal = Signal.copy()
    filled_Signal.set_index('Time')
    
    # Get valid values
    if use_nan_mask:
        # Get valid values from mask filter
        mask_col = 'mask_' + str(col)
        
        # Raise an exception if the mask column does not exist
        if mask_col not in list(filled_Signal.columns.values):
            raise Exception('Mask column not detected for: ' + str(col))
        
        mask = filled_Signal[mask_col]
        valid_values = filled_Signal[mask][col].dropna().values
        valid_index = filled_Signal[mask][col].dropna().index.astype(float)
    else:
        # Get valid values by dropping NaNs
        valid_values = filled_Signal[col].dropna().values
        valid_index = filled_Signal[col].dropna().index.astype(float)
    
    # Perform interpolation
        
    if method=='pchip':
        
        if len(valid_values) < 2:
            raise Exception('Not enough valid points for PCHIP interpolation.')
        else:
            # Perform interpolation
            pchip = scipy.interpolate.PchipInterpolator(valid_index, valid_values)
            filled_Signal[col] = filled_Signal[col].combine_first(pd.Series(pchip(filled_Signal.index.astype(float)), index=filled_Signal.index))
        
    elif method=='spline':
        
        if len(valid_index) < 4:
            raise Exception('Not enough valid points for cubic spline interpolation')
        else:
            # Perform interpolation
            cs = scipy.interpolate.CubicSpline(valid_index, valid_values)
            filled_Signal[col] = filled_Signal[col].combine_first(pd.Series(cs(filled_Signal.index.astype(float)), index=filled_Signal.index))

    else:
        raise Exception('Invalid interpolation method chosen: ' + str(method), ', use "pchip", "spline" or None.')
    
    filled_Signal.reset_index(inplace=True)
    
    return filled_Signal

#
# =============================================================================
#

def fill_missing_signals(in_path, out_path, sampling_rate, method='pchip', use_nan_mask=True, cols=None, expression=None, exp_copy=False, file_ext='csv'):

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
                cols = [col for col in cols if col != 'Time' and not col.startswith('mask_')]
            
            # Apply filter to columns
            for col in cols:
                data = apply_fill_missing(data, col, method=method, use_nan_mask=use_nan_mask)
            
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
