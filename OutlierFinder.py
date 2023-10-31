import neurokit2 as nk
import pandas as pd
import numpy as np
import scipy.optimize
import os
import re
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

from PlotSubjects import ZoomIn

import warnings
warnings.filterwarnings('ignore')

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
    
    in_data = 'Data/Clean-Data/'
    sampling_rate = 2000
    threshold = 15
    
    outliers = FindOutliers2(in_data, sampling_rate, threshold)
    
    print('Outliers found:', len(outliers))
    
    #PlotOutliers(outliers, out_path, sampling_rate)