import scipy.signal
import pandas as pd
import os
import re

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

# Put bandpass filter function here 
def BandpassFilterSignals():
    return

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
    
    NotchFilterSignals(in_data, out_data, sampling_rate, Hzs, Qs, special_cases)