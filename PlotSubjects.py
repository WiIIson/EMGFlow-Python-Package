import neurokit2 as nk
import pandas as pd
import os
import re
import matplotlib.pyplot as plt

from SignalFilterer import applyNotchFilters
from SpectrumMapper import zoomIn



# Plots all physiological files from the subjects listed
# before and after applying notch filters in the EMG_zyg
# and EMG_cor columns
def plotSubjects(in_data, out_data, sampling_rate, Hzs, Qs, subjects, special_cases=None):
    
    # Create output folder if it does not exist already
    os.makedirs(out_data, exist_ok=True)
        
    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('^Raw_PID_[0-9]{2}-[0-9]{2}$', raw):
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
                        fig, axs = plt.subplots(2, 2, figsize=(15,15))
                        
                        # Plot 'before' PSD graphs
                        psd_zyg = nk.signal_psd(data['EMG_zyg'], sampling_rate=sampling_rate)
                        psd_cor = nk.signal_psd(data['EMG_cor'], sampling_rate=sampling_rate)
                        psd_zyg = zoomIn(psd_zyg, 20, 450)
                        psd_cor = zoomIn(psd_cor, 20, 450)
                        axs[0,0].plot(psd_zyg['Frequency'], psd_zyg['Power'])
                        axs[1,0].plot(psd_cor['Frequency'], psd_cor['Power'])
                        
                        # Apply notch filters
                        data = applyNotchFilters(data, 'EMG_zyg', Hzs, Qs, sampling_rate)
                        data = applyNotchFilters(data, 'EMG_cor', Hzs, Qs, sampling_rate)
                        
                        # Apply 'special cases' notch filters
                        if special_cases is not None:
                            if person in special_cases.keys():
                                (p_Hzs, p_Qs) = special_cases[person]
                                data = applyNotchFilters(data, 'EMG_zyg', p_Hzs, p_Qs, sampling_rate)
                                data = applyNotchFilters(data, 'EMG_cor', p_Hzs, p_Qs, sampling_rate)
                        
                        # Plot 'after' PSD graphs
                        psd_zyg = nk.signal_psd(data['EMG_zyg'], sampling_rate=sampling_rate)
                        psd_cor = nk.signal_psd(data['EMG_cor'], sampling_rate=sampling_rate)
                        psd_zyg = zoomIn(psd_zyg, 20, 450)
                        psd_cor = zoomIn(psd_cor, 20, 450)
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
    
    
    
if __name__ == '__main__':
    
    in_data = 'Data/'
    out_data = 'Plots/SubjectExplore/'
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
    
    plotSubjects(in_data, out_data, sampling_rate, Hzs, Qs, subjects)