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

Surface electromyography (sEMG) is increasingly used to study human physiology and behaviour, spurred by advances in deep learning and wearable sensors. Here, we introduce _EMGFlow_, an open-source Python package designed to simplify the preprocessing and feature extraction of sEMG signals. Tailored for batch processing, EMGFlow efficiently handles large datasets typical in machine learning contexts, extracting a comprehensive set of 33 statistical features across both time and frequency domains. The package integrates regular expression matching to support flexible file selection for preprocessing and feature extraction tasks. _EMGFlow_ uses Pandas DataFrames throughout its workflow to facilitate interoperability with other data analysis tools. An interactive dashboard provides visual comparisons of signals at each preprocessing stage, enhancing user understanding and decision-making. _EMGFlow_ is distributed under the GNU General Public License v3.0 (GPL-3.0) and can be installed directly from PyPI. A dedicated documentation site—complete with detailed guides, API references, and runnable examples—is available at [https://wiiison.github.io/EMGFlow-Python-Package/](https://wiiison.github.io/EMGFlow-Python-Package/).

# Statement of Need

Although several packages exist for processing physiological and neurological signals, support for sEMG has remained limited. Many packages lack a comprehensive set of features that can be extracted from sEMG data, leaving researchers to use a patchwork of tools. Other packages are orientated around event detection in individual recordings and use a GUI-based workflow that requires more manual intervention. While this design works well for processing unedited continuous recordings of a single participant, it complicates the extraction of features from large datasets common to machine learning [@abadi_decaf_2015; @chen_emotion_2022; @koelstra_deap_2012; @schmidt_introducing_2018; @sharma_dataset_2019; @zhang_biovid_2016].

_EMGFlow_, a portmanteau of EMG and Workflow, fills this gap by providing a flexible pipeline for extracting a wide range of sEMG features, with a scalable design suited for large datasets.

# Comparison to Other Packages

Compared to existing toolkits, _EMGFlow_ offers a more comprehensive set of 33 statistical features tailored specifically for sEMG signals [@bota_biosppy_2024; @makowski_neurokit2_2021; @sjak-shie_physiodata_2022; @soleymani_toolbox_2017]. An interactive dashboard visualizes batch processed files rather than individual recordings, allowing the operator to view the effects of preprocessing across multiple datasets simultaneously [@gabrieli_pysiology_2020]. Adjustable filter settings and smoothing functions accommodate different international standards (50 vs. 60 Hz mains AC), a critical detail overlooked by some packages.

# Features

## A Simplified Processing Pipeline

Extracting features from large datasets is fundamental in machine learning and quantitative analyses. _EMGFlow_ supports batch-processing, enabling users to automate fully or semi-automate the treatment of sEMG recordings. Figure 1 illustrates the general pipeline. For demonstration, we use the built-in sample dataset from PeakAffectDS [@greene_peakaffectds_2022], containing data from two facial muscles: Zygomaticus major (Zyg) and Corrugator supercilii (Cor). We begin by creating file structures using `make_paths()`, then generating our sample data with `make_sample_data()`.

_EMGFlow_ has been designed to allow researchers without deep signal-processing expertise to analyze sEMG data, while providing expert users flexability to control each step in the pipeline. Next, the `clean_signals()` function provides a high-level wrapper for automated preprocessing with sensible, literature-based defaults. Advanced users can customize individual processing steps as needed, as demonstrated below. Here, we apply a notch filter to remove AC mains interference, a common preliminary step in sEMG signal preprocessing.

```python
import EMGFlow

# Create processing file structure within '/Data'
path_names = EMGFlow.make_paths()

# Load sample data into Data/Raw
EMGFlow.make_sample_data(path_names)

# Sampling rate (in Hz)
sampling_rate = 2000

# Notch filter parameters (frequency, Q-factor)
notch_vals = [(50, 5)]

# Data columns for preprocessing
cols = ['EMG_zyg', 'EMG_cor']

# Apply notch filter (input path: /Raw, output path: /Notch)
EMGFlow.notch_filter_signals(path_names['Raw'], path_names['Notch'], sampling_rate, notch_vals, cols)
```

![Figure 1](figure1.png)
**Figure 1:** Overview of _EMGFlow_'s processing pipeline.

At each preprocessing step, _EMGFlow_ mirrors the original input file structure, mapping its layout to the concomittant output folder. This approch maintains the researcher's data hierarchy, allowing for easy inspection of results at each stage of processing.

Advanced users can further customize preprocessing via regular expressions to selectively process subsets of files. Default parameters use canonical values widely recommended in the literature, and can be adjusted according to specific requirements. For example, in North America, mains electricity is nominally supplied at 120 VAC 60 Hz, while other countries may supply power at 200-240 VAC 50Hz. This variation in frequency requires different notch filter settings depending on where the data were recorded. Here we apply an additional notch filter to a subset of files belonging to participant 02, that exhibited noise at 150 Hz, the 3rd harmonic of the mains source.

```python
# Secondary notch filter
notch_vals_subset = [(150, 25)]

# Match all .csv files within participant folder '02/'
participant_pattern = '02\/\w+.csv'

# Apply custom notch filter
EMGFlow.notch_filter_signals(path_names['Notch'], path_names['Notch'], sampling_rate, notch_vals_subset, cols, expression=participant_pattern)
```

## Visualization of Preprocessing Stages

A bandpass filter typically follows notch filtering, as it isolates the frequency spectrum of human muscle activity. Signals are commonly filtered to the 10-500 Hz range [@livingstone_deficits_2016; @mcmanus_analysis_2020; @sato_emotional_2021; @tamietto_unseen_2009], though precise filter corner frequencies vary by research domain and approach [@abadi_decaf_2015]. Next, data are smoothed to reduce high-frequency noise and outliers, enhancing temporal feature extraction accuracy. The default smoother is RMS, equal to the square root of the total power in the sEMG signal and commonly used to estimate signal amplitude [@mcmanus_analysis_2020]. Alternative smoothing methods include boxcar, Gaussian, and LOESS.

_EMGFlow_ provides an interactive Shiny dashboard that allows users to visualize and contrast the effects of preprocessing on sEMG signals, as shown in Figure 2. Preprocessing stages can be displayed simultaneously or shown individually with options for Notch, Bandpass, and Smoothing steps. Users can select the file for visualization using the Files dropdown box. The dashboard is generated by extracting paths from the pipeline's file structure. Below, our example shows how signals are further bandpass filtered and smoothed, with results visualized using the dashboard.

```python
# Bandpass and smoothing filter parameters
band_low = 20
band_high = 140
smooth_window = 50

# Apply bandpass filter
EMGFlow.bandpass_filter_signals(path_names['Notch'], path_names['Bandpass'], sampling_rate, band_low, band_high, cols)

# Apply smoothing filter
EMGFlow.smooth_filter_signals(path_names['Bandpass'], path_names['Smooth'], smooth_window, cols)

# Data column and units for plotting
col = 'EMG_zyg'
units = 'mV'

# Plot all "EMG_zyg" data with interactive dashboard
EMGFlow.plot_dashboard(path_names, col, units)
```

![Figure 2](figure2.png)
**Figure 2:** _EMGFlow_'s interactive dashboard shows the effects of preprocessing stages on batch processed files.

## Feature Extraction

We begin with a review of surface electromyography as a recording instrument to better understand the range of features extracted by _EMGFlow_. Nearly all body movement occurs by muscle contraction. During contraction, nerve impulses sent from motoneurons cause muscle fibers innervated by the axon to discharge, creating a motor unit action potential [@mcmanus_analysis_2020]. The speed at which action potentials propogate down the fibre is called muscle fiber conduction velocity. Each motor unit firing results in a force twitch. The superposition of these twiches over time produces a sustained force that enables functional muscle activity, such as lifting or smiling [@de_luca_practicum_2008].

Surface electromyography measures muscle activity by detecting the voltage differences produced as action potentials propagate through contracting muscle fibres. The resulting recordings form a voltage time-series that reflects the intensity and timing of muscle activation [@fridlund_guidelines_1986]. _EMGFlow_ processes these voltage timeseries and extracts 33 features across time and frequency domains, as listed in Table 1. A key contribution of _EMGFlow_ is that all features are computed natively with SciPy primitives; no external feature‑extraction libraries are required [@virtanen_scipy_2020]. All computed features, along with their mathematical definitions, can be found in the Reference section of the Documentation website.

Eighteen time-domain features capture standanrd statistical moments, including mean, variance, skew, and kurtosis, along with sEMG-specific measures. These include features such as Willison amplitude, an indicator of motor unit firing calculated as the number of times the sEMG amplitude exceeds a threshold, and log-detector, an estimate of the exerted muscle force [@tkach_study_2010]. Fifteen frequency-domain features provide information on the shape and distribution of the signal’s power spectrum. Measures such as median frequency [@phinyomark2009novel] provide insight into changes in muscle fibre conduction velocity and are used in the assessment of muscle fatigue [@van1983changes; @lindstrom1977electromyographic; @mcmanus_analysis_2020]. Standard frequency measures include spectral centroid, flatness, entropy, and roll-off. An innovative feature is Twich Ratio, defined as the ratio of energy contained in the upper versus lower power spectrum, with a threshold of 60 Hz to delineate slow- and fast-twitch muscles fibres [@hegedus_adaptation_2020]. Twitch ratio was adapted from Alpha Ratio in speech signal analysis [@eyben_geneva_2016].

| Domain   | Feature |
|:----------|:---------|
| Temporal | minV, maxV, meanV, stdV, skewV, kurtosisV, maxF, IEMG, MAV, MMAV1, MMAV2, SSI, VAR, VOrder, RMS, WL, WAMP, LOG |
| Spectral | MFL, AP, SpecFlux, MDF, MNF, TwitchRatio, TwitchIndex, TwitchSlope, SC, SF, SS, SDec, SEntropy, SRoll, SBW |

**Table 1:** Features extracted from sEMG signals.

Our demonstration concludes with the extraction of features from our processed sEMG signal files. Features are summarized into a single CSV file, containing rows for each file analyzed, as shown below.

```python
# Extract features and save results in "/Feature/Features.csv"
df = EMGFlow.extract_features(path_names, sampling_rate, cols)

# Print first few rows of extracted features table. The “File_ID” column
# contains the local path of files extracted, and the additional columns take
# the format “[Column name]_[Feature name]”.
df.head()
"""
File_ID column contains

      File_ID                EMG_zyg_Min  ...  EMG_cor_Spec_Rolloff  EMG_cor_Spec_Bandwidth
0  01/sample_data_01.csv     0.000826     ...  0.040222              1424.933862
1  01/sample_data_02.csv     0.000740     ...  0.019559              2651.987804
2  02/sample_data_03.csv     0.000780     ...  0.065183              2021.345274
3  02/sample_data_04.csv     0.000660     ...  0.087384              1755.834836

[4 rows x 61 columns]
"""
```

# Documentation, Testing, and Availability

_EMGFlow_ is supported by comprehensive documentation ([https://wiiison.github.io/EMGFlow-Python-Package](https://wiiison.github.io/EMGFlow-Python-Package)), generated with VitePress to provide a modern user experience [@vitepress]. Documentation consists of (i) a Quick-Start tutorial for new users, (ii) an example gallery spanning three-line demonstrations to advanced processing pipelines, and (iii) an API reference annotated with executable code snippets, and mathematical definitions of all features. Package-level mind-maps, rendered with Mermaid.js [@mermaidjs], provide a visual overview of the module hierarchy to assist user orientation.

Code reliability is maintained by an automated test suite, _unittest_, that executes on every GitHub commit via continuous-integration workflows. The complete source code is publicly available on GitHub under the GPL-3.0 licence - [https://github.com/WiIIson/EMGFlow-Python-Package](https://github.com/WiIIson/EMGFlow-Python-Package).

# Community Guidelines

Contributions are encouraged via the project's issue tracker or pull requests. Suggestions for feature enhancements, tips, as well as general questions and concerns, can also be expressed through direct interaction with contributors and developers.

# Declaration of Generative AI and AI-Assisted Technologies in the Writing Process

GPT-4.5 was used to edit the final manuscript draft. Authors carefully reviewed and finalized the content, and take full responsibility for the content of the publication.

# Acknowledgements

We acknowledge the support of the Natural Sciences and Engineering Research Council of Canada (NSERC), (#2023-03786), and from the Faculty of Science, Ontario Tech University.

# Author contributions

S.R.L. conceptualised the project. W.L.C. and S.R.L. designed the toolbox functionality. W.L.C. wrote the toolbox code. W.L.C. created and maintained the Github repository. S.R.L. and W.L.C. created the documentation website. W.L.C. and S.R.L. prepared figures for manuscript and Github repository. S.R.L and W.L.C. prepared the manuscript and approved the final version of the manuscript for submission.

# References