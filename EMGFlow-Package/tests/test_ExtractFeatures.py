import unittest
import pandas as pd
import numpy as np
import os
import sys

sys.path.append('..')

from src.EMGFlow.ExtractFeatures import *

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

    def test_ExtractFeatures(self):
        ExtractFeatures('./Testing/', './Testing/', './Testing_out', 100)

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