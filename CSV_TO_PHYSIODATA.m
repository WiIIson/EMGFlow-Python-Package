%--------------------------------------------------------------------------
% INFO:
%   This file shows how to load signals from a csv file into MATLAB and
%   save them as a PhysioData file for processing in the Toolbox, along
%   with custom labels and epochs
%--------------------------------------------------------------------------

%% Loading Raw Data:

% Load data:
fileName = '.\Data\Clean-Data\Clean_PID_01-10\01\01-01-02.csv';
csvData = readtable(fileName);

% Create empty struct:
pdtData = struct();

% Add the EMG_zyg channel to the struct in channel 1:
chanNum = 1;
pdtData.data.signals.channels{chanNum}           = csvData.EMG_zyg;
pdtData.data.signals.channelNames{chanNum}       = 'EMG_zyg';
pdtData.data.signals.channelUnits{chanNum}       = 'mV';
pdtData.data.signals.channelDescription{chanNum} = 'Zygomaticus EMG data';

% Add the EMG_cor channel to the struct in channel 2:
chanNum = 2;
pdtData.data.signals.channels{chanNum}           = csvData.EMG_cor;
pdtData.data.signals.channelNames{chanNum}       = 'EMG_cor';
pdtData.data.signals.channelUnits{chanNum}       = 'mV';
pdtData.data.signals.channelDescription{chanNum} = 'Corrugator EMG data';

% Add the ECG channel to the struct in channel 3:
chanNum = 3;
pdtData.data.signals.channels{chanNum}           = csvData.ECG;
pdtData.data.signals.channelNames{chanNum}       = 'ECG';
pdtData.data.signals.channelUnits{chanNum}       = 'mV';
pdtData.data.signals.channelDescription{chanNum} = 'ECG data';

% Add the Respiration channel to the struct in channel 4:
chanNum = 4;
pdtData.data.signals.channels{chanNum}           = csvData.Respiration;
pdtData.data.signals.channelNames{chanNum}       = 'Respiration';
pdtData.data.signals.channelUnits{chanNum}       = 'mV';
pdtData.data.signals.channelDescription{chanNum} = 'Respiration data';

% Log that the sampling frequency was 2000 Hz:
pdtData.data.signals.fs = 2000;

%% Adding Labels:

%% Adding Pregenerated Epochs:

%% Saving the File:

% Add metadata:
pdtData.physioDataInfo.rawDataSource       = fileName;
pdtData.physioDataInfo.pdtFileCreationDate = datestr(now);
pdtData.physioDataInfo.pdtFileCreationUser = getenv('USERNAME');

% Save pdtData struct as a .physioData file:
save('signal2.physioData', '-struct', 'pdtData');