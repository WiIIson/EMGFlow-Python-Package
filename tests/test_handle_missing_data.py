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

    def test_apply_fill_missing(self):
        pathNames = EMGFlow.make_paths()
        filePath = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
        Signal = EMGFlow.read_file_type(filePath, 'csv')
        ASignal = EMGFlow.apply_screen_artefacts(Signal, 'EMG_zyg')
        FSignal = EMGFlow.apply_fill_missing(ASignal, 'EMG_zyg')
        self.assertIsInstance(FSignal, pd.DataFrame)
    
    def test_fill_missing_signals(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.screen_artefact_signals(pathNames['Raw'], pathNames['Filled'], 2000)
        EMGFlow.fill_missing_signals(pathNames['Filled'], pathNames['Filled'], 2000)
        self.assertTrue(os.path.exists(os.path.join(pathNames['Filled'], '01', 'sample_data_01.csv')))

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