import neurokit2 as nk
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import random

from SignalFilterer import ApplyNotchFilters

import warnings
warnings.filterwarnings('ignore')

#
# =============================================================================
#

# A collection of functions for plotting subject data

#
# =============================================================================
#

# Zooms in on a set frequency range in a PSD plot
#
# data  PSD data to zoom in on
# a     Lower frequency range
# b     Upper frequency range
def ZoomIn(data, a, b):
    data = data[data['Frequency'] >= a]
    data = data[data['Frequency'] <= b]
    return data

#
# =============================================================================
#

def PlotInspectSignal(data, col, sampling_rate):
    fig, axs = plt.subplots(1, 2, figsize=(15*2,15))

    axs[0].plot(data['Time'], data[col])
    axs[0].set_title(col + ' - Clean')
    axs[0].set_ylabel('Voltage (mV)')
    axs[0].set_xlabel('Time (s)')

    psd_col = nk.signal_psd(data[col], sampling_rate=sampling_rate, normalize=False)

    axs[1].plot(psd_col['Frequency'], psd_col['Power'])
    axs[1].set_title(col + ' - PSD')
    axs[1].set_ylabel('Voltage (mV)')
    axs[1].set_xlabel('Frequency (Hz)')

    fig.suptitle('Inspection of ' + col)
    plt.show()
    return

#
# =============================================================================
#

# Plot PSD of data for 2 random samples from each subject before and after
# applying specified filters to the data
#
# in_data           Filepath for data folder
# col               Column of PSD data to plot (EMG_Zyg, EMG_Cor, etc.)
# out_data          Filepath for plot output
# sampling_rate     Sampling rate of EMG data
# Hzs               Frequencies of filters to apply to data
# Qs                Q-factors of filters to apply to data
# special_cases     Special case filters (optional)
#
# special_cases = {
#   "subjectNumber1": ([Hz1, Hz2, ...], [Q1, Q2, ...]),
#   "subjectNumber2": ([Hz1, Hz2, ...], [Q1, Q2, ...]),
#   ...
# }
def PlotSampleSubject(in_data, col, out_data, sampling_rate, Hzs, Qs, special_cases=None):
    
    # Create output folder if it does not exist already
    os.makedirs(out_data, exist_ok=True)
    
    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('^Raw_PID_[0-9]{2}-[0-9]{2}$', raw):
            in_raw = in_data + raw + '/'
            
            # Iterate through each person folder
            for person in os.listdir(in_raw):
                print('Creating plots for subject', person, '...')
                in_person = in_raw + person + '/'
                    
                # Get data from 2 random files
                [file1, file2] = random.sample(os.listdir(in_person), 2)
                data1 = pd.read_csv(in_person + file1)
                data2 = pd.read_csv(in_person + file2)
                
                # Create subplots
                fig, axs = plt.subplots(2, 2, figsize=(15,15))
                
                # Plot 'before' PSD graphs
                psd1 = nk.signal_psd(data1[col], sampling_rate=sampling_rate)
                psd2 = nk.signal_psd(data2[col], sampling_rate=sampling_rate)
                psd1 = ZoomIn(psd1, 20, 450)
                psd2 = ZoomIn(psd2, 20, 450)
                axs[0,0].plot(psd1['Frequency'], psd1['Power'])
                axs[1,0].plot(psd2['Frequency'], psd2['Power'])
                
                # Apply universal notch filters
                data1 = ApplyNotchFilters(data1, col, Hzs, Qs, sampling_rate)
                data2 = ApplyNotchFilters(data2, col, Hzs, Qs, sampling_rate)
                
                # Apply 'special cases' notch filters
                if special_cases is not None:
                    if person in special_cases.keys():
                        print("\tApplying special cases ...")
                        (p_Hzs, p_Qs) = special_cases[person]
                        data1 = ApplyNotchFilters(data1, col, p_Hzs, p_Qs, sampling_rate)
                        data2 = ApplyNotchFilters(data2, col, p_Hzs, p_Qs, sampling_rate)
                    
                # Plot 'after' PSD graphs
                psd1 = nk.signal_psd(data1[col], sampling_rate=sampling_rate)
                psd2 = nk.signal_psd(data2[col], sampling_rate=sampling_rate)
                psd1 = ZoomIn(psd1, 20, 450)
                psd2 = ZoomIn(psd2, 20, 450)
                axs[0,1].plot(psd1['Frequency'], psd1['Power'])
                axs[1,1].plot(psd2['Frequency'], psd2['Power'])
                
                
                # Add labels to plots
                fig.suptitle('Subject ' + person + ' ' + col)
                axs[0,0].set_title('Before')
                axs[0,1].set_title('After')
                axs[0,0].set_ylabel(file1)
                axs[1,0].set_ylabel(file2)
                
                # Export figure as JPG
                fig.savefig(out_data + person + '_' + col + '_plot.jpg')

    print("Done.")
    return

#
# =============================================================================
#

# Plot PSD of EMG data for specified subjects before and after applying
# specified filters to the data
#
# in_data           Filepath for data folder
# out_data          Filepath for plot output
# sampling_rate     Sampling rate of EMG data
# Hzs               Frequencies to apply notch filters to
# Qs                Q-factors of notch filters
# subjects          List of subjects to generate plots for
# special_cases     Special case filters (optional)
#
# NOTE: In [subjects], the subject number should be of the form 01, 02, ... 51
def PlotCompareSubject(in_data, out_data, sampling_rate, Hzs, Qs, subjects, special_cases=None):
    
    # Create output folder if it does not exist already
    os.makedirs(out_data, exist_ok=True)
        
    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('PID_[0-9]{2}-[0-9]{2}$', raw):
            in_raw = in_data + raw + '/'
            
            # Iterate through each person folder
            for person in os.listdir(in_raw):
                # Check if the person is one of the people
                # specified
                if person in subjects:
                    in_person = in_raw + person + '/'
                    
                    # Iterate through each phsiological data file
                    for file in os.listdir(in_person):
                        print('Plotting', file, '...')
                        in_file = in_person + file
                        
                        # Get data
                        data = pd.read_csv(in_file)
                        
                        # Create subplots
                        fig, axs = plt.subplots(2, 2, figsize=(15*2,15))
                        
                        # Plot 'before' PSD graphs
                        psd_zyg = nk.signal_psd(data['EMG_zyg'], sampling_rate=sampling_rate)
                        psd_cor = nk.signal_psd(data['EMG_cor'], sampling_rate=sampling_rate)
                        psd_zyg = ZoomIn(psd_zyg, 20, 450)
                        psd_cor = ZoomIn(psd_cor, 20, 450)
                        axs[0,0].plot(psd_zyg['Frequency'], psd_zyg['Power'])
                        axs[1,0].plot(psd_cor['Frequency'], psd_cor['Power'])
                        
                        # Apply notch filters
                        data = ApplyNotchFilters(data, 'EMG_zyg', Hzs, Qs, sampling_rate)
                        data = ApplyNotchFilters(data, 'EMG_cor', Hzs, Qs, sampling_rate)
                        
                        # Apply 'special cases' notch filters
                        if special_cases is not None:
                            if person in special_cases.keys():
                                (p_Hzs, p_Qs) = special_cases[person]
                                data = ApplyNotchFilters(data, 'EMG_zyg', p_Hzs, p_Qs, sampling_rate)
                                data = ApplyNotchFilters(data, 'EMG_cor', p_Hzs, p_Qs, sampling_rate)
                        
                        # Plot 'after' PSD graphs
                        psd_zyg = nk.signal_psd(data['EMG_zyg'], sampling_rate=sampling_rate)
                        psd_cor = nk.signal_psd(data['EMG_cor'], sampling_rate=sampling_rate)
                        psd_zyg = ZoomIn(psd_zyg, 20, 450)
                        psd_cor = ZoomIn(psd_cor, 20, 450)
                        axs[0,1].plot(psd_zyg['Frequency'], psd_zyg['Power'])
                        axs[1,1].plot(psd_cor['Frequency'], psd_cor['Power'])
                        
                        # Add labels to plots
                        fig.suptitle('Subject ' + person + ': ' + file)
                        axs[0,0].set_title('Before')
                        axs[0,1].set_title('After')
                        axs[0,0].set_ylabel('EMG_zyg')
                        axs[1,0].set_ylabel('EMG_cor')
                        
                        # Export figure as JPG
                        fig.savefig(out_data + file + '.jpg')
                        
    print("Done.")
    return

#
# =============================================================================
#

# Plot PSD of EMG for every subject in the dataset
#
# in_data           Filepath for data folder
# out_data          Filepath for plot output
# sampling_rate     Sampling rate of EMG data
# zoom              If the graph should be zoomed in to the 20-450 Hz range
def PlotAllSubject(in_data, out_data, sampling_rate, zoom=True):
    
    # Create output folder if it does not exist already
    os.makedirs(out_data, exist_ok=True)
        
    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('PID_[0-9]{2}-[0-9]{2}$', raw):
            in_raw = in_data + raw + '/'
            
            # Iterate through each person folder
            for person in os.listdir(in_raw):
                in_person = in_raw + person + '/'
                
                # Iterate through each phsiological data file
                for file in os.listdir(in_person):
                    print('Plotting', file, '...')
                    in_file = in_person + file
                    
                    # Get data
                    data = pd.read_csv(in_file)
                    
                    # Create graphs
                    psd_zyg = nk.signal_psd(data['EMG_zyg'], sampling_rate=sampling_rate)
                    psd_cor = nk.signal_psd(data['EMG_cor'], sampling_rate=sampling_rate)
                    if zoom == True:
                        psd_zyg = ZoomIn(psd_zyg, 20, 450)
                        psd_cor = ZoomIn(psd_cor, 20, 450)
                    
                    # Create plots
                    fig, axs = plt.subplots(1, 2, figsize=(15*2,15))
                    axs[0].plot(psd_zyg['Frequency'], psd_zyg['Power'])
                    axs[1].plot(psd_cor['Frequency'], psd_cor['Power'])
                    
                    # Create labels
                    axs[0].set_title('EMG_zyg')
                    axs[0].set_ylabel('Power (mV^2/Hz)')
                    axs[0].set_xlabel('Frequency (Hz)')
                    axs[1].set_title('EMG_cor')
                    axs[1].set_ylabel('Power (mV^2/Hz)')
                    axs[1].set_xlabel('Frequency (Hz)')
                    
                    axs[0].set_ylim([0,0.2])
                    axs[1].set_ylim([0,0.2])
                    
                    fig.suptitle('Subject: ' + person + ', File: ' + file)
                    fig.savefig(out_data + file + '_plot.jpg')
    
    print('Done.')
    return

#
# =============================================================================
#
    
if __name__ == '__main__':
    
    in_data = 'Data/Clean-Data/'
    out_data = 'Plots/CleanSubjectPlots/'
    sampling_rate = 2000
    Hzs = [50, 150, 250, 350, 400, 450, 550, 650, 750, 850, 950]
    Qs  = [ 5,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]
    subjects = ('08', '11')
    
    # Special filtering for subjects 8 and 11
    special_cases = {
        # subjectNum: (Hzs, Qs),
        "08": ([50, 100, 117, 150, 183, 200, 217, 250, 283, 317, 350, 383, 417],
               [ 1,  75, 125, 125, 100,  25,  25,  25,  50,  10,  25,  25,  25]),
        "11": ([317],
               [ 50])
    }
    
    special_cases2 = {
        # subjectNum: (Hzs, Qs),
        "08": ([50, 317],
               [ 1,  10]),
        "11": ([317],
               [ 50])
    }
    
    #PlotCompareSubject(in_data, out_data, sampling_rate, Hzs, Qs, subjects)
    
    PlotAllSubject(in_data, out_data, sampling_rate, zoom=False)