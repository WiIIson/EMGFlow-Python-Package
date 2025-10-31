# Testing

## Overview

Code reliability in _EMGFlow_ is enforced via an automated _unittest_ suite run on every commit via GitHub Actions. Developers can also run these same tests locally.

## Running Unit Tests

The _EMGFlow_ package must first be installed. Test case files can then be downloaded and run. These test files are available in the [tests subfolder](https://github.com/WiIIson/EMGFlow-Python-Package/tree/main/tests) of the GitHub repository. Alternatively, users can clone the repo. Test cases can then be run individually, or sequentially as shown below.

```bash
# 1. Install EMGFlow package
pip install EMGFlow

# 2. Clone repo to local folder
git clone git@github.com:WiIIson/EMGFlow-Python-Package.git .

# 3. Navigate to test folder
cd tests

# 5. Run all test cases
python -m unittest discover -v -s . -p 'test_*.py'
```

## Test Coverage

_EMGFlow_’s tests provide broad functional coverage across modules. Access utilities are exercised via package metadata, path creation, sample-data generation, file-type reading, and directory mapping. Preprocessing is covered at both function and batch levels: PSD computation; notch filtering; bandpass filtering; full-wave rectification; artefact screening with both Hampel and Wiener methods; gap filling; four smoothing modes (boxcar, RMS, Gaussian, LOESS); a composite smooth_signals stage; and an end-to-end clean_signals pipeline. Feature tests span >20 calculators across time and frequency domains—e.g., iEMG, MAV, MMAV1/2, RMS, WL, WAMP, variance/SSI, MFL/MNF/MDF, spectral entropy and related slope/decay indices, and twitch metrics—and include a full extract_features run that produces Features.csv. The plotting layer includes a dashboard smoke test to ensure the Shiny app constructs. Assertions focus on types, successful execution, and expected file creation, giving wide “does it run and produce outputs” assurance; targeted numeric regressions, adversarial inputs (missing columns, NaNs at boundaries), and parameter-bound checks can be added to deepen correctness guarantees.
