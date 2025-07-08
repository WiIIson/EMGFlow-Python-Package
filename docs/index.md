---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "EMGFlow"
  text: 
  tagline: The open workflow for EMG signal processing and feature extraction
  image:
    src: /EMGFlow.png
    alt: EMGFlow_sticker
  actions:
    - theme: brand
      text: What is EMGFlow?
      link: /guide/what-is-emgflow
    - theme: alt
      text: Processing Steps
      link: /guide/processing-steps
    - theme: alt
      text: GitHub
      link: https://github.com/WiIIson/EMGFlow-Python-Package

features:
  - icon: 
      light: 'icons/filter2.svg'
      dark: 'icons/filter-dark2.svg'
    title: Signal Preprocessing
    details: Advanced cleaning routines produce optimal sEMG signal quality
  - icon: 
      light: 'icons/automation.svg'
      dark: 'icons/automation-dark.svg'
    title: Automated pipeline
    details: Batch processing enables a hands-off approach to large datasets
  - icon: 
      light: 'icons/features.svg'
      dark: 'icons/features-dark.svg'
    title: Feature extraction
    details: Provides extraction of 33 features across temporal and spectral domains
---

