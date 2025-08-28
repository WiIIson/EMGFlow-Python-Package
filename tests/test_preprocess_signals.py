import unittest
import os
import shutil
import pandas as pd

import EMGFlow

#
# =============================================================================
#

class TestSimple(unittest.TestCase):
    
    def setUp(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        pass

#
# =============================================================================
#
    
    def test_emg_to_psd(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        PSD = EMGFlow.emg_to_psd(Signal, 'EMG_zyg', 2000)
        self.assertIsInstance(PSD, pd.DataFrame)
    
    def test_apply_notch_filters(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        NSignal = EMGFlow.apply_notch_filters(Signal, 'EMG_zyg', 2000, [(40, 4)])
        self.assertIsInstance(NSignal, pd.DataFrame)
    
    def test_notch_filter_signals(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.notch_filter_signals(pathNames['Raw'], pathNames['Notch'], 2000, [(40, 4)])
        self.assertTrue(os.path.exists(os.path.join(pathNames['Notch'], '01', 'sample_data_01.csv')))
    
    def test_apply_bandpass_filter(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        BSignal = EMGFlow.apply_bandpass_filter(Signal, 'EMG_zyg', 2000, 20, 450)
        self.assertIsInstance(BSignal, pd.DataFrame)
    
    def test_bandpass_filter_signals(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.bandpass_filter_signals(pathNames['Raw'], pathNames['Bandpass'], 2000)
        self.assertTrue(os.path.exists(os.path.join(pathNames['Bandpass'], '01', 'sample_data_01.csv')))
    
    def test_apply_rectify(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        SSignal = EMGFlow.apply_rectify(Signal, 'EMG_zyg')
        self.assertIsInstance(SSignal, pd.DataFrame)
    
    def test_rectify_signals(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.rectify_signals(pathNames['Raw'], pathNames['FWR'])
        self.assertTrue(os.path.exists(os.path.join(pathNames['FWR'], '01', 'sample_data_01.csv')))
    
    def test_apply_screen_artefacts(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        ASignal = EMGFlow.apply_screen_artefacts(Signal, 'EMG_zyg', 2000)
        self.assertIsInstance(ASignal, pd.DataFrame)
    
    def test_screen_artefact_signals(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.screen_artefact_signals(pathNames['Raw'], pathNames['Screened'], 2000)
        self.assertTrue(os.path.exists(os.path.join(pathNames['Screened'], '01', 'sample_data_01.csv')))
    
    def test_apply_fill_missing(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        FSignal = EMGFlow.apply_fill_missing(Signal, 'EMG_zyg')
        self.assertIsInstance(FSignal, pd.DataFrame)
    
    def test_fill_missing_signals(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.fill_missing_signals(pathNames['Raw'], pathNames['Filled'])
        self.assertTrue(os.path.exists(os.path.join(pathNames['Filled'], '01', 'sample_data_01.csv')))
    
    def test_apply_boxcar_smooth(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        SSignal = EMGFlow.apply_boxcar_smooth(Signal, 'EMG_zyg', 2000, 50)
        self.assertIsInstance(SSignal, pd.DataFrame)
    
    def test_apply_rms_smooth(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        SSignal = EMGFlow.apply_rms_smooth(Signal, 'EMG_zyg', 2000, 50)
        self.assertIsInstance(SSignal, pd.DataFrame)
    
    def test_apply_gaussian_smooth(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        SSignal = EMGFlow.apply_gaussian_smooth(Signal, 'EMG_zyg', 2000, 50)
        self.assertIsInstance(SSignal, pd.DataFrame)
    
    def test_apply_loess_smooth(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        SSignal = EMGFlow.apply_loess_smooth(Signal, 'EMG_zyg', 2000, 50)
        self.assertIsInstance(SSignal, pd.DataFrame)
    
    def test_smooth_signals(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.smooth_signals(pathNames['Raw'], pathNames['Smooth'], 2000)
        self.assertTrue(os.path.exists(os.path.join(pathNames['Smooth'], '01', 'sample_data_01.csv')))
    
    def test_clean_signals(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.clean_signals(pathNames, 2000, use_optional=True)
        self.assertTrue(os.path.exists(os.path.join(pathNames['Smooth'], '01', 'sample_data_01.csv')))

    def test_detect_outliers(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        outliers = EMGFlow.detect_spectral_outliers(pathNames['Raw'], 2000)
        self.assertIsInstance(outliers, dict)

#
# =============================================================================
#

    def tearDown(self):
        if os.path.exists('./Data') == True:
            shutil.rmtree('./Data')
            
#
# =============================================================================
#

if __name__ == '__main__':
    unittest.main()