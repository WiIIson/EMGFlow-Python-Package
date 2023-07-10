import scipy
import pandas as pd
import numpy as np
import os
import re
import cv2

#
# =============================================================================
#

# Apply a single notch filter to input data
#
# data              Data notch filter is being applied to
# freq              Frequency to apply notch filter to
# Q                 Q-factor of notch filter
# sampling_rate     Sampling rate of data
def ApplyNotchFilter(data, freq, Q, sampling_rate):
    
    # Normalize filtering frequency
    nyq_freq = sampling_rate / 2
    norm_freq = freq / nyq_freq
    
    # Use scipy notch filter using normalized frequency
    b, a = scipy.signal.iirnotch(norm_freq, Q)
    filtered_data = scipy.signal.lfilter(b, a, data)
    
    return filtered_data

#
# =============================================================================
#

# Applies a sequence of notch filters for given frequencies and Q-factors to a
# column of the provided data
#
# data              Data notch filter is being applied to
# col               Column of [data] notch filter is being applied to
# freq              Frequency to apply notch filter to
# Q                 Q-factor of notch filter
# sampling_rate     Sampling rate of data   
def ApplyNotchFilters(data, col, Hzs, Qs, sampling_rate):
    
    data = data.copy()
    
    if len(Hzs) == len(Qs):
        for i in range(len(Qs)):
            data[col] = ApplyNotchFilter(data[col], Hzs[i], Qs[i], sampling_rate)
        return data
    else:
        raise Exception("Error: Provided", len(Hzs), "frequencies and", len(Qs), "Q-factors.")

#
# =============================================================================
#

# Applies notch filters to provided raw data and saves resulting cleaned data
#
# in_path           Filepath for raw data folder
# out_path          Filepath for clean data folder
# sampling_rate     Sampling rate of files
# Hzs               Frequencies to apply notch filters to
# Qs                Q-factors of notch filters
# special_cases     Additional optional special case notch filters
def NotchFilterSignals(in_path, out_path, sampling_rate, Hzs, Qs, special_cases=None):    

    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('PID_[0-9]{2}-[0-9]{2}$', raw):
            in_raw = in_path + raw + '/'
            out_raw = out_path + raw + '/'
            
            # Iterate through each person folder
            for person in os.listdir(in_raw):
                print("Writing files for subject", person, "...")
                in_person = in_raw + person + '/'
                out_person = out_raw + person
                
                # Iterate through each phsiological data file
                for file in os.listdir(in_person):
                    in_file = in_person + file
                    out_file = out_person + '/' + file
                    
                    # Get data and apply notch filter
                    data = pd.read_csv(in_file)
                    for i in range(len(Qs)):
                        data['EMG_zyg'] = ApplyNotchFilter(data['EMG_zyg'], Hzs[i], Qs[i], sampling_rate)
                        data['EMG_cor'] = ApplyNotchFilter(data['EMG_cor'], Hzs[i], Qs[i], sampling_rate)
                    
                    # Apply 'special cases' notch filters
                    if special_cases is not None:
                        if person in special_cases.keys():
                            (p_Hzs, p_Qs) = special_cases[person]
                            data = ApplyNotchFilters(data, 'EMG_zyg', p_Hzs, p_Qs, sampling_rate)
                            data = ApplyNotchFilters(data, 'EMG_cor', p_Hzs, p_Qs, sampling_rate)
                    
                    # Save results
                    os.makedirs(out_person, exist_ok=True)    # Create subirectories if they do not exist
                    data.to_csv(out_file, index=False)        # Save output
    
    print("Done.")
    return

#
# =============================================================================
#

# Apply a bandpass filter to data given the upper and lower frequency
#
# data              Data to apply the bandpass filter to
# col               Column of [data] to apply the bandpass filter to
# high              Upper frequency of the bandpass filter
# low               Lower frequency of the bandpass filter
# sampling_rate     Sampling rate of [data]
def ApplyBandpassFilter(data, col, low, high, sampling_rate):
    data = data.copy()
    # Here, the "5" is the order of the butterworth filter
    # (how quickly the signal is cut off)
    b, a = scipy.signal.butter(5, [low, high], fs=sampling_rate, btype='band')
    data[col] = scipy.signal.lfilter(b, a, data[col])
    return data

#
# =============================================================================
#

# Apply a full wave rectifier to data
#
# data  Data to apply the FWR to
# col   Column of [data] to apply the FWR to
def ApplyFWR(data, col):
    data = data.copy()
    data[col] = np.abs(data[col])
    return data

#
# =============================================================================
#

# Apply a boxcar smoothing filter to data given a window size
#
# Performs a rolling average using the window size
#
# data          Data to apply the filter to
# col           Column of [data] to apply the filter to
# window_size   Size of the window
def ApplyBoxcarSmooth(data, col, window_size):
    data = data.copy()
    window = np.ones(window_size) / float(window_size)
    data[col] = np.convolve(data[col], window, 'same')
    return data

#
# =============================================================================
#

# Apply an RMS smoothing filter to data given a window size
#
# Squares the data, performs a rolling average using the
# window size, then takes the root
#
# data          Data to apply the filter to
# col           Column of [data] to apply the filter to
# window_size   Size of the window
def ApplyRMSSmooth(data, col, window_size):
    data = data.copy()
    data[col] = np.power(data[col], 2)
    window = np.ones(window_size) / float(window_size)
    data[col] = np.sqrt(np.convolve(data[col], window, 'same'))
    return data

#
# =============================================================================
#

# Apply a loess smoothing filter to data
#
# Performs a rolling average average using the window size,
# weighted using a Gaussian distribution of a given sigma
#
# data
# col
# window_size
# sigma
def ApplyLoessSmooth(data, col, window_size, sigma=1):
    data = data.copy()
    window = cv2.getGaussianKernel(window_size, sigma).transpose()[0]
    data[col] = np.convolve(data[col], window, 'same')
    return data

#
# =============================================================================
#

if __name__ == '__main__':
    
    # The folders listed in in_data and out_data must exist before
    # running the script, and should not have any subdirectories.
    # The output will be generated in the
    # out_data (output) folder listed, with the same file format
    # contained in the in_data (input) folder
    
    in_data = 'Data/Raw-Data/'       # Input data folder
    out_data = 'Data/Clean-Data/'    # Output data folder
    sampling_rate = 2000            # Sampling rate
    
    # The Hzs and Qs values can be adjusted to change the filters
    # that are applied to the data
    
    Hzs = [50, 150, 250, 350, 450, 400, 550, 650, 750, 850, 950]
    Qs =  [ 5,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]
    
    # The special cases are additional notch filters to be applied
    # only to specific subjects
    
    special_cases = {
        # subjectNum: ([Hzs ...],
        #              [ Qs ...])
        '08': ([317],
               [ 25]),
        '11': ([317],
               [ 25])
    }
    
    #NotchFilterSignals(in_data, out_data, sampling_rate, Hzs, Qs, special_cases)