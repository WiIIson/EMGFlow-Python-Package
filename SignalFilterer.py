import numpy as np
import scipy.signal
import pandas as pd
import neurokit2 as nk
import os
import re

path1 = 'Data/'         # Input data folder
out1 = 'DataOut/'       # Output data folder
sampling_rate = 2000    # Sampling rate

Hzs = [50, 150, 250, 350, 400, 450, 550, 650, 750, 850, 950]
Qs =  [ 1,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]

# Apply a notch filter to input data
def apply_notch_filter(data, freq, Q, sampling_rate):
    # Normalize filtering frequency
    nyq_freq = sampling_rate / 2
    norm_freq = freq / nyq_freq
    
    # Use scipy notch filter using normalized frequency
    b, a = scipy.signal.iirnotch(norm_freq, Q)
    filtered_data = scipy.signal.lfilter(b, a, data)
    
    return filtered_data



# Iterate through each RAW folder
for raw in os.listdir(path1):
    if re.search('^Raw_PID_[0-9]{2}-[0-9]{2}$', raw):
        path2 = path1 + raw + '/'
        out2 = out1 + raw + '/'
        
        # Iterate through each person folder
        for person in os.listdir(path2):
            path3 = path2 + person + '/'
            out3 = out2 + person
            
            # Iterate through each phsiological data file
            for file in os.listdir(path3):
                path4 = path3 + file
                out4 = out3 + '/' + file
                
                # Get data and apply notch filter
                data = pd.read_csv(path4)
                for i in range(len(Qs)):
                    data['EMG_zyg'] = apply_notch_filter(data['EMG_zyg'], Hzs[i], Qs[i], sampling_rate)
                    data['EMG_cor'] = apply_notch_filter(data['EMG_cor'], Hzs[i], Qs[i], sampling_rate)
                
                # Save results
                os.makedirs(out3, exist_ok=True)  # Create subirectories if they do not exist
                data.to_csv(out4)               # Save output
                
                print("Written", out4)