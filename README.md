# UOIT-Thesis

## About The Data Files

The PeakAffectDS contains the physiological records of participants during the viewing of videos designed to trigger emotional responses.

51 participants were involved in the study. They each viewed a neutral video to effectively reset their emotions, followed by an emotional video to capture their emotions. This process was repeated 6 times to capture 6 different emotions: calm, happy, sad, angry, fearful, disgust.

During the viewing, the participants were attached to different machines that could record their physiological data. This included: An EMG for the zygomaticus (cheek muscle, associated with positive emotion), an EMG for the corrugator (brow muscle, associated with negative emotion), an ECG, and a respirator (?). This data was recorded in volts over the duration of each video, with an associated timestamp. This resulted in 12 physiological files for each participant (6 neutral and 6 emotional).

In addition, each participant had an associated perceptual file, which contained summaries about each of the emotional videos viewed. This included: the video filename, the felt emotional response, the valence (alignment) of the emotion, and the arousal (intensity) of the emotion. 

Overall data makeup:

51 Participants
- Perceptual rating file
    - Timestamps of "peak" emotional events
    - Arousal (intensity of emotion)
    - Valence (alignment of emotion - "good" or "bad")
- 12 physiology files
    - Timestamp
    - EMG Zygomaticus
    - EMG Corrugator
    - ECG
    - Respirator (?)
    - Peak event marker
        - 0 &larr; None
        - 1 &larr; Chills
        - 2 &larr; Tears
        - 3 &larr; Startle

---

## First Milestone

The first step is to open up the data and to look at the physiology files. We will need to make power spectrum graphs of the voltages of the different features over time to try and identify possible noise introduced by the machines. Since the machines are powered by AC energy, there is a 50 Hz signal that can interfere with some of the records, so we will need to identify where this is happening and use a Notch filter to remove it.

---

## Equipment

### Zygomatic EMG

- https://www.sciencedirect.com/topics/medicine-and-dentistry/facial-electromyography
- https://www.researchgate.net/figure/Mean-zygomatic-and-corrugator-electromyography-EMG-activity-as-a-function-of_fig2_336518194
- https://www.sciencedirect.com/book/9780123869159/measures-of-personality-and-social-psychological-constructs
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6976919/
    - When the zygomaticus major muscle contracts, it lifts the corners of the mouth, which constitutes a smile.
    - The sensors attached to this muscle measure the degree to which this muscle is activated, and records it as voltage.

### Corrugator EMG

- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6976919/
    - When the corrugator supercilii contracts, it pulls the brow downwards, which constitutes a frown.
    - The sensors attached to this muscle measure the degree to which this muscle is activated, and records it as voltage.

### ECG

- https://www.sciencedirect.com/science/article/abs/pii/S1746809418300636
    - An ECG records the electrucal activity of the heart. These signals can be further investigated to determine aspects of heart functions, suchas heatbeats, heart abnormalities, emotions and biometric identification
    - In this project we will focus on the emotional aspects and relationships.

### Respiration

- https://www.nature.com/articles/s41746-021-00493-6
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7665156/

---

## Noise

- https://dsp.stackexchange.com/questions/78426/how-to-differentiate-between-line-frequency-50hz-and-the-signal-frequency-of-5

The data files contain noise in the 50 Hz range due to the 50 Hz AC power being recieved by the devices (the standard for New Zealand).

---

## Python Pakages Notes for Literature Review

https://socthesis.fas.harvard.edu/files/socseniorthesis/files/pres-litreview.pdf


Possible packages
- [NeuroKit2](https://pypi.org/project/neurokit2/)
    - https://link.springer.com/article/10.3758/s13428-020-01516-y
        - https://www.sciencedirect.com/science/article/abs/pii/S0010945218304386?via%3Dihub
        - https://link.springer.com/article/10.1007/s10827-018-0702-z
        - https://www.science.org/doi/10.1126/science.aac4716
        - https://www.frontiersin.org/articles/10.3389/fncom.2015.00030/full
- [SciPy](https://scipy.org/)
- [pyemgpipeline](https://pypi.org/project/pyemgpipeline/)
    - https://www.theoj.org/joss-papers/joss.04156/10.21105.joss.04156.pdf
- [MNE](https://mne.tools/stable/index.html)
    - https://github.com/mne-tools/mne-python
- [BioSPPy](https://github.com/PIA-Group/BioSPPy)
    - https://biosppy.readthedocs.io/en/latest/
- [PySiology](https://github.com/Gabrock94/Pysiology)
- [PsPM](https://github.com/bachlab/PsPM)
    - This package is for MatLab, not Python
- [pyphysio](https://github.com/MPBA/pyphysio)
    - https://www.sciencedirect.com/science/article/pii/S2352711019301839
- [py-ECG-Detectors](https://github.com/berndporr/py-ecg-detectors)
- [BIOPEAKS](https://github.com/JanCBrammer/biopeaks)
- [EMG-Signal-Processing-Library](https://github.com/cancui/EMG-Signal-Processing-Library)

Literature review
- Need to use packages to do things more simply
- Created by people with experience in the area
- Makes the work easier for people doing things in the same area
- Develops a common practice for working with the field

### Introduction

Processing physiological data is a complicated process that involves many complicated steps to perform. Fortunately, there are many different packages that can be used to make this work easier, condensing these processes down into simple function calls. These packages were created by people with experience in the area to help developers working on similar problems keep a more streamlined and understandable workflow. These packages help develop common practices for the types of problems they deal with, and provide support for errors encountered when working with them.

### Packages

NeuroKit2 is a toolkit for working with neurophysiological signals. It provides many different functions needed to process these signals. NeuroKit2 is intended to help alleviate the "reproducibility crisis" of neuroscience - a problem caused by the complexity, ambiguity and inaccessibility of development pipelines, by offering a free, comprehensive solution. This includes a series of functions that help every step of the way when working with ECG, RSP, EMG, EDA and EOG signals, also providing functions that can summarise the signals it works with, and extract features.

SciPy is a broad package that contains different algorithms for many applications in computing. Part of this includes the `signal` module, containing methods that help the processing of signals, similar to the work being done in this project. SciPy is a widely known package, that is optimized for high performance, and is well documented with many resources and tutorials on how to use it.

PyEMGPipeline is a more specialized package that helps with EMG signal processing. The package is divided into processors, wrappers and plots. The processors are a collection of functions that can be used in different steps of processing the signals during a workflow. The wrappers are classes that represent different forms of the data being worked with, providing class methods and parameters that make accessing and interacting with the data easier. The plots are a collection of functions that make plotting the data easier, and can make adjusting related parameters easier.

MNE is a large scale package with broad applications for exploring, analyzing and displaying physiological data. This includes MEG, EEG, sEEG, ECoG, and many more kinds of signals. MNE provides a large amount of support, with tutorials, how-to examples, and a large amount of documentation for all of the classes, functions and methods in the package. It also has an online forum where users can share problems and troubleshooting tips. The MNE package is also available to use in MatLab and C.

BioSPPy is a small package designed for processing biological signals in Python. It has a collection of functions that can process signals such as PPG, ECG, EDA, EEG, EMG and respiration signals. It can also be used to analyze these signals using pattern recognition.

Pysiology is a smaller package that helps in the analysis of EMG, ECG and GSR signals.

pyphysio contains algorithms that aid in the analysis of physiological signals, such as ECG, BVP, EDA, inertial and fNIRS signals. pyphysio was created to help combat the lack of open-source signal processing tools available, which negatively impacts the control developers have over their data. pyphysio offers more transparent and customizable functions, and can serve as a basis for machine learning modules. The algorithms in the package include: estimators that change signals to one of a different type, filters that filter a given signal, indicators that produce values from the signal, segmentators that produce a series of segments from a signal, and tools that produce arbitrary data from a signal.

py-ECG-detectors is a small library that helps with the detection and analysis of heartbeats. It provides 8 different algorithms that can detect heartbeats in ECGs, as well as a large collection of tools to analyse the heartrate.

BIOPEAKS is a Python library that provides a graphical user interface for the feature extraction of ECG, PPG and respiration physiological signals. It is able to read files in biosignal, or plain text format, and allows for the interactive visualization of these signals. It can perform automatic feature detection and filtering, as well as providing manual methods of editing the signals. This analysis can be done across multiple files, with the package allowing for batch processing. Once the editing is completed, the interface allows for the exporting of the data for further analysis.

EMG-Signal-Processing-Library is a specialized library for processing EMG signals. It has the capabilities for processing EMG signals in real-time, using algorithms that can run in constant time with respect to the sampling rate of the signals they are working with. The library also has an implementation in C.

### Project

When data is being collected from machines, error can be introduced by many different sources. In this project, noise can be introduced by the 50 Hz AC power being used with the EMG machine. This means the data must examined, cleaned and prepared before it is used in analysis.

The pyemgpipeline package contains a function `plot_emg()` that can plot EMG signals. However, it was straightforward enough to accomplish this with matplotlib, and there were no other needs from the package so it was avoided in favor of matplotlib.

#### PSD Graph

NeuroKit2 contains a useful function `nk.signal_psd()`, which allows for the conversion of signals (tables of voltage over time) to power spectrum density graphs. These graphs show the power being given off by different frequencies in the signal, which provides insight to the components of the overall signal. This allows the signal to be visualized in terms of frequency, and the noise to be identified visually. This helped identify noise in the primary harmonic of 50 Hz, as well additional noise in the upper harmonics - 150 Hz, 250 Hz, ..., 950 Hz.

MNE also contains useful functions for processing EMG data and creating PSD graphs, but was not used. MNE is aimed towards interpreting data from .fif files, a proprietary file format. This project takes a more open source approach, instead involving reading data from .csv files. Using open source software offers advantages, as neuroscience suffers from a "reproducibility crisis" (Maizey & Tzavella, 2019). Many of the processes involved are proprietary, and made inaccessible to many. By using open source software, the project is made more transparent, and allows the results to be reproduced. Further, since this project is intended to provide features that can be used in the studies of others, using open source software will allow the results to be more widely accessible to researchers.

#### Reproducibility Crisis

In their report, Topalidou et al. commented how models need to be reproducable so they can be tested, evaluated, criticized, or modified in some way. This is necessary to verify the accuracy of models, adjust them in some way if needed, or to build upon them to extend  application. If a model cannot be reproduced, it is not possible to further our understanding of the subject, forcing us to rediscover a process that someone has already completed. The authors mention a situation where they were exploring a topic, and asked the research team who made the model for their code, only to discover that the code called on libraries they did not have access to. Ultimately, they had to entirely reproduce the code from scratch just to begin their study.

In their report, Huber, Potter and Huszar discuss the "reproducibility crisis" of neuroscience - the problem of incentivising unreliable research being published to advance careers when at the same time discouraging attempts to reproduce results.

#### Noise Removal

To remove the noise from the signal, the signal module in SciPy contains useful functions. The `scipy.signal.iirnotch()` function creates a notch filter for a given frequency and Q-factor. A notch filter is a filter for a signal that removes a specific frequency, with a given intensity, the Q-factor. A small Q-score increases the intensity of the filter, but risks removing surrounding frequencies unintentionally. This notch filter can then be applied to a signal to remove the frequency specified using another function - `scipy.signal.lfilter()`

#### Export

Once this was accomplished, the data was exported as a csv file (following the same format it was read in with) using the Pandas `to_csv()` method.

--

## Toolboxes

Toolboxes that can be used to explore the data

[PhysioLab](https://neurorehablab.arditi.pt/tools/physiolab/)

---

## Other

Reference manager: Zotero