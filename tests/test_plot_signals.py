import unittest
import os
import shutil
import shiny

import EMGFlow

#
# =============================================================================
#

class TestSimple(unittest.TestCase):
    
    def setUp(self):
        pathNames = EMGFlow.make_paths()
        EMGFlow.make_sample_data(pathNames)
        samplingRate = 2000
        cols = ['EMG_zyg', 'EMG_cor']
        EMGFlow.notch_filter_signals(pathNames['Raw'], pathNames['Notch'], samplingRate, [(50, 5)], cols)
        EMGFlow.bandpass_filter_signals(pathNames['Notch'], pathNames['Bandpass'], samplingRate, 20, 140, cols)
        EMGFlow.smooth_filter_signals(pathNames['Bandpass'], pathNames['Smooth'], 50, cols)

#
# =============================================================================
#
    
    def test_plot_dashboard(self):
        pathNames = EMGFlow.make_paths()
        app = EMGFlow.plot_dashboard(pathNames, 'EMG_zyg', 'mV', auto_run=False)
        self.assertIsInstance(app, shiny.App)

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