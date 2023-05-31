import scipy.signal
import pandas as pd
import os
import re



# Apply a single notch filter to input data
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
def filterSignals(in_path, out_path, sampling_rate, Hzs, Qs, special_cases=None):

    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('^Raw_PID_[0-9]{2}-[0-9]{2}$', raw):
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
                        data['EMG_zyg'] = applyNotchFilter(data['EMG_zyg'], Hzs[i], Qs[i], sampling_rate)
                        data['EMG_cor'] = applyNotchFilter(data['EMG_cor'], Hzs[i], Qs[i], sampling_rate)
                    
                    # Apply 'special cases' notch filters
                    if special_cases is not None:
                        if person in special_cases.keys():
                            (p_Hzs, p_Qs) = special_cases[person]
                            data = applyNotchFilters(data, 'EMG_zyg', p_Hzs, p_Qs, sampling_rate)
                            data = applyNotchFilters(data, 'EMG_cor', p_Hzs, p_Qs, sampling_rate)
                    
                    # Save results
                    os.makedirs(out_person, exist_ok=True)    # Create subirectories if they do not exist
                    data.to_csv(out_file)                     # Save output
    
    print("Done.")
    return



if __name__ == '__main__':
    
    # The folders listed in in_data and out_data must exist before
    # running the script, and should not have any subdirectories.
    # The output will be generated in the
    # out_data (output) folder listed, with the same file format
    # contained in the in_data (input) folder
    
    in_data = 'Data/RawData/'       # Input data folder
    out_data = 'Data/CleanData/'    # Output data folder
    sampling_rate = 2000            # Sampling rate
    
    # The Hzs and Qs values can be adjusted to change the filters
    # that are applied to the data
    
    Hzs = [50, 150, 250, 350, 450, 550, 650, 750, 850, 950]
    Qs =  [ 5,  25,  25,  25,  25,  25,  25,  25,  25,  25]
    
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
    
    filterSignals(in_data, out_data, sampling_rate, Hzs, Qs, special_cases)