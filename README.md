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

Processing physiological data is a complicated process that involves many complicated steps to perform. Fortunately, there are many different packages that can be used to make this work easier, condensing these processes down into simple function calls. These packages were created by people with experience in the area to help developers working on similar problems keep a more streamlined and understandable workflow. These packages help develop common practices for the types of problems they deal with, and provide support for errors encountered when working with them.

NeuroKit2 is a toolkit for working with neurophysiological signals. It provides many different functions needed to process these signals. NeuroKit2 is intended to help alleviate the "reproducibility crisis" of neuroscience - a problem caused by the complexity, ambiguity and inaccessibility of development pipelines, by offering a free, comprehensive solution. This includes a series of functions that help every step of the way when working with ECG, RSP, EMG, EDA and EOG signals, also providing functions that can summarise the signals it works with, and extract features.

PyEMGPipeline is a more specialized package that helps with EMG signal processing. The package is divided into processors, wrappers and plots. The processors are a collection of functions that can be used in different steps of processing the signals during a workflow. The wrappers are classes that represent different forms of the data being worked with, providing class methods and parameters that make accessing and interacting with the data easier. The plots are a collection of functions that make plotting the data easier, and can make adjusting related parameters easier.

MNE is a large scale package with broad applications for exploring, analyzing and displaying physiological data. This includes MEG, EEG, sEEG, ECoG, and many more kinds of signals. MNE provides a large amount of support, with tutorials, how-to examples, and a large amount of documentation for all of the classes, functions and methods in the package. It also has an online forum where users can share problems and troubleshooting tips. The MNE package is also available to use in MatLab and C.

BioSPPy is a small package designed for processing biological signals in Python. It has a collection of functions that can process signals such as PPG, ECG, EDA, EEG, EMG and respiration signals. It can also be used to analyze these signals using pattern recognition.

Pysiology is a smaller package that helps in the analysis of EMG, ECG and GSR signals.

pyphysio contains algorithms that aid in the analysis of physiological signals, such as ECG, BVP, EDA, inertial and fNIRS signals. pyphysio was created to help combat the lack of open-source signal processing tools available, which negatively impacts the control developers have over their data. pyphysio offers more transparent and customizable functions, and can serve as a basis for machine learning modules. The algorithms in the package include: estimators that change signals to one of a different type, filters that filter a given signal, indicators that produce values from the signal, segmentators that produce a series of segments from a signal, and tools that produce arbitrary data from a signal.

py-ECG-detectors is a small library that helps with the detection and analysis of heartbeats. It provides 8 different algorithms that can detect heartbeats in ECGs, as well as a large collection of tools to analyse the heartrate.

BIOPEAKS is a Python library that provides a graphical user interface for the feature extraction of ECG, PPG and respiration physiological signals. It is able to read files in biosignal, or plain text format, and allows for the interactive visualization of these signals. It can perform automatic feature detection and filtering, as well as providing manual methods of editing the signals. This analysis can be done across multiple files, with the package allowing for batch processing. Once the editing is completed, the interface allows for the exporting of the data for further analysis.

EMG-Signal-Processing-Library is a specialized library for processing EMG signals. It has the capabilities for processing EMG signals in real-time, using algorithms that can run in constant time with respect to the sampling rate of the signals they are working with. The library also has an implementation in C.

---

## Other

Reference manager: Zotero