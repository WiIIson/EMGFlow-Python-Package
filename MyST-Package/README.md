# EMGT Package Documentation

## Overview

The EMGT (EMG Toolkit) package is a general package for the analysis of EMG signals in Python.

## SignalFilterer Module

The `EMGT.SignalFilterer` module is designed to handle the pre-processing and analysis of EMG files. It contains key functions such as `NotchFilterSignals`, `BandpassFilterSignals`, `SmoothFilterSignals` and `AnalyzeSignals`, which make up the main part of the package's workflow.

## OutlierFinder Module

The `EMGT.OutlierFinder` module is designed to assist with finding outliers among your EMG files that may require special case filters.

## PlotSubjects Module

The `EMGT.PlotSubjects` module is designed to assist with visualizing your EMG signals, such as to compare files and visually identify outliers.