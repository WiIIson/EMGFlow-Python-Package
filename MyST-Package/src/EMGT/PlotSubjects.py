import neurokit2 as nk
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import random
from tqdm import tqdm

from SignalFilterer import ConvertMapFiles

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

# NOTE: Make this plot both the PSD **AND** signal


# Plot PSD of provided columns in the data
#
# in_path           Filepath for data to plot
# out_path          Output for plots
# sampling_rate     Sampling rate of EMG data
# cols              Columns to plot
# p                 Set to a percentage to introduce random sampling
#                   of files
# expression        If left none, will plot from all samples, but if set,
#                   will only plot from files whose names match the
#                   regular expression
# file_ext          File extension to read
def PlotSpectrum(in_path, out_path, sampling_rate, cols=None, p=None, expression=None, file_ext='csv'):
    
    # Convert out path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path) + '\\'
    
    filedirs = ConvertMapFiles(in_path, file_ext=file_ext, expression=expression)
    
    # Make plots
    for file in tqdm(filedirs):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Randomly create signal plots if requested
            if (p is not None) and (random.random() < p):
                
                # Read file
                data = pd.read_csv(filedirs[file])
                
                # If no columns selected, apply filter to all columns except time
                if cols is None:
                    cols = list(data.columns)
                    cols.remove('Time')
                
                # Create plot
                fig, axs = plt.subplots(1, len(cols), figsize=(15*len(cols),15))
                
                # Plot each column
                for i in range(len(cols)):
                    col = cols[i]
                    psd = nk.signal_psd(data[col], sampling_rate=sampling_rate)
                    axs[i].plot(psd['Frequency'], psd['Power'])
                    axs[i].set_ylabel('Power magnitude')
                    axs[i].set_xlabel('Frequency')
                    axs[i].set_title(col)
                
                # Set title and save figure
                fig.suptitle(file + ' Power Spectrum Density')
                fig.savefig(out_path + file[:-len(file_ext)] + 'jpg')
    return

#
# =============================================================================
#

# Compare the PSDs of two stages of processing
#
# in_path1          Filepath for first data folder
# in_path2          Filepath for second data folder
# out_path          Output for plots
# sampling_rate     Sampling rate of EMG data
# cols              Columns to plot
# expression        If left none, will plot from all samples, but if set,
#                   will only plot from files whose names match the
#                   regular expression
# file_ext          File extension to read
def PlotCompareSignals(in_path1, in_path2, out_path, sampling_rate, cols=None, expression=None, file_ext='csv'):
    
    # Convert out path to absolute
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path) + '\\'
    
    # Get dictionary of file locations
    filedirs1 = ConvertMapFiles(in_path1, file_ext=file_ext, expression=expression)
    filedirs2 = ConvertMapFiles(in_path2, file_ext=file_ext, expression=expression)
    
    # Make plots
    for file in tqdm(filedirs1):
        if (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data1 = pd.read_csv(filedirs1[file])
            data2 = pd.read_csv(filedirs2[file])
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data1.columns)
                cols.remove('Time')
            
            # Create plot
            fig, axs = plt.subplots(2, len(cols), figsize=(15*len(cols),30))
            
            # Plot each column
            for i in range(len(cols)):
                col = cols[i]
                
                psd1 = nk.signal_psd(data1[col], sampling_rate=sampling_rate)
                axs[0,i].plot(psd1['Frequency'], psd1['Power'])
                axs[0,i].set_ylabel('Power magnitude')
                axs[0,i].set_title(col)
                
                psd2 = nk.signal_psd(data2[col], sampling_rate=sampling_rate)
                axs[1,i].plot(psd2['Frequency'], psd2['Power'])
                axs[1,i].set_ylabel('Power magnitude')
                axs[1,i].set_xlabel('Frequency')
            
            # Set title and save figure
            fig.suptitle(file + ' Power Spectrum Density')
            fig.savefig(out_path + file[:-len(file_ext)] + 'jpg')
    
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
    
    #PlotSpectrumSample(raw_path, plot_path, sampling_rate, 0.1)
    PlotCompareSignals(raw_path, notch_path, plot_path, sampling_rate)