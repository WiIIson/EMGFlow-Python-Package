import scipy
import pandas as pd
import numpy as np
import neurokit2 as nk
import os
import re
import cv2
from tqdm import tqdm

#
# =============================================================================
#

# A collection of functions for filtering signals.
# This collection contains the main pipeline of the work.

#
# =============================================================================
#

# Raises an error if provided object is not a "Signal"
#
# A "Signal" should be a pandas dataframe with a column
# named "Time", and additional columns for the recordings
def CheckSignal(Signal):
    if (Signal != pd.DataFrame):
        # Signal is not a dataframe
        raise Exception('Provided signal is not a dataframe')
    elif 'Time' not in Signal:
        # Signal does not have a time column
        raise Exception('Provided signal does not have a "Time" column')

#
# =============================================================================
#

# Applies a sequence of notch filters for given frequencies and Q-factors to a
# column of the provided data
#
# data              Data notch filter is being applied to
# col               Column of [data] notch filter is being applied to
# notch_vals        Notch filter parameters: (Hz, Q) tuples, Hz = frequency,
#                   Q = Q-score
# sampling_rate     Sampling rate of data
def ApplyNotchFilters(Signal, col, sampling_rate, notch_vals):
    
    # Function that applies a singular notch filter
    def ApplyNotchFilter(Signal, col, sampling_rate, notch):
        
        Signal = Signal.copy()
        
        (Hz, Q) = notch
        
        # Normalize filtering frequency
        nyq_freq = sampling_rate / 2
        norm_Hz = Hz / nyq_freq
        
        # Use scipy notch filter using normalized frequency
        b, a = scipy.signal.iirnotch(norm_Hz, Q)
        Signal_col = scipy.signal.lfilter(b, a, Signal[col])
        
        return Signal_col
    
    Signal = Signal.copy()
    
    # Applies ApplyNotchFilter for every notch_val tuple
    for i in range(len(notch_vals)):
        Signal[col] = ApplyNotchFilter(Signal, col, sampling_rate, notch_vals[i])
    return Signal

#
# =============================================================================
#

# Applies notch filters to provided raw data and saves resulting
# notch-filtered data
#
# in_path           Filepath for raw data folder
# out_path          Filepath for notch-filtered data folder
# sampling_rate     Sampling rate of files
# notch_vals        Notch filter parameters: (Hz, Q) tuples, Hz = frequency,
#                   Q = Q-score
# special_cases     Additional optional special case notch filters
def PADS_NotchFilterSignals(in_path, out_path, sampling_rate, notch_vals, special_cases=None):    

    # Iterate through each RAW folder
    for raw in os.listdir(in_path):
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
                    data = ApplyNotchFilters(data, 'EMG_zyg', sampling_rate, notch_vals)
                    data = ApplyNotchFilters(data, 'EMG_cor', sampling_rate, notch_vals)
                    
                    # Apply 'special cases' notch filters
                    if special_cases is not None:
                        if person in special_cases.keys():
                            p_notch_vals = special_cases[person]
                            data = ApplyNotchFilters(data, 'EMG_zyg', sampling_rate, p_notch_vals)
                            data = ApplyNotchFilters(data, 'EMG_cor', sampling_rate, p_notch_vals)
                    
                    # Save results
                    os.makedirs(out_person, exist_ok=True)    # Create subirectories if they do not exist
                    data.to_csv(out_file, index=False)        # Save output
    
    print('Done.')
    return

#
# =============================================================================
#

# Apply notch filters to all signals contained within a
# folder for specified columns and 
#
# in_path           Path to folder containing raw data
# out_path          Path to folder for output
# sampling_rate     Sampling rate of data
# notch             (Hz, Q) tuples, Hz = frequency, Q = Q-score)
# cols              Columns notch filters are applied to
# expression        Regular expression, if left none will apply notch filters
#                   to all files, but if entered, will only apply to files
#                   whose names match the pattern
def NotchFilterSignals(in_path, out_path, sampling_rate, notch, cols=None, expression=None):
    
    # Convert paths to absolute
    if not os.path.isabs(in_path):
        in_path = os.path.abspath(in_path) + '\\'
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path) + '\\'
    
    # Generates a dictionary of file names and locations
    def MapFiles(in_path, expression=expression):
        filedirs = {}
        for file in os.listdir(in_path):
            if os.path.exists(in_path + file + '\\'):
                subDir = MapFiles(in_path + file + '\\')
                filedirs.update(subDir)
            elif (file[-3:] == 'csv') and ((expression is None) or (re.match(expression, file))):
                filedirs[file] = in_path + file
        return filedirs
    
    # Get dictionary of file locations
    filedirs = MapFiles(in_path)
    
    # Apply transformations
    for file in tqdm(filedirs):
        if (file[-3:] == 'csv') and ((expression is None) or (re.match(expression, file))):
            # Read file
            data = pd.read_csv(filedirs[file])
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data.columns)
                cols.remove('Time')
            
            # Apply filter to columns
            for col in cols:
                data = ApplyNotchFilters(data, col, sampling_rate, notch)
            
            # Construct out path
            out_file = out_path + filedirs[file][len(in_path):]
            out_folder = out_file[:len(out_file) - len(file)]
            
            # Make folders and write data
            os.makedirs(out_folder, exist_ok=True)
            data.to_csv(out_file, index=False)
    
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
def ApplyBandpassFilter(data, col, sampling_rate, low, high):
    data = data.copy()
    # Here, the "5" is the order of the butterworth filter
    # (how quickly the signal is cut off)
    b, a = scipy.signal.butter(5, [low, high], fs=sampling_rate, btype='band')
    data[col] = scipy.signal.lfilter(b, a, data[col])
    return data

#
# =============================================================================
#

# Clean signals by applying a bandpass filter
#
# in_path           Filepath for notch-filtered data folder
# out_path          Filepath for clean data folder
# sampling_rate     Sampling rate of files
# low               Lower frequency limit for bandpass filter
# high              Upper frequency limit for bandpass filter
def PADS_BandpassFilterSignals(in_path, out_path, sampling_rate, low, high):    

    # Iterate through each RAW folder
    for raw in os.listdir(in_path):
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
                    
                    # Get data, apply bandpass filter and RMS cleaning
                    data = pd.read_csv(in_file)
                    data = ApplyBandpassFilter(data, 'EMG_zyg', sampling_rate, low, high)
                    data = ApplyBandpassFilter(data, 'EMG_cor', sampling_rate, low, high)
                    
                    # Save results
                    os.makedirs(out_person, exist_ok=True)    # Create subirectories if they do not exist
                    data.to_csv(out_file, index=False)        # Save output
    
    print('Done.')
    return

#
# =============================================================================
#

def BandpassFilterSignals(in_path, out_path, sampling_rate, low, high, cols=None, expression=None, quiet=False):
    
    # Convert paths to absolute
    if not os.path.isabs(in_path):
        in_path = os.path.abspath(in_path) + '\\'
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path) + '\\'
    
    # Generates a dictionary of file names and locations
    def MapFiles(in_path, expression=expression):
        filedirs = {}
        for file in os.listdir(in_path):
            if os.path.exists(in_path + file + '\\'):
                subDir = MapFiles(in_path + file + '\\')
                filedirs.update(subDir)
            elif (file[-3:] == 'csv') and ((expression is None) or (re.match(expression, file))):
                filedirs[file] = in_path + file
        return filedirs
    
    # Get dictionary of file locations
    filedirs = MapFiles(in_path)
    
    for file in os.listdir(in_path):
        
        # Handle file
        if os.path.exists(in_path + file + '/'):
            BandpassFilterSignals(in_path + file + '/', out_path + file + '/', sampling_rate, low, high)
        
        # Handle CSV
        elif file[-3:] == 'csv':
            # Apply filters to file
            data = pd.read_csv(in_path + file)
            data = ApplyBandpassFilter(data, 'EMG_zyg', sampling_rate, low, high)
            data = ApplyBandpassFilter(data, 'EMG_cor', sampling_rate, low, high)
            
            # Save results
            os.makedirs(out_path, exist_ok=True)
            data.to_csv(out_path + file, index=False)
    return

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
    # Construct kernel
    window = np.ones(window_size) / float(window_size)
    # Convolve
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
    # Square
    data[col] = np.power(data[col], 2)
    # Construct kernel
    window = np.ones(window_size) / float(window_size)
    # Convolve and square root
    data[col] = np.sqrt(np.convolve(data[col], window, 'same'))
    return data

#
# =============================================================================
#

# Apply a Gaussian smoothing filter to data
#
# Performs a rolling average average using the window size
# using a Gaussian weight
#
# data          Data to apply the filter to
# col           Column of [data] to apply the filter to
# window_size   Size of the window
# sigma         Sigma value of the Gaussian filter
def ApplyGaussianSmooth(data, col, window_size, sigma=1):
    data = data.copy()
    # Construct kernel
    window = cv2.getGaussianKernel(window_size, sigma).transpose()[0]
    # Convolve
    data[col] = np.convolve(data[col], window, 'same')
    return data

#
# =============================================================================
#

# Apply a Loess smoothing filter to data
#
# Performs a rolling average using the window size
# using a tri-cubic weight
#
# data          Data to apply the filter to
# col           Column of [data] to apply the filter to
# window_size   Size of the window
def ApplyLoessSmooth(data, col, window_size):
    data = data.copy()
    # Construct kernel
    window = np.linspace(-1,1,window_size+1,endpoint=False)[1:]
    window = np.array(list(map(lambda x: (1 - np.abs(x) ** 3) ** 3, window)))
    window = window / np.sum(window)
    # Convolve
    data[col] = np.convolve(data[col], window, 'same')
    return data

#
# =============================================================================
#

# Clean signals by applying an RMS smoothing filter
#
# in_path           Filepath for notch-filtered data folder
# out_path          Filepath for clean data folder
# sampling_rate     Sampling rate of files
# low               Lower frequency limit for bandpass filter
# high              Upper frequency limit for bandpass filter
def PADS_RMSFilterSignals(in_path, out_path, sampling_rate, window_size):    

    # Iterate through each RAW folder
    for raw in os.listdir(in_path):
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
                    
                    # Get data, apply bandpass filter and RMS cleaning
                    data = pd.read_csv(in_file)
                    data = ApplyRMSSmooth(data, 'EMG_zyg', window_size)
                    data = ApplyRMSSmooth(data, 'EMG_cor', window_size)
                    
                    # Save results
                    os.makedirs(out_person, exist_ok=True)    # Create subirectories if they do not exist
                    data.to_csv(out_file, index=False)        # Save output
    
    print('Done.')
    return

#
# =============================================================================
#

def RMSFilterSignals(in_path, out_path, sampling_rate, window_size):  
    for file in os.listdir(in_path):
        
        # Handle file
        if os.path.exists(in_path + file + '/'):
            RMSFilterSignals(in_path + file + '/', out_path + file + '/', sampling_rate, window_size)
        
        # Handle CSV
        elif file[-3:] == 'csv':
            # Apply filters to file
            data = pd.read_csv(in_path + file)
            data = ApplyRMSSmooth(data, 'EMG_zyg', window_size)
            data = ApplyRMSSmooth(data, 'EMG_cor', window_size)
            
            # Save results
            os.makedirs(out_path, exist_ok=True)
            data.to_csv(out_path + file, index=False)
    return

#
# =============================================================================
#

# Merge the perceptual data files
def MergePerceptual(in_path, out_path):
    dfs = []
    emotions = np.array([
        'Neutral',
        'Calm',
        'Happy',
        'Sad',
        'Angry',
        'Fearful',
        'Disgust'
    ])
    for perceptual in os.listdir(in_path):
        in_file = in_path + perceptual
        data = pd.read_csv(in_file)
        subject_num = perceptual[:2]
        data['PID'] = subject_num
        data = data.rename(columns={'emotion':'DV_Category','filename':'Filename', 'valence':'DV_Valence', 'arousal':'DV_Arousal'})
        data['EID'] = [int(emotion[1]) for emotion in data['Filename']]
        data['Emotion_Name'] = emotions[data['EID'] - 1]
        data['SID'] = [emotion[4] for emotion in data['Filename']]
        data['Order'] = np.linspace(1,12,12)
        data = data[['PID', 'EID', 'SID', 'Order', 'Filename', 'Emotion_Name', 'DV_Category', 'DV_Valence', 'DV_Arousal']]
        dfs.append(data)
        
    df = pd.concat(dfs)
    df.to_csv(out_path + 'Perceptual_Data.csv', index=False)
    return df

#
# =============================================================================
#

# Calculate the spectral flux of a signal
def CalcSpecFlux(Signal, col, sr, p=0.5):
    
    # Find column divider index
    div = int(len(Signal[col]) * p)
    
    # Take the PSD of each signal
    psd1 = nk.signal_psd(Signal[col][:div], sampling_rate=sr)
    psd2 = nk.signal_psd(Signal[col][div:], sampling_rate=sr)
    # Calculate the spectral flux
    flux = np.sum((psd1['Power'] - psd2['Power']) ** 2)
    return flux

#
# =============================================================================
#

# Calculate the Integrated EMG (IEMG) of a signal
def CalcIEMG(Signal, col, sr):
    IEMG = np.sum(np.abs(Signal[col]) * sr)
    return IEMG

#
# =============================================================================
#

# Calculate the Mean Absolute Value (MAV) of a signal
def CalcMAV(Signal, col):
    N = len(Signal[col])
    MAV = np.sum(np.abs(Signal[col])) / N
    return MAV

#
# =============================================================================
#

# Calculate the Modified Mean Absolute Value 1 (MMAV1) of a signal
def CalcMMAV1(Signal, col):
    N = len(Signal[col])
    vals = list(np.abs(Signal[col]))
    total = 0
    for n in range(N):
        if (0.25*N <= n) and (n <= 0.75*N):
            total += vals[n]
        else:
            total += 0.5 * vals[n]
    MMAV1 = total/N
    return MMAV1

#
# =============================================================================
#

# Calculate the Simple Square Integral (SSI) of a signal
def CalcSSI(Signal, col, sr):
    SSI = np.sum((np.abs(Signal[col]) * sr) ** 2)
    return SSI

#
# =============================================================================
#

# Calculate the Variance (VAR) of a signal
def CalcVAR(Signal, col):
    N = len(Signal[col])
    VAR = 1/(N - 1) * np.sum(Signal[col] ** 2)
    return VAR

#
# =============================================================================
#

# Calculate the V-Order of a signal
def CalcVOrder(Signal, col):
    vOrder = np.sqrt(CalcVAR(Signal, col))
    return vOrder

#
# =============================================================================
#

# Calculate the Root Mean Square (RMS) of a signal
def CalcRMS(Signal, col):
    N = len(Signal)
    RMS = np.sqrt((1/N) * np.sum(Signal[col] ** 2))
    return RMS

#
# =============================================================================
#

# Calculate the Waveform Length (WL) of a signal
def CalcWL(Signal, col):
    N = len(Signal[col])
    vals = list(Signal[col])
    diff = np.array([np.abs(vals[i + 1] - vals[i]) for i in range(N - 1)])
    WL = np.sum(diff)
    return WL

#
# =============================================================================
#

# Calculate the Willison Amplitude (WAMP) of a signal
def CalcWAMP(Signal, col, threshold):
    N = len(Signal[col])
    vals = list(Signal[col])
    diff = np.array([np.abs(vals[i + 1] - vals[i]) for i in range(N - 1)])
    WAMP = np.sum(diff > threshold)
    return WAMP

#
# =============================================================================
#

# Calculate the Log Detector (LOG) of a signal
def CalcLOG(Signal, col):
    N = len(Signal[col])
    ex = (1/N) * np.sum(np.log(Signal[col]))
    LOG = np.e ** ex
    return LOG

#
# =============================================================================
#

# Calculate the Maxiumum Fractal Length (MFL) of a signal
def CalcMFL(Signal, col):
    vals = Signal[col]
    N = len(Signal[col])
    diff = np.array([np.abs(vals[i + 1] - vals[i]) for i in range(N - 1)])
    MFL = np.log(np.sqrt(np.sum(diff ** 2)))
    return MFL

#
# =============================================================================
#

# Calculate the Average Power (AP) of a signal
def CalcAP(Signal, col):
    AP = np.sum(Signal[col] ** 2) / len(Signal[col])
    return AP

#
# =============================================================================
#

# Calculate the "Alpha Ratio" of a PSD graph
# Has presets for known threshold values
#
# psd   PSD graph to perform the twitch ratio on
# freq  Frequency threshold separating fast-twitching muscles from
#       slow-twitching muscles
def CalcTwitchRatio(psd, freq=60):
    
    fast_twitch = psd[psd['Frequency'] > freq]
    slow_twitch = psd[psd['Frequency'] < freq]
    
    twitch_ratio = np.sum(fast_twitch['Power']) / np.sum(slow_twitch['Power'])
    
    return twitch_ratio

#
# =============================================================================
#

# Calculate the "twitch index" of a PSD graph
#
# psd   PSD graph to perform the twitch index on
# freq  Frequency threshold separating fast-twitching muscles from
#       slow-twitching muscles
def CalcTwitchIndex(psd, freq=60):
    
    fast_twitch = psd[psd['Frequency'] > freq]
    slow_twitch = psd[psd['Frequency'] < freq]
    
    twitch_index = np.max(fast_twitch['Power']) / np.max(slow_twitch['Power'])
    
    return twitch_index

#
# =============================================================================
#

# Calculate the "twitch slope" of a PSD graph
#
# psd   PSD graph to perform the twitch slope on
# freq  Frequency threshold separating fast-twitching muscles from
#       slow-twitching muscles
def CalcTwitchSlope(psd, freq=60):
    
    fast_twitch = psd[psd['Frequency'] > freq]
    slow_twitch = psd[psd['Frequency'] < freq]
    
    x_fast = fast_twitch['Frequency']
    y_fast = fast_twitch['Power']
    A_fast = np.vstack([x_fast, np.ones(len(x_fast))]).T
    
    x_slow = slow_twitch['Frequency']
    y_slow = slow_twitch['Power']
    A_slow = np.vstack([x_slow, np.ones(len(x_slow))]).T
    
    fast_alpha = np.linalg.lstsq(A_fast, y_fast, rcond=None)[0]
    slow_alpha = np.linalg.lstsq(A_slow, y_slow, rcond=None)[0]
    
    fast_slope = fast_alpha[0]
    slow_slope = slow_alpha[0]
    
    return fast_slope, slow_slope

#
# =============================================================================
#

# Calculate the Spectral Centroid (SC) of a PSD graph
def CalcSC(psd):
    SC = np.sum(psd['Power']*psd['Frequency']) / np.sum(psd['Power'])
    return SC

#
# =============================================================================
#

# Calculate the Spectral Flatness (SF) of a PSD graph
def CalcSF(psd):
    N = psd.shape[0]
    SS = np.prod(psd['Power'] ** (1/N)) / ((1/N) * np.sum(psd['Power']))
    return SS

#
# =============================================================================
#

# Calculate the Spectral Spread (SS) of a PSD graph
def CalcSS(psd):
    SC = CalcSC(psd)
    SS = np.sum(((psd['Frequency'] - SC) ** 2) * psd['Power']) / np.sum(psd['Power'])
    return SS

#
# =============================================================================
#

# Calculate the Spectral Decrease (SDec) of a PSD graph
def CalcSDec(psd):
    N = psd.shape[0]
    vals = np.array(psd['Power'])
    SDec = np.sum((vals[1:] - vals[0])/N) / np.sum(vals[1:])
    return SDec

#
# =============================================================================
#

# Calculate the Spectral Entropy of a PSD graph
def CalcSEntropy(psd):
    prob = psd['Power'] / np.sum(psd['Power'])
    SEntropy = -np.sum(prob * np.log(prob))
    return SEntropy

#
# =============================================================================
#

# Calculate the Spectral Rolloff of a PSD graph
def CalcSRoll(psd, percent=0.85):
    total_prob = 0
    total_power = np.sum(psd['Power'])
    # Make copy and reset rows to iterate over them
    psdCalc = psd.copy()
    psdCalc = psdCalc.reset_index()
    for i in range(len(psdCalc)):
        prob = psdCalc.loc[i, 'Power'] / total_power
        total_prob += prob
        if total_power >= percent:
            return psdCalc.loc[i, 'Frequency']

#
# =============================================================================
#

# Calculate the Spectral Bandwidth (SB) of a PSD graph
def CalcSBW(psd, p):
    cent = CalcSC(psd)
    SBW = (np.sum(psd['Power'] * (psd['Frequency'] - cent) ** p)) ** (1/p)
    return SBW

#
# =============================================================================
#

# Analyze signals by performing a collection of analyses on them
def PADS_AnalyzeSignals(in_bandpass, in_smooth, in_perceptual, out_path, sampling_rate):
    
    # Define analysis dataframe
    subject_analysis = pd.DataFrame(columns=[
        # Independent variables
        'PID',      # Person ID
        'EID',      # Emotion ID
        'SID',      # Sample ID
        'Filename', # PID-EID-SID
        'Emotion',  # Actual emotion
        
        # Time-series evaluations
        'Zyg_Min_Volt (mV)',
        'Zyg_Max_Volt (mV)',
        'Zyg_Mean_Volt (mV)',
        'Zyg_SD_Volt (mV)',
        'Zyg_Skewness (mV)',
        'Zyg_Kurtosis (mV)',
        #'Zyg_Spectral_Flux',
        'Zyg_IEMG',
        'Zyg_MAV',
        'Zyg_MMAV1',
        'Zyg_SSI',
        'Zyg_VAR',
        'Zyg_VOrder',
        'Zyg_RMS',
        'Zyg_WL',
        'Zyg_LOG',
        
        'Cor_Min_Volt (mV)',
        'Cor_Max_Volt (mV)',
        'Cor_Mean_Volt (mV)',
        'Cor_SD_Volt (mV)',
        'Cor_Skewness (mV)',
        'Cor_Kurtosis (mV)',
        #'Cor_Spectral_Flux',
        'Cor_IEMG',
        'Cor_MAV',
        'Cor_MMAV1',
        'Cor_SSI',
        'Cor_VAR',
        'Cor_VOrder',
        'Cor_RMS',
        'Cor_WL',
        'Cor_LOG',
        
        # Frequency evaluations
        'Zyg_Max_Freq (Hz)',
        'Zyg_Twitch_Ratio',
        'Zyg_Twitch_Index',
        'Zyg_Fast_Twitch_Slope',
        'Zyg_Slow_Twitch_Slope',
        'Zyg_Spectral_Centroid',
        'Zyg_Spectral_Flatness',
        'Zyg_Spectral_Spread',
        'Zyg_Spectral_Decrease',
        'Zyg_Spectral_Entropy',
        'Zyg_Spectral_Rolloff (Hz)',
        'Zyg_Spectral_Bandwidth',
        
        'Cor_Max_Freq (Hz)',
        'Cor_Twitch_Ratio',
        'Cor_Twitch_Index',
        'Cor_Fast_Twitch_Slope',
        'Cor_Slow_Twitch_Slope',
        'Cor_Spectral_Centroid',
        'Cor_Spectral_Flatness',
        'Cor_Spectral_Spread',
        'Cor_Spectral_Decrease',
        'Cor_Spectral_Entropy',
        'Cor_Spectral_Rolloff (Hz)',
        'Cor_Spectral_Bandwidth'
    ])
    
    emotions = [
        'Neutral',
        'Calm',
        'Happy',
        'Sad',
        'Angry',
        'Fearful',
        'Disgust'
    ]
    
    perceptual = pd.read_csv(in_perceptual)
    
    # Iterate through each RAW folder
    for raw in os.listdir(in_smooth):
        if re.search('PID_[0-9]{2}-[0-9]{2}$', raw):
            in_raw_b = in_bandpass + 'Bandpass_PID_' + raw[-5:] + '/'
            in_raw_s = in_smooth + 'Smooth_PID_' + raw[-5:] + '/'
            #out_raw = out_path + raw + '/'
            
            # Iterate through each person folder
            for person in os.listdir(in_raw_s):
                print("Analyzing files for subject", person, "...")
                in_person_b = in_raw_b + person + '/'
                in_person_s = in_raw_s + person + '/'
                #out_person = out_raw + person
                
                # Iterate through each phsiological data file
                for file in os.listdir(in_person_s):
                    # Read bandpass and smoothed files
                    in_file_b = in_person_b + file
                    in_file_s = in_person_s + file
                    
                    # Get ID data
                    filename = file
                    PID = int(file[0:2])
                    EID = int(file[3:5])
                    SID = int(file[6:8])
                    emotion = emotions[EID - 1]
                    
                    # Read perceptual file to identify baseline reading
                    perceptual_file = perceptual.loc[(perceptual['PID'] == PID) & (perceptual['EID'] == EID) & (perceptual['SID'] == SID)]
                    perceptual_file = perceptual_file.reset_index(drop=True).loc[0]
                    percep_order = perceptual_file['Order']
                    if percep_order % 2 == 0:
                        # File is emotional, use the previous file
                        baseline_file = perceptual.loc[(perceptual['PID'] == PID) & (perceptual['Order'] == percep_order - 1)]
                        baseline_file = baseline_file.reset_index(drop=True).loc[0]
                        baseline = baseline_file['Filename']
                    else:
                        # File is not emotional, it is the baseline
                        baseline = perceptual_file['Filename']
                        
                    # Construct baseline file link
                    if PID >= 10:
                        in_file_baseline = in_person_b + str(PID) + '-' + baseline[:5] + '.csv'
                    else:
                        in_file_baseline = in_person_b + '0' + str(PID) + '-' + baseline[:5] + '.csv'
                    
                    # Get data (bandpass and smooth)
                    data_b = pd.read_csv(in_file_b)
                    data_s = pd.read_csv(in_file_s)
                    data_baseline = pd.read_csv(in_file_baseline)
                    
                    # Get time-series data (smooth)
                    Zyg_Min_Time = np.min(data_s['EMG_zyg'])
                    Zyg_Max_Time = np.max(data_s['EMG_zyg'])
                    Zyg_Mean_Time = np.mean(data_s['EMG_zyg'])
                    Zyg_SD_Time = np.std(data_s['EMG_zyg'])
                    Zyg_Skew = scipy.stats.skew(data_s['EMG_zyg'])
                    Zyg_Kurtosis = scipy.stats.kurtosis(data_s['EMG_zyg'])
                    #Zyg_Spectral_Flux = CalcSpecFlux(data_b, data_baseline, 'EMG_zyg', 'EMG_zyg', sampling_rate, sampling_rate)
                    Zyg_IEMG = CalcIEMG(data_s, 'EMG_zyg', sampling_rate)
                    Zyg_MAV = CalcMAV(data_s, 'EMG_zyg')
                    Zyg_MMAV1 = CalcMMAV1(data_s, 'EMG_zyg')
                    Zyg_SSI = CalcSSI(data_s, 'EMG_zyg', sampling_rate)
                    Zyg_VAR = CalcVAR(data_s, 'EMG_zyg')
                    Zyg_VOrder = CalcVOrder(data_s, 'EMG_zyg')
                    Zyg_RMS = CalcRMS(data_s, 'EMG_zyg')
                    Zyg_WL = CalcWL(data_s, 'EMG_zyg')
                    Zyg_LOG = CalcLOG(data_s, 'EMG_zyg')
                    
                    Cor_Min_Time = np.min(data_s['EMG_cor'])
                    Cor_Max_Time = np.max(data_s['EMG_cor'])
                    Cor_Mean_Time = np.mean(data_s['EMG_cor'])
                    Cor_SD_Time = np.std(data_s['EMG_cor'])
                    Cor_Skew = scipy.stats.skew(data_s['EMG_cor'])
                    Cor_Kurtosis = scipy.stats.kurtosis(data_s['EMG_cor'])
                    #Cor_Spectral_Flux = CalcSpecFlux(data_b, data_baseline, 'EMG_cor', 'EMG_cor', sampling_rate, sampling_rate)
                    Cor_IEMG = CalcIEMG(data_s, 'EMG_cor', sampling_rate)
                    Cor_MAV = CalcMAV(data_s, 'EMG_cor')
                    Cor_MMAV1 = CalcMMAV1(data_s, 'EMG_cor')
                    Cor_SSI = CalcSSI(data_s, 'EMG_cor', sampling_rate)
                    Cor_VAR = CalcVAR(data_s, 'EMG_cor')
                    Cor_VOrder = CalcVOrder(data_s, 'EMG_cor')
                    Cor_RMS = CalcRMS(data_s, 'EMG_cor')
                    Cor_WL = CalcWL(data_s, 'EMG_cor')
                    Cor_LOG = CalcLOG(data_s, 'EMG_cor')
                    
                    # Get frequency data (bandpass)
                    psd_zyg = nk.signal_psd(data_b['EMG_zyg'], sampling_rate=sampling_rate)
                    Zyg_Max_Freq = psd_zyg.iloc[psd_zyg['Power'].idxmax()]['Frequency']
                    Zyg_Twitch_Ratio = CalcTwitchRatio(psd_zyg)
                    Zyg_Twitch_Index = CalcTwitchIndex(psd_zyg)
                    Zyg_Fast_Twitch_Slope, Zyg_Slow_Twitch_Slope = CalcTwitchSlope(psd_zyg)
                    Zyg_Spectral_Centroid = CalcSC(psd_zyg)
                    Zyg_Spectral_Flatness = CalcSF(psd_zyg)
                    Zyg_Spectral_Spread = CalcSS(psd_zyg)
                    Zyg_Spectral_Decrease = CalcSDec(psd_zyg)
                    Zyg_Spectral_Entropy = CalcSEntropy(psd_zyg)
                    Zyg_Spectral_Rolloff = CalcSRoll(psd_zyg)
                    Zyg_Spectral_Bandwidth = CalcSBW(psd_zyg, 2)
                    
                    psd_cor = nk.signal_psd(data_b['EMG_cor'], sampling_rate=sampling_rate)
                    Cor_Max_Freq = psd_cor.iloc[psd_cor['Power'].idxmax()]['Frequency']
                    Cor_Twitch_Ratio = CalcTwitchRatio(psd_cor)
                    Cor_Twitch_Index = CalcTwitchIndex(psd_cor)
                    Cor_Fast_Twitch_Slope, Cor_Slow_Twitch_Slope = CalcTwitchSlope(psd_cor)
                    Cor_Spectral_Centroid = CalcSC(psd_cor)
                    Cor_Spectral_Flatness = CalcSF(psd_cor)
                    Cor_Spectral_Spread = CalcSS(psd_cor)
                    Cor_Spectral_Decrease = CalcSDec(psd_cor)
                    Cor_Spectral_Entropy = CalcSEntropy(psd_cor)
                    Cor_Spectral_Rolloff = CalcSRoll(psd_cor)
                    Cor_Spectral_Bandwidth = CalcSBW(psd_cor, 2)
                    
                    # Append results
                    results = [
                        # Independent variables
                        PID,
                        EID,
                        SID,
                        filename,
                        emotion,
                        
                        # Time-series evaluations
                        Zyg_Min_Time,
                        Zyg_Max_Time,
                        Zyg_Mean_Time,
                        Zyg_SD_Time,
                        Zyg_Skew,
                        Zyg_Kurtosis,
                        #Zyg_Spectral_Flux,
                        Zyg_IEMG,
                        Zyg_MAV,
                        Zyg_MMAV1,
                        Zyg_SSI,
                        Zyg_VAR,
                        Zyg_VOrder,
                        Zyg_RMS,
                        Zyg_WL,
                        Zyg_LOG,
                        
                        Cor_Min_Time,
                        Cor_Max_Time,
                        Cor_Mean_Time,
                        Cor_SD_Time,
                        Cor_Skew,
                        Cor_Kurtosis,
                        #Cor_Spectral_Flux,
                        Cor_IEMG,
                        Cor_MAV,
                        Cor_MMAV1,
                        Cor_SSI,
                        Cor_VAR,
                        Cor_VOrder,
                        Cor_RMS,
                        Cor_WL,
                        Cor_LOG,
                        
                        # Frequency evaluations
                        Zyg_Max_Freq,
                        Zyg_Twitch_Ratio,
                        Zyg_Twitch_Index,
                        Zyg_Fast_Twitch_Slope,
                        Zyg_Slow_Twitch_Slope,
                        Zyg_Spectral_Centroid,
                        Zyg_Spectral_Flatness,
                        Zyg_Spectral_Spread,
                        Zyg_Spectral_Decrease,
                        Zyg_Spectral_Entropy,
                        Zyg_Spectral_Rolloff,
                        Zyg_Spectral_Bandwidth,
                        
                        Cor_Max_Freq,
                        Cor_Twitch_Ratio,
                        Cor_Twitch_Index,
                        Cor_Fast_Twitch_Slope,
                        Cor_Slow_Twitch_Slope,
                        Cor_Spectral_Centroid,
                        Cor_Spectral_Flatness,
                        Cor_Spectral_Spread,
                        Cor_Spectral_Decrease,
                        Cor_Spectral_Entropy,
                        Cor_Spectral_Rolloff,
                        Cor_Spectral_Bandwidth
                    ]
                    
                    subject_analysis.loc[len(subject_analysis.index)] = results
    
    # Write results
    subject_analysis.to_csv(feature_path + 'Features.csv', index=False)
    print('Done.')
    return

#
# =============================================================================
#

# Analyze signals by performing a collection of analyses on them
def AnalyzeSignals(in_bandpass, in_smooth, out_path, sampling_rate, perceptual=None):
    
    
    def MapFiles(in_path):
        filedirs = {}
        for file in os.listdir(in_path):
            if os.path.exists(in_path + file + '/'):
                subDir = MapFiles(in_path + file + '/')
                filedirs.update(subDir)
            elif file[-3:] == 'csv':
                filedirs[file] = in_path + file
        return filedirs
        
    #for file in os.listdir(in_smooth):
    #    
    #    # Handle file
    #    if os.path.exists(in_smooth + file + '/'):
    #        RMSFilterSignals(in_bandpass + file + '/', in_smooth + file + '/', out_path + file + '/')
    #    
    #    # Handle CSV
    #    elif file[-3:] == 'csv':
    #        
    #        
    #        # Save results
    #        os.makedirs(out_path, exist_ok=True)
    #        data.to_csv(out_path + file, index=False)
    #return
            
    filedirs = MapFiles(in_bandpass)
    
    for key in filedirs:
        print(key, ":", filedirs[key])
    
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
    
    raw_path = 'Data/01_Raw/'
    notch_path = 'Data/02_Notch/'
    notch_s_path = 'Data/02_Notch_Special/'
    bandpass_path = 'Data/03_Bandpass/'
    smooth_path = 'Data/04_Smooth/'
    feature_path = 'Data/05_Feature/'
    perceptual_file = 'Data/05_Feature/Perceptual_Data.csv'
    
    sampling_rate = 2000            # Sampling rate
    
    # Frequencies to filter, and their respective intensities
    Hzs = [50, 150, 250, 350, 450, 400, 550, 650, 750, 850, 950]
    Qs =  [ 5,  25,  25,  25,  25,  25,  25,  25,  25,  25,  25]
    
    # Bind Hz and Q values to (Hz, Q) tuples
    notch_vals = []
    for i in range(len(Hzs)):
        notch_val = (Hzs[i], Qs[i])
        notch_vals.append(notch_val)
        
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
    
    notch_sc = [(317, 25)]
    reg = ['^08', '^11']
    
    cols = ['EMG_zyg', 'EMG_cor']
    
    # Old PADS pipeline
    #MergePerceptual(perceptual_path, feature_path)
    #PADS_NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, special_cases)
    #PADS_BandpassFilterSignals(notch_path, bandpass_path, sampling_rate, 20, 450)
    #PADS_RMSFilterSignals(bandpass_path, smooth_path, sampling_rate, 50)
    #PADS_AnalyzeSignals(bandpass_path, smooth_path, perceptual_file, feature_path, sampling_rate)
    
    # Package pipeline
    NotchFilterSignals(raw_path, notch_path, sampling_rate, notch_vals, cols)
    NotchFilterSignals(notch_path, notch_s_path, sampling_rate, notch_sc, cols, expression="^(08|11)")
    #BandpassFilterSignals(notch_s_path, bandpass_path, sampling_rate, 20, 450)
    #RMSFilterSignals(bandpass_path, smooth_path, sampling_rate, 50)
    #AnalyzeSignals(bandpass_path, smooth_path, perceptual_file, feature_path, sampling_rate)