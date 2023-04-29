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

- [NeuroKit2](https://pypi.org/project/neurokit2/)
- [pyemgpipeline](https://pypi.org/project/pyemgpipeline/)
    - https://www.theoj.org/joss-papers/joss.04156/10.21105.joss.04156.pdf
- [MNE](https://mne.tools/stable/index.html)
- [BioSPPy](https://github.com/PIA-Group/BioSPPy)
- [PySiology](https://github.com/Gabrock94/Pysiology)
- [PsPM](https://github.com/bachlab/PsPM)
- [pyphysio](https://github.com/MPBA/pyphysio)
- [py-ECG-Detectors](https://github.com/berndporr/py-ecg-detectors)
- [BIOPEAKS](https://github.com/JanCBrammer/biopeaks)
- [EMG-Signal-Processing-Library](https://github.com/cancui/EMG-Signal-Processing-Library)

---

## Other

Reference manager: Zotero