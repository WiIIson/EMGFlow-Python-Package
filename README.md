# EMGFlow <img src="https://raw.githubusercontent.com/WiIIson/EMGFlow-Python-Package/refs/heads/main/HexSticker.png"  width="100" height="110" align="right">

[![Versions](https://img.shields.io/pypi/pyversions/EMGFlow.svg?logo=python&logoColor=FFE873)](https://pypi.python.org/pypi/emgflow)
[![Coverage](https://raw.githubusercontent.com/WiIIson/EMGFlow-Python-Package/main/badges/coverage.svg)](https://github.com/WiIIson/EMGFlow-Python-Package)
[![pypi](https://img.shields.io/pypi/v/emgflow.svg)](https://pypi.python.org/pypi/emgflow)
[![Downloads](https://static.pepy.tech/badge/EMGFlow/month)](https://pepy.tech/project/EMGFlow)
[![Downloads](https://static.pepy.tech/badge/EMGFlow)](https://pepy.tech/project/EMGFlow)

A Python package for preprocessing and feature extraction of surface electromyography (sEMG) signals.

_EMGFlow_ streamlines end-to-end sEMG analysis for research and clinical workflows. It is designed for batch processing of large datasets typical in machine learning, extracting a comprehensive set of 33 time- and frequency-domain features. The package uses Pandas DataFrames throughout for interoperability and supports flexible file selection with regular expressions. An interactive dashboard visualises signals at each preprocessing stage to aid decisions.

_EMGFlow_ includes a Shiny dashboard for visualising preprocessing effects. Pipeline steps can be overlaid or shown individually, and files are selected from a drop-down menu. A checkbox toggles between a time-domain amplitude view and a spectral view:

![Example 1](https://github.com/WiIIson/EMGFlow-Python-Package/blob/main/EMGFlow_GUI.webp?raw=true)

## Statement Of Need

Although several packages process physiological and neurological signals, support for sEMG has remained limited. Many lack a comprehensive feature set for sEMG, forcing researchers to use a patchwork of tools. Others focus on event detection with GUI-centric workflows that suit continuous recordings of a single participant, but complicate batch feature extraction common in machine learning.

_EMGFlow_, a portmanteau of EMG and Workflow, fills this gap by providing a flexible pipeline for extracting a wide range of sEMG features, with a scalable design suited for large datasets.

## Example

As a quick example, the following will create a feature file, and create a plot of the "EMG_zyg" column:

```python
import EMGFlow as ef

# Get path dictionary
path_names = ef.make_paths()

# Load sample data
ef.make_sample_data(path_names)

# Preprocess signals
ef.clean_signals(path_names, sampling_rate=2000, notch_f0=50)

# Plot data on the "EMG_zyg" column
ef.plot_dashboard(path_names, 'EMG_zyg', sampling_rate=2000)

# Extract features and save results in "Features.csv" in feature_path
df = ef.extract_features(path_names, sampling_rate=2000)
```

## Documentation

[![pypi](https://img.shields.io/badge/documentation-online-brightgreen.svg)](https://wiiison.github.io/EMGFlow-Python-Package/reference/api-overview.html)
[![pypi](https://img.shields.io/badge/tutorials-examples-orange.svg?colorB=E91E63)](https://wiiison.github.io/EMGFlow-Python-Package/guide/examples.html)

General:
- [EMG processing background](https://wiiison.github.io/EMGFlow-Python-Package/guide/about-emg.html)
- [EMGFlow processing pipeline overview](https://wiiison.github.io/EMGFlow-Python-Package/reference/api-overview.html)
- [AccessFiles module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/access-files.html)
- [PreprocessSignals module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/preprocess-signals.html)
- [PlotSignals module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/plot-signals.html)
- [ExtractFeatures module API](https://wiiison.github.io/EMGFlow-Python-Package/reference/extract-features.html)

Examples:
- [Processing pipeline examples](https://wiiison.github.io/EMGFlow-Python-Package/guide/examples.html)

## Installation

EMGFlow can be installed from PyPI:

```python
pip install EMGFlow
```

Once installed, the package can be loaded as follows:

```python
import EMGFlow
```

Project dependencies can be seen in the [build file](https://github.com/WiIIson/EMGFlow-Python-Package/blob/main/pyproject.toml).

## Contributions

Contributions and community guidelines can be seen the [contributing guide](https://github.com/WiIIson/EMGFlow-Python-Package/blob/main/.github/CONTRIBUTING.md).

## Citations

This package can be cited as follows:

```bibtex
@software{Conley_EMGFlow_2025,
  author = {Conley, William and Livingstone, Steven R},
  month = {10},
  title = {{EMGFlow Package}},
  url = {https://github.com/WiIIson/EMGFlow-Python-Package},
  version = {1.1.1},
  year = {2025},
  note = "{\tt william@cconley.ca}"
}
```

If you are using a different version of EMGFlow, change the `version` tag to the version you are using.

You can also use the `EMGFlow.package_citation()` function to print the citation for the version of EMGFlow you are using, or use the `EMGFlow.package_version()` function to view the package version you are using.
