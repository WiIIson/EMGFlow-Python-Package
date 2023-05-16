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
def plotSpectrums(in_data, col, out_data, sampling_rate, Hzs, Qs):
    
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
                
                # Plot 'after' PSD graphs
                data1 = applyNotchFilters(data1, col, Hzs, Qs, sampling_rate)
                data2 = applyNotchFilters(data2, col, Hzs, Qs, sampling_rate)
                psd1 = nk.signal_psd(data1[col], sampling_rate=sampling_rate)
                psd2 = nk.signal_psd(data2[col], sampling_rate=sampling_rate)
                psd1 = zoomIn(psd1, 20, 450)
                psd2 = zoomIn(psd2, 20, 450)
                axs[0,1].plot(psd1['Frequency'], psd1['Power'])
                axs[1,1].plot(psd2['Frequency'], psd2['Power'])
                
                # Add labels
                fig.suptitle('Subject ' + person + ' ' + col)
                axs[0,0].set_title('Before')
                axs[0,1].set_title('After')
                axs[0,0].set_ylabel(file1)
                axs[1,0].set_ylabel(file2)
                
                # Save figure as JPG
                fig.savefig(out_data + person + '_' + col + '_plot.jpg')

    print("Done.")
    
    

if __name__ == '__main__':

    in_data = 'Data/'
    col = 'EMG_cor'
    out_data = 'Plots/SubjectPSDsCor/'
    sampling_rate = 2000
    Hzs = [50, 150, 250, 350, 400, 450, 550, 650, 750, 850, 950]
    Qs =  [ 1,  25,  25,  25,  25,  25,  25,  25,  25,  25,  10]
    
    plotSpectrums(in_data, col, out_data, sampling_rate, Hzs, Qs)