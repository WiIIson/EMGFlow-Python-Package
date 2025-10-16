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
        sampling_rate = 2000
        column_names = ['EMG_zyg', 'EMG_cor']
        EMGFlow.notch_filter_signals(pathNames['raw'], pathNames['notch'], column_names, sampling_rate, [(50, 5)])
        EMGFlow.bandpass_filter_signals(pathNames['notch'], pathNames['bandpass'], column_names, sampling_rate, (20, 140),)
        EMGFlow.smooth_signals(pathNames['bandpass'], pathNames['smooth'], column_names, sampling_rate)

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