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

## First Milestone

The first step is to open up the data and to look at the physiology files. We will need to make power spectrum graphs of the voltages of the different features over time to try and identify possible noise introduced by the machines. Since the machines are powered by AC energy, there is a 50 Hz signal that can interfere with some of the records, so we will need to identify where this is happening and use a Notch filter to remove it.