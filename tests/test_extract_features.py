import unittest
import os
import shutil
import numpy as np

import EMGFlow

#
# =============================================================================
#

class TestSimple(unittest.TestCase):
    
    def setUp(self):
        pass

#
# =============================================================================
#


    def test_calc_iemg(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        IEMG = EMGFlow.calc_iemg(Signal, 'EMG_zyg', 2000)
        self.assertIsInstance(IEMG, float)
    
    def test_calc_mav(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        MAV = EMGFlow.calc_mav(Signal, 'EMG_zyg')
        self.assertIsInstance(MAV, float)
    
    def test_calc_mmav1(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        MMAV1 = EMGFlow.calc_mmav1(Signal, 'EMG_zyg')
        self.assertIsInstance(MMAV1, float)
    
    def test_calc_mmav2(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        MMAV2 = EMGFlow.calc_mmav2(Signal, 'EMG_zyg')
        self.assertIsInstance(MMAV2, float)
    
    def test_calc_ssi(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        SSI = EMGFlow.calc_ssi(Signal, 'EMG_zyg', 2000)
        self.assertIsInstance(SSI, float)
    
    def test_calc_var(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        VAR = EMGFlow.calc_var(Signal, 'EMG_zyg')
        self.assertIsInstance(VAR, float)
    
    def test_calc_vorder(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        VOrder = EMGFlow.calc_vorder(Signal, 'EMG_zyg')
        self.assertIsInstance(VOrder, float)
    
    def test_calc_rms(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        RMS = EMGFlow.calc_rms(Signal, 'EMG_zyg')
        self.assertIsInstance(RMS, float)
    
    def test_calc_wl(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        WL = EMGFlow.calc_wl(Signal, 'EMG_zyg')
        self.assertIsInstance(WL, float)
    
    def test_calc_wamp(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        WAMP = EMGFlow.calc_wamp(Signal, 'EMG_zyg', 0.001)
        self.assertIsInstance(WAMP, np.integer)
        
    
    def test_calc_log(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        Signal = EMGFlow.apply_fwr(Signal, 'EMG_zyg')
        Signal += 0.0001
        LOG = EMGFlow.calc_log(Signal, 'EMG_zyg')
        self.assertIsInstance(LOG, float)
    
    def test_calc_mfl(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        MFL = EMGFlow.calc_mfl(Signal, 'EMG_zyg')
        self.assertIsInstance(MFL, float)
    
    def test_calc_ap(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        AP = EMGFlow.calc_ap(Signal, 'EMG_zyg')
        self.assertIsInstance(AP, float)
    
    def test_calc_mdf(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        MDF = EMGFlow.calc_mdf(PSD)
        self.assertIsInstance(MDF, float)
    
    def test_calc_mnf(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        MNF = EMGFlow.calc_mnf(PSD)
        self.assertIsInstance(MNF, float)
    
    def test_calc_twitch_ratio(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        twitchRatio = EMGFlow.calc_twitch_ratio(PSD)
        self.assertIsInstance(twitchRatio, float)
    
    def test_calc_twitch_index(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        twitchIndex = EMGFlow.calc_twitch_index(PSD)
        self.assertIsInstance(twitchIndex, float)
    
    def test_calc_twitch_slope(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        twitchSlope = EMGFlow.calc_twitch_slope(PSD)
        self.assertIsInstance(twitchSlope, tuple)
        self.assertIsInstance(twitchSlope[0], float)
        self.assertIsInstance(twitchSlope[1], float)
    
    def test_calc_sc(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        SC = EMGFlow.calc_sc(PSD)
        self.assertIsInstance(SC, float)
    
    def test_calc_sflt(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        SF = EMGFlow.calc_sflt(PSD)
        self.assertIsInstance(SF, float)
    
    def test_calc_sflx(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        specFlux = EMGFlow.calc_sflx(Signal, 0.5, 'EMG_zyg', 2000)
        self.assertIsInstance(specFlux, float)
    
    def test_calc_ss(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        SS = EMGFlow.calc_ss(PSD)
        self.assertIsInstance(SS, float)
    
    def test_calc_sd(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        SD = EMGFlow.calc_sd(PSD)
        self.assertIsInstance(SD, float)
    
    def test_calc_se(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        SE = EMGFlow.calc_se(PSD)
        self.assertIsInstance(SE, float)
    
    def test_calc_sr(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        SR = EMGFlow.calc_sr(PSD)
        self.assertIsInstance(SR, float)
    
    def test_calc_sbw(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal['EMG_zyg'], 2000)
        SBW = EMGFlow.calc_sbw(PSD)
        self.assertIsInstance(SBW, float)
    
    def test_extract_features(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        samplingRate = 2000
        cols = ['EMG_zyg', 'EMG_cor']
        EMGFlow.notch_filter_signals(pathNames['Raw'], pathNames['Notch'], samplingRate, [(50, 5)], cols)
        EMGFlow.bandpass_filter_signals(pathNames['Notch'], pathNames['Bandpass'], samplingRate, 20, 140, cols)
        EMGFlow.smooth_filter_signals(pathNames['Bandpass'], pathNames['Smooth'], 50, cols)
        EMGFlow.extract_features(pathNames, samplingRate, cols)
        self.assertTrue(os.path.exists(os.path.join('Data', 'Feature', 'Features.csv')))

#
# =============================================================================
#

    def tearDown(self):
        if os.path.exists('./Data') == True:
            shutil.rmtree('./Data')
        pass
            
#
# =============================================================================
#

if __name__ == '__main__':
    unittest.main()