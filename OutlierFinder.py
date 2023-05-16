import neurokit2 as nk
import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt


from SpectrumMapper import zoomIn


# Check for outliers among the filtered data at specified
# Hz values
def findOutliers(in_data, sampling_rate, Hzs, threshold, col):
    outliers = []
    
    # Iterate through each RAW folder
    for raw in os.listdir(in_data):
        if re.search('^Raw_PID_[0-9]{2}-[0-9]{2}$', raw):
            in_raw = in_data + raw + '/'
            
            # Iterate through each person folder
            for person in os.listdir(in_raw):
                print("Checking subject", person, "...")
                in_person = in_raw + person + '/'
                
                # Iterate through each phsiological data file
                for file in os.listdir(in_person):
                    in_file = in_person + file
                    
                    # Get data
                    data = pd.read_csv(in_file)
                    
                    # Make PSD
                    psd = nk.signal_psd(data[col], sampling_rate=sampling_rate)
                    
                    # Get median
                    med = np.mean(psd['Power'])
                    
                    # Find value closest to specified Hz
                    for Hz in Hzs:
                        # Filter values within 0.25 Hz of the specified value
                        sub_psd = psd[psd['Frequency'] >= Hz - 0.25]
                        sub_psd = sub_psd[sub_psd['Frequency'] <= Hz + 0.25]
                        
                        # Get largest Power value
                        max_val = max(sub_psd['Power'])
                       
                        if max_val >= threshold * med:
                            print("\tOutlier detected...")
                            outliers.append(in_file)
    
    print("Done.")
    return outliers



# Creates plots using a list of outliers
def plotOutliers(outliers, out_path, col, sampling_rate):
    # Create out_path file location if it does not exist
    os.makedirs(out_path, exist_ok=True)
    
    for file in outliers:
        path = file
        data = pd.read_csv(path)
        psd = nk.signal_psd(data[col], sampling_rate=sampling_rate)
        psd = zoomIn(psd, 20, 450)
        plt.clf()
        plt.plot(psd['Frequency'], psd['Power'])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power (mV^2/Hz)')
        plt.title(file)
        plt.savefig(out_path + file[-12:-4] + '.jpg')



if __name__ == '__main__':
    
    in_data = 'DataOut/'
    sampling_rate = 2000
    #Hzs = [ 50, 150, 250, 350, 400, 450, 550, 650, 750, 850, 950]
    Hzs = [217, 317, 417, 517, 617, 717, 817, 917]
    threshold = 5           # Threshold for an outlier
    col = 'EMG_zyg'
    
    outliers = findOutliers(in_data, sampling_rate, Hzs, threshold, col)
    
    print("The outliers are:")
    print(outliers)
    
    #out_path = 'Plots/Outliers/50s/'
    out_path = 'Plots/Outliers/17s/'
    
    plotOutliers(outliers, out_path, col, sampling_rate)