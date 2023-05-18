import neurokit2 as nk
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import random

from SignalFilterer import applyNotchFilters
    


# Zooms in on a set frequency range in some data
def zoomIn(data, a, b):
    data = data[data['Frequency'] >= a]
    data = data[data['Frequency'] <= b]
    return data



# Creates a 'before' and 'after' plot of the PSD graph
# for each subject using 2 random phsiology files

# The special_cases parameter allows special case filters to
# be applied to specific subjects based on subject number.
# 'special_cases' is a dictionary where the subject number
# is the key, with the value being a tuple of two lists:
# the frequencies and Q-factors of the notch filters to be
# applied to them
#
# special_cases = {
#   "subjectNumber1": ([Hz1, Hz2, ...], [Q1, Q2, ...]),
#   "subjectNumber2": ([Hz1, Hz2, ...], [Q1, Q2, ...]),
#   ...
# }
#
# Note: Make sure that subjectNumber follows the convention
#       01, 02, 03, ... 10, ... 99
def plotSpectrums(in_data, col, out_data, sampling_rate, Hzs, Qs, special_cases=None):
    
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
                psd1 = zoomIn(psd1, 20, 450)
                psd2 = zoomIn(psd2, 20, 450)
                axs[0,0].plot(psd1['Frequency'], psd1['Power'])
                axs[1,0].plot(psd2['Frequency'], psd2['Power'])
                
                # Apply universal notch filters
                data1 = applyNotchFilters(data1, col, Hzs, Qs, sampling_rate)
                data2 = applyNotchFilters(data2, col, Hzs, Qs, sampling_rate)
                
                # Apply 'special cases' notch filters
                if special_cases is not None:
                    if person in special_cases.keys():
                        print("\tApplying special cases ...")
                        (p_Hzs, p_Qs) = special_cases[person]
                        data1 = applyNotchFilters(data1, col, p_Hzs, p_Qs, sampling_rate)
                        data2 = applyNotchFilters(data2, col, p_Hzs, p_Qs, sampling_rate)
                    
                # Plot 'after' PSD graphs
                psd1 = nk.signal_psd(data1[col], sampling_rate=sampling_rate)
                psd2 = nk.signal_psd(data2[col], sampling_rate=sampling_rate)
                psd1 = zoomIn(psd1, 20, 450)
                psd2 = zoomIn(psd2, 20, 450)
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
    
    

if __name__ == '__main__':

    in_data = 'Data/'
    col = 'EMG_zyg'
    out_data = 'Plots/SubjectPSDsZyg/'
    sampling_rate = 2000
    Hzs = [50, 150, 250, 350, 400, 450, 550, 650, 750, 850, 950]
    #Qs =  [ 1,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]
    Qs =  [5,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]
    
    special_cases = {
        # subjectNum: (Hzs, Qs),
        "08": ([317],[25]),
        "11": ([317],[25])
    }
    
    plotSpectrums(in_data, col, out_data, sampling_rate, Hzs, Qs, special_cases)