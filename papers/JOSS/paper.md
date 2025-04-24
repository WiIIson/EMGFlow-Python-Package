---
title: "EMGFlow: A Python package for pre-processing and feature extraction of electromyographic signals"
tags:
  - Biosignals
  - Physiology
  - Python
  - EMGFlow
  - EMG
authors:
  - name: William L. Conley
    corresponding: true
    orcid: 0009-0001-7454-1286
    affiliation: 1
  - name: Steven R. Livingstone
    orcid: 0000-0002-6364-6410
    affiliation: 1
affiliations:
  - index: 1
    name: Department of Computer Science, Ontario Tech University, Oshawa, Canada
date: 9 July 2024
bibliography: paper.bib
---

# Summary

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The use of surface electromyography (sEMG) as a measure of human physiology and behaviour has grown recently, supported by developments in deep learning and wearable computing. Here, we present _EMGFlow_, an open-source Python package for preprocessing and extracting features from sEMG signals. *EMGFlow* has been designed to facilitate the analysis of large datasets through batch processing of signal files, a common requirement in machine learning. The package extracts an extensive set of features from both time and frequency domains. Regular expression matching provides additional flexibility in mapping files for selective preprocessing and extraction. The use of Pandas DataFrame throughout allows users to mix and match elements of the processing pipeline, supporting interoperability with other packages. An interactive dashboard supports human decision processes through a visual comparison of signals at each stage of preprocessing. _EMGFlow_ is released under the GNU General Public License (v3.0) and can be installed from PyPI. Source code, documentation, and examples are accessible on GitHub ([https://github.com/WiIIson/EMGFlow-Python-Package](https://github.com/WiIIson/EMGFlow-Python-Package)).

# Statement of Need

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Although several packages exist for processing physiological and neurological signals, support for sEMG has remained limited. Many packages lack a comprehensive set of features that can be extracted from sEMG data, leaving researchers to use a patchwork of tools. Other packages are orientated around event detection in individual recordings and use a GUI-based workflow that requires more manual intervention. While this design works well for processing unedited continuous recordings of a single participant, it complicates the extraction of features from large datasets common to machine learning [@abadi_decaf_2015; @chen_emotion_2022; @koelstra_deap_2012; @schmidt_introducing_2018; @sharma_dataset_2019; @zhang_biovid_2016].

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_EMGFlow_, a portmanteau of EMG and Workflow, fills this gap by providing a flexible pipeline for extracting a wide range of sEMG features, with a scalable design suited for large datasets.

# Comparison to Other Packages

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Compared to other toolkits, _EMGFlow_ extracts a comprehensive set of 32 statistical features from sEMG signals [@bota_biosppy_2024; @makowski_neurokit2_2021; @sjak-shie_physiodata_2022; @soleymani_toolbox_2017]. An interactive dashboard visualizes batch processed files rather than individual recordings, allowing the operator to efficiently view the effects of preprocessing stages across all files. Adjustable filter settings and smoothing functions support cleaning of data collected in North America or internationally (50 vs 60 HZ mains AC), a subtle difference overlooked in some packages.

# Features

## Processing Pipeline

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Extracting features from large datasets is a common task in machine learning and quantitative domains. _EMGFlow_ supports this need through batch-processing, allowing users to either semi- or fully automate the treatment of sEMG recordings. To demonstrate, we use data from PeakAffectDS [@greene_peakaffectds_2022], a collection of physiological signals that includes two channels of facial sEMG, labelled Zyg and Cor, capturing Zygomaticus major and Corrugator supercilii muscle activity respectively. We begin by defining the path to the directory containing our raw, uncleaned files stored in plaintext (.csv) format. We then apply a notch filter to remove the AC mains noise introduced by the recording system’s power source, a common initial step in preprocessing raw sEMG signals.

```python
import EMGFlow

# Get path dictionary
path_names = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(path_names)

# Sampling rate
sampling_rate = 2000

# Filter parameters
notch_vals = [(50, 5)]

# Columns containing data for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# Apply notch filters
EMGFlow.NotchFilterSignals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)
```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Additional arguments allow users to customize which files are selected and how they are processed. Filtering functions accept an optional regex argument, allowing users to apply filters to specific files. Most functions use common sense defaults, which can be modified task-wide or for select cases. For example, in North America, mains electricity is nominally supplied at 120 VAC 60 Hz, while other countries may supply power at 200-240 VAC 50Hz. This variation in frequency requires different notch filter settings depending on where the data were recorded. _EMGFlow_ accommodates this need by allowing the user to specify the frequency and quality factor of the applied filter. Extending our first example, we now apply an additional notch filter to a subset of files exhibiting noise at 150 Hz, the 3rd harmonic of the mains source.

```python
# Filter parameters for files that start with "08" or "11"
notch_vals_extra = [(150,25)]
reg_pat = '^(08|11)'

# Apply extra notch filters
EMGFlow.NotchFilterSignals(path_names['Notch'], path_names['Notch'], sampling_rate, notch_vals_extra, cols, expression=reg_pat)
```

## Visualization of Preprocessing Stages

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The application of a bandpass filter is often the second stage in preprocessing sEMG signals, as it isolates the frequency spectrum of human muscle activity. Signals are commonly filtered to the 10-500 Hz range [@livingstone_deficits_2016; @mcmanus_analysis_2020; @sato_emotional_2021; @tamietto_unseen_2009], though precise filter corner frequencies vary by research domain and approach [@abadi_decaf_2015]. After filtering, data can be further smoothed to remove high-frequency noise and outliers in preparation for the extraction of temporal features. The default smoother is RMS, equal to the square root of the total power in the sEMG signal and commonly used to estimate signal amplitude [@mcmanus_analysis_2020]. Additional filter options are provided, including boxcar, Gaussian, and LOESS. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_EMGFlow_ provides an interactive Shiny dashboard to visualize the effects of preprocessing on sEMG signals. Preprocessing stages can be displayed simultaneously or shown individually with options for Notch, Bandpass, and Smoothing steps. Users can select the file for visualization using the Files dropdown box. The dashboard is generated from a list of file paths containing files at different stages of preprocessing. Here, our example shows how signals are further bandpass filtered and smoothed, with results visualized using the dashboard. 

```python
# Filter and smoothing parameters
band_low = 20
band_high = 140
smooth_window = 50

# Apply bandpass filter
EMGFlow.BandpassFilterSignals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)

# Apply smoothing filter
EMGFlow.SmoothFilterSignals(path_names['Bandpass'], path_names['Smooth'], smooth_window, cols)

# Set units and column to plot
col = 'EMG_zyg'
units = 'mV

# Plot data on the "EMG_zyg" column
EMGFlow.GenPlotDash(path_names, col, units)
```

![Figure 1](figure1.png)
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Figure 1:** _EMGFlow_'s interactive dashboard visualizing effects of different preprocessing stages on batch processed files.

## The nature of electromyographic recordings

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;To better understand the range of features extracted by _EMGFlow_, we begin with a review of surface electromyography as a recording instrument. Nearly all body movement occurs by muscle contraction. During contraction, nerve impulses sent from motoneurons cause muscle fibers innervated by the axon to discharge, creating a motor unit action potential [@mcmanus_analysis_2020]. The speed at which action potentials propogate down the fibre is called muscle fiber conduction velocity. Each motor unit firing results in a force twitch. The superposition of these twiches over time produces a sustained force that enables functional muscle activity, such as lifting or smiling [@de_luca_practicum_2008]. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Surface electromyography measures voltage difference across muscle fibers generated by action potentials, producing a voltage timeseries that quantifies muscle activity [@fridlund_guidelines_1986]. It is from this voltage timeseries that statistical features are extracted.

## Feature Extraction Routines

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Following data preprocessing, the signal files are ready for feature extraction. _EMGFlow_ extracts 32 features that capture information in both time and frequency domains. The set of 17 time-domain features capture standard statistical moments, including mean, variance, skew, and kurtosis, along with sEMG-specific measures. These include features such as Willison amplitude, an indicator of motor unit firing calculated as the number of times the sEMG amplitude exceeds a threshold, and log-detector, an estimate of the exerted muscle force [@tkach_study_2010]. 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A set of 15 frequency-domain features are also extracted, providing information on the shape and distribution of the signal’s power spectrum. Measures such as median frequency [@phinyomark2009novel] provide insight into changes in muscle fibre conduction velocity and are used in the assessment of muscle fatigue [@van1983changes; @lindstrom1977electromyographic; @mcmanus_analysis_2020]. Standard frequency measures include spectral centroid, flatness, entropy, and roll-off. One novel sEMG feature introduced here is Twitch Ratio, an adaptation of Alpha Ratio from speech signal analysis [@eyben_geneva_2016]. Twitch Ratio is defined as the ratio of energy contained in the upper versus lower power spectrum, with a threshold of 60 Hz to delineate slow- and fast-twitch muscles fibres [@hegedus_adaptation_2020].

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_EMGFlow_ has been designed to allow researchers without extensive knowledge of signal processing to analyze sEMG data. Here we present a simple workflow example that produces extracted features in only two lines of code. The example datasets used below are available with the package, and can be generated with the `make_sample_data` function. This function generates sample data files, and returns a series of file paths required for subsequent preprocessing steps. The `CleanSignals` function is a high-level wrapper that sequentially calls the three preprocessing functions for applying notch, bandpass and smoothing filters.

```python
import EMGFlow

# Get path dictionary
path_names = EMGFlow.make_paths()

# Load sample data
EMGFlow.make_sample_data(path_names)

# Preprocess signals
EMGFlow.CleanSignals(path_names, sampling_rate = 2000)

# Extract features and save results in "Features.csv" in feature_path
df = EMGFlow.ExtractFeatures(path_names, sampling_rate = 2000)

"""
df dataframe contains

        File_ID     EMG_zyg_Min   ...     EMG_cor_Spec_Rolloff  EMG_cor_Spec_Bandwidth
0  sample_data.csv  0.002859      ...     4                     196.068942

[1 rows x 65 columns]
"""
```

# Community Guidelines

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;We welcome contributions to the project. These can be initiated through the project's issue tracker or via a pull request. Suggestions for feature enhancements, tips, as well as general questions and concerns, can also be expressed through direct interaction with contributors and developers.

# Declaration of Generative AI and AI-Assisted Technologies in the Writing Process
During the preparation of this work, the authors used GPT-4o to edit a final draft of the manuscript for flow, tone, and grammatical correctness. After using this tool, the authors reviewed and edited the content as needed and take full responsibility for the content of the publication.

# Acknowledgements

We acknowledge the support of the Natural Sciences and Engineering Research Council of Canada (NSERC), (#2023-03786), and from the Faculty of Science, Ontario Tech University.

# Author contributions

S.R.L. conceptualised the project. W.L.C. and S.R.L. designed the toolbox functionality. W.L.C. wrote the toolbox code. W.L.C. created and maintained the Github repository. W.L.C. prepared figures for manuscript and Github repository. W.L.C. and S.R.L prepared the manuscript and approved the final version of the manuscript for submission.

# References