import scipy.signal
import pandas as pd
import os
import re



# Apply a notch filter to input data
def applyNotchFilter(data, freq, Q, sampling_rate):
    # Normalize filtering frequency
    nyq_freq = sampling_rate / 2
    norm_freq = freq / nyq_freq
    
    # Use scipy notch filter using normalized frequency
    b, a = scipy.signal.iirnotch(norm_freq, Q)
    filtered_data = scipy.signal.lfilter(b, a, data)
    
    return filtered_data



# Applies a sequence of notch filters for given frequencies
# and Q-factors
def applyNotchFilters(data, col, Hzs, Qs, sampling_rate):
    if len(Hzs) == len(Qs):
        for i in range(len(Qs)):
            data[col] = applyNotchFilter(data[col], Hzs[i], Qs[i], sampling_rate)
        return data
    else:
        raise Exception("Error: Provided", len(Hzs), "frequencies and", len(Qs), "Q-factors.")



# Apply filters to the raw data at the given Hz (with
# corresponding Q-factor) and save the modified data
# to a new folder
def filterSignals(in_data, out_data, sampling_rate, Hzs, Qs):

    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('^Raw_PID_[0-9]{2}-[0-9]{2}$', raw):
            path2 = in_data + raw + '/'
            out2 = out_data + raw + '/'
        
            # Iterate through each person folder
            for person in os.listdir(path2):
                print("Writing files for subject", person, "...")
                path3 = path2 + person + '/'
                out3 = out2 + person
            
                # Iterate through each phsiological data file
                for file in os.listdir(path3):
                    path4 = path3 + file
                    out4 = out3 + '/' + file
                    
                    # Get data and apply notch filter
                    data = pd.read_csv(path4)
                    for i in range(len(Qs)):
                        data['EMG_zyg'] = applyNotchFilter(data['EMG_zyg'], Hzs[i], Qs[i], sampling_rate)
                        data['EMG_cor'] = applyNotchFilter(data['EMG_cor'], Hzs[i], Qs[i], sampling_rate)
                
                    # Save results
                    os.makedirs(out3, exist_ok=True)    # Create subirectories if they do not exist
                    data.to_csv(out4)                   # Save output
    
    print("Done.")



if __name__ == '__main__':
    
    # The folders listed in path1 and out1 must exist before
    # running the script. The output will be generated in the
    # out1 (output) folder listed, with the same file format
    # contained in the path1 (input) folder
    
    in_data = 'Data/'           # Input data folder
    out_data = 'DataOut/'       # Output data folder
    sampling_rate = 2000        # Sampling rate
    
    # The Hzs and Qs values can be adjusted to change the filters
    # that are applied to the data
    
    Hzs = [50, 150, 250, 350, 400, 450, 550, 650, 750, 850, 950]
    Qs =  [ 1,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]
    
    filterSignals(in_data, out_data, sampling_rate, Hzs, Qs)