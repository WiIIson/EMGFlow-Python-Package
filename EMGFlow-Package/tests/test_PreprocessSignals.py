import unittest
import pandas as pd
import numpy as np
import os

from EMGFlow.PreprocessSignals import *

test_df = pd.DataFrame({'r1':[1,2,4,2,5,3,1,5,7,3,7,8,4,2,5,3,5,3,2,1,6,3,6,1,2]})
test_df_2 = pd.DataFrame({'r1':[1,-2,3,-4,5,6,-7]})
test_sr = 1000

class TestSimple(unittest.TestCase):
    
    def setUp(self):
        if os.path.exists('./Testing') == False:
            os.mkdir('./Testing')
            time_col = np.array(range(500)) / 100
            emg_col = np.sin(time_col) + (np.random.rand(500)/10)
            df = pd.DataFrame({'Time':time_col, 'EMG':emg_col})
            df.to_csv('./Testing/Data.csv', index=False)
        if os.path.exists('./Testing_out') == False:
            os.mkdir('./Testing_out')
        if os.path.exists('./Testing_plots') == False:
            os.mkdir('./Testing_plots')

#
# =============================================================================
#

    # ============================
    # TEST MAIN PIPELINE FUNCTIONS
    # ============================

    def test_NotchFilterSignals(self):
        NotchFilterSignals('./Testing/', './Testing_out/', 100, [(10,4)], cols=['EMG'])
        self.assertTrue(os.path.isfile('./Testing_out/Data.csv'))
        os.remove('./Testing_out/Data.csv')

    def test_BandpassFilterSignals(self):
        BandpassFilterSignals('./Testing/', './Testing_out/', 100, 10, 40, cols=['EMG'])
        self.assertTrue(os.path.isfile('./Testing_out/Data.csv'))
        os.remove('./Testing_out/Data.csv')
        
    def test_SmoothFilterSignals(self):
        SmoothFilterSignals('./Testing/', './Testing_out/', 5, ['EMG'])
        self.assertTrue(os.path.isfile('./Testing_out/Data.csv'))
        os.remove('./Testing_out/Data.csv')
        
    def test_ExtractFeatures(self):
        ExtractFeatures('./Testing/', './Testing/', './Testing_out', 100)
        self.assertTrue(os.path.isfile('./Testing_out/Features.csv'))
        os.remove('./Testing_out/Features.csv')

#
# =============================================================================
#

    # =====================
    # TEST HELPER FUNCTIONS
    # =====================

    def test_EMG2PSD(self):
        test = EMG2PSD(test_df['r1']).round(6)
        ans = pd.DataFrame({'Frequency':[166.666667,208.333333,250.000000,
                                         291.666667,333.333333,375.000000,
                                         416.666667,458.333333,500.000000],
                          'Power':[0.730713,0.797440,0.900509,
                                   1.000000,0.887714,0.456161,
                                   0.119441,0.310694,0.275484],
                          '':[4,5,6,7,8,9,10,11,12]}).set_index('')
        self.assertTrue(ans.equals(test))
        
    def test_ReadFileType(self):
        df = ReadFileType('./Testing/Data.csv', 'csv')
        self.assertIsInstance(df, pd.DataFrame)
    
    def test_MapFiles(self):
        dic = MapFiles('./Testing')
        self.assertEqual(list(dic.keys()), ['Data.csv'])
    
    def test_ConvertMapFiles(self):
        dic = ConvertMapFiles('./Testing')
        self.assertEqual(list(dic.keys()), ['Data.csv'])
    
    def test_MapFilesFuse(self):
        f1 = {'f1': 'data/raw/file1.csv', 'f2': 'data/raw/file2.csv'}
        f2 = {'f1': 'data/notch/file1.csv', 'f2': 'data/notch/file2.csv'}
        mf = MapFilesFuse([f1, f2], ['raw', 'notch'])
        ans = pd.DataFrame({'File': ['f1', 'f2'],
                            'ID': ['f1', 'f2'],
                            'raw':['data/raw/file1.csv', 'data/raw/file2.csv'],
                            'notch': ['data/notch/file1.csv', 'data/notch/file2.csv']}).set_index('ID')
        self.assertTrue(ans.equals(mf))
    
    def test_ApplyNotchFilters(self):
        test = ApplyNotchFilters(test_df, 'r1', test_sr, [(300, 1)])
        test = list(test['r1'].round(6))
        ans = [0.420808,0.992248,2.432778,2.247981,4.108091,2.692046,3.255595,
               3.206220,4.348613,4.563833,6.173350,5.566716,6.239481,4.507329,
               4.123417,3.045906,4.849224,3.046484,3.701607,1.723204,3.764653,
               2.537514,5.766236,2.145930,3.981718]
        self.assertEqual(test, ans)
    
    def test_ApplyBandpassFilter(self):
        test = ApplyBandpassFilter(test_df, 'r1', test_sr, 200, 400)
        test = list(test['r1'].round(6))
        ans = [ 0.021940,-0.006279,-0.076945,-0.052606, 0.206017, 0.205518,
               -0.589232, 0.129109, 0.835802,-1.401190, 0.206412, 2.198563,
               -2.222842,-0.935213, 3.018585,-1.124564,-1.896266, 1.720436,
                0.458087,-0.738796, 0.164597,-0.640371,-0.10242, 1.4873330,
               -0.260217]
        
        self.assertEqual(test, ans)
        
        with self.assertRaises(Exception):
            ApplyBandpassFilter(test_df, 'r1', test_sr, 400, 200)
        
        with self.assertRaises(Exception):
            ApplyBandpassFilter(test_df, 'r2', test_sr, 200, 400)
    
    def test_ApplyFWR(self):
        test = ApplyFWR(test_df_2, 'r1')
        test = list(test['r1'].round(6))
        ans = [1,2,3,4,5,6,7]
        self.assertEqual(test, ans)
    
    def test_ApplyBoxcarSmooth(self):
        test = ApplyBoxcarSmooth(test_df, 'r1', 3)
        test = list(test['r1'].round(6))
        ans = [1.0, 2.333333, 2.666667, 3.666667, 3.333333, 3.0, 3.0, 4.333333,
               5.0, 5.666667, 6.0, 6.333333, 4.666667, 3.666667, 3.333333,
               4.333333, 3.666667, 3.333333, 2.0, 3.0, 3.333333, 5.0, 3.333333,
               3.0, 1.0]
        
        self.assertEqual(test, ans)
        
        with self.assertRaises(Exception):
            ApplyBoxcarSmooth(test_df, 'r1', -1)
        
        with self.assertRaises(Exception):
            ApplyBoxcarSmooth(test_df, 'r2', 3)
    
    def test_ApplyRMSSmooth(self):
        test = ApplyRMSSmooth(test_df, 'r1', 3)
        test = list(test['r1'].round(6))
        ans = [1.290994, 2.645751, 2.828427, 3.872983, 3.559026, 3.41565,
               3.41565, 5.0, 5.259911, 5.972158, 6.377042, 6.557439, 5.291503,
               3.872983, 3.559026, 4.434712, 3.785939, 3.559026, 2.160247,
               3.696846, 3.91578, 5.196152, 3.91578, 3.696846, 1.290994]
        
        self.assertEqual(test, ans)
        
        with self.assertRaises(Exception):
            ApplyRMSSmooth(test_df, 'r1', -1)
        
        with self.assertRaises(Exception):
            ApplyRMSSmooth(test_df, 'r2', 3)
    
    def test_ApplyGaussianSmooth(self):
        test = ApplyGaussianSmooth(test_df, 'r1', 3)
        test = list(test['r1'].round(6))
        ans = [0.882884, 2.007738, 2.563652, 2.975621, 3.204565, 2.648651,
               2.334708, 3.930477, 4.728362, 4.584417, 5.454274, 5.853216,
               4.015476, 2.975621, 3.204565, 3.616534, 3.446536, 2.890622,
               1.765767, 2.334708, 3.361537, 4.100476, 3.361537, 2.334708,
               1.039855]
        
        self.assertEqual(test, ans)
        
        with self.assertRaises(Exception):
            ApplyGaussianSmooth(test_df, 'r1', -1)
        
        with self.assertRaises(Exception):
            ApplyGaussianSmooth(test_df, 'r2', 3)
    
    def test_ApplyLoessSmooth(self):
        test = ApplyLoessSmooth(test_df, 'r1', 3)
        test = list(test['r1'].round(6))
        ans = [1.0, 2.286311, 2.854758, 3.431553, 3.568447, 3.0, 2.717863,
               4.427379, 5.282137, 5.290484, 6.141068, 6.568447, 4.572621,
               3.431553, 3.568447, 4.145242, 3.854758, 3.286311, 2.0, 2.717863,
               3.709516, 4.717863, 3.709516, 2.717863, 1.141068]
        
        self.assertEqual(test, ans)
        
        with self.assertRaises(Exception):
            ApplyLoessSmooth(test_df, 'r1', -1)
        
        with self.assertRaises(Exception):
            ApplyLoessSmooth(test_df, 'r2', 3)

#
# =============================================================================
#

    # =========================
    # TEST FEATURE CALCULATIONS
    # =========================

    def test_CalcIEMG(self):
        val = CalcIEMG(test_df, 'r1', test_sr)
        self.assertAlmostEqual(val, 91000, 6)
    
    def test_CalcMAV(self):
        val = CalcMAV(test_df, 'r1')
        self.assertAlmostEqual(val, 3.64, 6)
    
    def test_CalcMMAV(self):
        val = CalcMMAV(test_df, 'r1')
        self.assertAlmostEqual(val, 2.9, 6)
    
    def test_CalcSSI(self):
        val = CalcSSI(test_df, 'r1', test_sr)
        self.assertAlmostEqual(val, 435000000, 6)
    
    def test_CalcVAR(self):
        val = CalcVAR(test_df, 'r1')
        self.assertAlmostEqual(val, 18.125, 6)
    
    def test_CalcVOrder(self):
        val = CalcVOrder(test_df, 'r1')
        self.assertAlmostEqual(val, 4.257346591481601, 6)
    
    def test_CalcRMS(self):
        val = CalcRMS(test_df, 'r1')
        self.assertAlmostEqual(val, 4.171330722922843, 6)
    
    def test_CalcWL(self):
        val = CalcWL(test_df, 'r1')
        self.assertAlmostEqual(val, 61, 6)
    
    def test_CalcWAMP(self):
        val = CalcWAMP(test_df, 'r1', 3)
        self.assertAlmostEqual(val, 6, 6)
    
    def test_CalcLOG(self):
        val = CalcLOG(test_df, 'r1')
        self.assertAlmostEqual(val, 3.0311944199668637, 6)
    
    def test_CalcMFL(self):
        val = CalcMFL(test_df, 'r1')
        self.assertAlmostEqual(val, 2.626136714023315, 6)
    
    def test_CalcAP(self):
        val = CalcAP(test_df, 'r1')
        self.assertAlmostEqual(val, 17.4, 6)
    
    def test_CalcSpecFlux(self):
        val = CalcSpecFlux(test_df, 0.5, 'r1', test_sr)
        self.assertAlmostEqual(val, 0.5224252376723382, 6)
    
    def test_CalcTwitchRatio(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcTwitchRatio(test_psd, 300)
        self.assertAlmostEqual(val, 0.5977534161813928, 6)
    
    def test_CalcTwitchIndex(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcTwitchIndex(test_psd, 300)
        self.assertAlmostEqual(val, 0.8877144736307457, 6)
    
    def test_CalcTwitchSlope(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcTwitchSlope(test_psd, 300)
        self.assertAlmostEqual(val[0], -0.00328782718654115, 6)
        self.assertAlmostEqual(val[1],  0.0021862362905523637, 6)
    
    def test_CalcSC(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcSC(test_psd)
        self.assertAlmostEqual(val, 292.359023451208, 6)
    
    def test_CalcSF(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcSF(test_psd)
        self.assertAlmostEqual(val, 0.8312063847767466, 6)
    
    def test_CalcSS(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcSS(test_psd)
        self.assertAlmostEqual(val, 8338.261247555056, 6)
    
    def test_CalcSDec(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcSDec(test_psd)
        self.assertAlmostEqual(val, -0.02570405799570487, 6)
    
    def test_CalcSEntropy(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcSEntropy(test_psd)
        self.assertAlmostEqual(val, 2.0549105067193647, 6)
    
    def test_CalcSRoll(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcSRoll(test_psd, 0.5)
        self.assertAlmostEqual(val, 166.66666666666666, 6)
    
    def test_CalcSBW(self):
        test_psd = EMG2PSD(test_df['r1'])
        val = CalcSBW(test_psd)
        self.assertAlmostEqual(val, 213.72481710595903, 6)

#
# =============================================================================
#

    def tearDown(self):
        if os.path.exists('./Testing') == True:
            os.remove('./Testing/Data.csv')
            os.rmdir('./Testing')
        if os.path.exists('./Testing_out') == True:
            os.rmdir('./Testing_out')
        if os.path.exists('./Testing_plots') == True:
            os.rmdir('./Testing_plots')