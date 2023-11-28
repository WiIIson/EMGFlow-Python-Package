import neurokit2 as nk
import pandas as pd
import numpy as np
import scipy.optimize
import os
import re
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from tqdm import tqdm

from PlotSubjects import MapFiles
from PlotSubjects import ZoomIn

#
# =============================================================================
#

# A collection of functions for finding outliers while
# testing

#
# =============================================================================
#

# Get a list of filenames of outliers from the cleaned data using
# a threshold value (that many times the median)
def FindOutliers(in_data, sampling_rate, threshold):
    outliers = []
    
    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('PID_[0-9]{2}-[0-9]{2}$', raw):
            in_raw = in_data + raw + '/'
            
            # Iterate through each person folder
            for person in os.listdir(in_raw):
                print("Checking subject", person, "...")
                in_person = in_raw + person + '/'
                
                # Iterate through each phsiological data file
                for file in os.listdir(in_person):
                    in_file = in_person + file
                    
                    # Get data
                    data = pd.read_csv(in_file)
                    
                    # Make PSDs
                    psd_zyg = nk.signal_psd(data['EMG_zyg'], sampling_rate=sampling_rate)
                    psd_cor = nk.signal_psd(data['EMG_cor'], sampling_rate=sampling_rate)
                    psd_zyg_med = ZoomIn(psd_zyg, 20, 450)
                    psd_cor_med = ZoomIn(psd_cor, 20, 450)
                    
                    # Get medians
                    med_zyg = np.median(psd_zyg_med['Power'])
                    med_cor = np.median(psd_cor_med['Power'])
                    #print(med_zyg)
                    
                    # Find maximum values
                    max_zyg = max(psd_zyg['Power'])
                    max_cor = max(psd_cor['Power'])
                    #print(max_zyg)
                    
                    # Check if max value is greater than threshold * max_value
                    if (max_zyg >= threshold * med_zyg) or (max_cor >= threshold * med_cor):
                        print('\tOutlier detected...')
                        outliers.append(in_file)
    
    print("Done.")
    return outliers

#
# =============================================================================
#

# Get a list of filenames of outliers from the cleaned data using
# a threshold value (that many times the median)
def FindOutliers2(in_data, sampling_rate, threshold):
    
    p_deg = 1
    q_deg = 2
    
    def Rational(x, *params):
        p = params[:p_deg]
        q = params[p_deg:]
        return np.polyval(p, x) / np.polyval(q, x)
    
    outliers = []
    
    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('PID_[0-9]{2}-[0-9]{2}$', raw):
            in_raw = in_data + raw + '/'
            
            # Iterate through each person folder
            for person in os.listdir(in_raw):
                print("Checking subject", person, "...")
                in_person = in_raw + person + '/'
                
                # Iterate through each phsiological data file
                for file in os.listdir(in_person):
                    in_file = in_person + file
                    
                    # Get data
                    data = pd.read_csv(in_file)
                    
                    # Make PSDs
                    psd_zyg = nk.signal_psd(data['EMG_zyg'], sampling_rate=sampling_rate)
                    psd_cor = nk.signal_psd(data['EMG_cor'], sampling_rate=sampling_rate)
                    psd_zyg = ZoomIn(psd_zyg, 20, 450)
                    psd_cor = ZoomIn(psd_cor, 20, 450)
                    
                    # Get local maxima
                    n = 200
                    psd_zyg['max'] = psd_zyg.iloc[argrelextrema(psd_zyg['Power'].values, np.greater_equal, order=n)[0]]['Power']
                    psd_cor['max'] = psd_cor.iloc[argrelextrema(psd_cor['Power'].values, np.greater_equal, order=n)[0]]['Power']
                    
                    # Filter non-maxima
                    maxima_zyg = psd_zyg[psd_zyg['max'].notnull()]
                    maxima_cor = psd_cor[psd_cor['max'].notnull()]
                    
                    # Initialize parameters
                    p_init = np.poly1d(np.ones(p_deg))
                    q_init = np.poly1d(np.ones(q_deg))
                    params_init = np.hstack((p_init.coeffs, q_init.coeffs))
                    
                    # Fit the line
                    params_best_zyg, params_covariance_zyg = scipy.optimize.curve_fit(
                        Rational, maxima_zyg['Frequency'], maxima_zyg['Power'], p0=params_init)
                    params_best_cor, params_covariance_cor = scipy.optimize.curve_fit(
                        Rational, maxima_cor['Frequency'], maxima_cor['Power'], p0=params_init)
                    
                    # Get y-values
                    y_values_zyg = Rational(maxima_zyg['Frequency'], *params_best_zyg)
                    y_values_cor = Rational(maxima_cor['Frequency'], *params_best_cor)
                    
                    # Get differences between actual and fitted Power values
                    diffs_zyg = abs(y_values_zyg - maxima_zyg['Power'])
                    diffs_cor = abs(y_values_cor - maxima_cor['Power'])
                    
                    # Get median
                    med_fit_zyg = np.median(diffs_zyg)
                    med_fit_cor = np.median(diffs_cor)
                    
                    # Get max (only care about positive values)
                    max_fit_zyg = np.max(maxima_zyg['Power'] - y_values_zyg)
                    max_fit_cor = np.max(maxima_cor['Power'] - y_values_cor)
                    
                    if (max_fit_zyg > med_fit_zyg * threshold) or (max_fit_cor > med_fit_cor * threshold):
                        print('\tOutlier detected...')
                        outliers.append(in_file)
                        
                        # Debug plots
                        fig, axs = plt.subplots(2, 2, figsize=(15,15))
                        
                        axs[0,0].set_title('Zyg best fit')
                        axs[0,0].plot(psd_zyg['Frequency'], psd_zyg['Power'])
                        axs[0,0].scatter(maxima_zyg['Frequency'], maxima_zyg['max'], c='g')
                        axs[0,0].plot(maxima_zyg['Frequency'], y_values_zyg)
                        
                        axs[1,0].set_title('Cor best fit')
                        axs[1,0].plot(psd_cor['Frequency'], psd_cor['Power'])
                        axs[1,0].scatter(maxima_cor['Frequency'], maxima_cor['max'], c='g')
                        axs[1,0].plot(maxima_cor['Frequency'], y_values_cor)
                        
                        axs[0,1].set_title('Zyg outliers')
                        axs[0,1].scatter(maxima_zyg['Frequency'], list(diffs_zyg))
                        axs[0,1].axhline(y=med_fit_zyg, c='g')
                        axs[0,1].axhline(y=med_fit_zyg * threshold, c='r')
                        axs[0,1].axhline(y=max_fit_zyg, c='b')
                        
                        axs[1,1].set_title('Cor outliers')
                        axs[1,1].scatter(maxima_cor['Frequency'], list(diffs_cor))
                        axs[1,1].axhline(y=med_fit_cor, c='g')
                        axs[1,1].axhline(y=med_fit_cor * threshold, c='r')
                        axs[1,1].axhline(y=max_fit_cor, c='b')
                        
                        fig.savefig('Plots/Debug/' + file[-12:-4] + '.jpg')
    
    print("Done.")
    return outliers

#
# =============================================================================
#

# Looks for outliers in a specified folder path. Will return a dictionary of
# file names and locations for files suspected to have outliers. This list can
# be plotted using the IEMG.PlotSubjects.______ function
#
# in_path           Path to signals being analyzed for outliers
# sampling_rate     Signal sampling rate
# cols              Columns to check for outliers
# threshold         Threshold to use when looking for outliers. Looks for data
#                   that is [threshold] times greater than [metric] of the data
# metric            Some summary function to use to find outliers (e.g.,
#                   np.mean, np.median)
# expression        If left none, will search for outliers in all samples, but
#                   if set, will only search for outliers in files whose names
#                   match the regular expression
# file_ext          File extension to read
def DetectOutliers(in_path, sampling_rate, cols, threshold, metric=np.median, expression=None, file_ext='csv'):
    
    p_deg = 1   # Degree of equation on the top of the fraction
    q_deg = 2   # Degree of equation on the bottom of the fraction
    
    # Create rational function equation
    def Rational(x, *params):
        p = params[:p_deg]
        q = params[p_deg:]
        return np.polyval(p, x) / np.polyval(q, x)
    
    outliers = {}
    
    # Convert path to absolute
    if not os.path.isabs(in_path):
        in_path = os.path.abspath(in_path) + '\\'
    
    # Get dictionary of files
    filedirs = MapFiles(in_path, file_ext=file_ext, expression=expression)
    
    # Iterate over detected files
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data = pd.read_csv(filedirs[file])
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols.remove('Time')
            
            # Iterate over columns
            for i in range(len(cols)):
                col = cols[i]
                psd = nk.signal_psd(data[col], sampling_rate=sampling_rate)
                
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
                    outliers[file] = filedirs[file]
                
    return outliers

#
# =============================================================================
#

# Creates plots using a list of outlier file locations, saves
# the plots to out_path
def PlotOutliers(outliers, out_path, sampling_rate):
    print('Plotting outliers...')
    
    # Create out_path file location if it does not exist
    os.makedirs(out_path, exist_ok=True)
    
    # Plot outliers
    for file in outliers:
        # Get data
        path = file
        data = pd.read_csv(path)
        
        # Prepare PSD graphs
        psd_zyg = nk.signal_psd(data['EMG_zyg'], sampling_rate=sampling_rate)
        psd_cor = nk.signal_psd(data['EMG_cor'], sampling_rate=sampling_rate)
        psd_zyg = ZoomIn(psd_zyg, 20, 450)
        psd_cor = ZoomIn(psd_cor, 20, 450)
        
        # Create plots
        fig, axs = plt.subplots(1, 2, figsize=(15,15))
        axs[0].plot(psd_zyg['Frequency'], psd_zyg['Power'])
        axs[0].set_yscale('log')
        axs[1].plot(psd_cor['Frequency'], psd_cor['Power'])
        axs[1].set_yscale('log')
        
        
        # Label plots
        axs[0].set_title('EMG_zyg')
        axs[0].set_ylabel('Power (mV^2/Hz)')
        axs[0].set_xlabel('Frequency (Hz)')
        axs[1].set_title('EMG_cor')
        axs[1].set_xlabel('Frequency (Hz)')
        fig.suptitle(file[-12:-4])
        
        # Save plots
        fig.savefig(out_path + file[-12:-4] + '.jpg')
    
    print('Done.')
    return

#
# =============================================================================
#

if __name__ == '__main__':
    
    raw_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/01_Raw/'
    notch_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/02_Notch/'
    notch_s_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/02_Notch_Special/'
    bandpass_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/03_Bandpass/'
    smooth_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/04_Smooth/'
    feature_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/05_Feature/'
    plot_path = 'C:/Users/willi/Documents/UOIT/UOIT-Thesis/Data/00_Plot/'
    
    sampling_rate = 2000
    
    outliers = DetectOutliers(notch_path, sampling_rate, ['EMG_zyg', 'EMG_cor'], 15)
    
    print(outliers)