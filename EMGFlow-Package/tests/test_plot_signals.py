import unittest
import importlib
import os
import shutil

# Load EMGFlow from local files
filePath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'EMGFlow', '__init__.py'))
spec = importlib.util.spec_from_file_location("EMGFlow", filePath)
EMGFlow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(EMGFlow)

import shiny

class TestSimple(unittest.TestCase):

#
# =============================================================================
#
    
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
        app = EMGFlow.plot_dashboard(pathNames, 'EMG_zyg', 'mV', autorun=False)
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