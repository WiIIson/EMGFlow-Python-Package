---

---

# What is EMGFlow?

_EMGFlow_ is an open-source Python package for preprocessing and extracting features from surface electromyographic (sEMG) signals. It has been designed to facilitate the analysis of large datasets through batch processing of signal files, a common requirement in machine learning.

<div class="tip custom-block" style="padding-top: 8px">

Want to see it in action? Skip to the [Quickstart](getting-started#quickstart).

</div>

## Statement of need

Although several packages process physiological and neurological signals, support for sEMG has remained limited. Many lack a comprehensive feature set for sEMG, forcing researchers to use a patchwork of tools. Others focus on event detection with GUI-centric workflows that suit continuous recordings of a single participant, but complicate batch feature extraction common in machine learning.

_EMGFlow_, a portmanteau of EMG and Workflow, fills this gap by providing a flexible pipeline for extracting a wide range of sEMG features, with a scalable design suited for large datasets. An overview of package metadata is presented in Table 1.

| Metadata| Description|
|:--------|:-----------|
| License |GPLv3 |
| Implementation | Python >= 3.9 |
| Code repository | https://github.com/WiIIson/EMGFlow-Python-Package |
| Documentation | https://wiiison.github.io/EMGFlow-Python-Package |
| PyPI installation | `pip install EMGFlow` |

<figcaption>
    Table 1: _EMGFlow_ package metadata.
</figcaption>

## Use cases

- **Machine learning** <br><br>Extracting features from large datasets is a common task in machine learning and quantitative domains. _EMGFlow_ supports this need through batch-processing, allowing users to either semi- or fully automate the treatment of sEMG recordings.

- **Experimental methods** <br><br> EMGFlow is ideal for analysing data recorded from participants using standard experimental techniques (e.g., within/between/mixed designs). Researchers and clinicians without extensive knowledge of sEMG processing can analyse electromyographyic recordings with only a few lines of code. _EMGFlow_ was designed with researchers in mind to streamline the process of cleaning and extraction of research-relevant features. Most functions in EMGFlow use common sense defaults, drawn from standard in the physiological and psychologcical literature, to generate reliable and reproducible results.

## Community Guidelines

We welcome contributions to the project. Contributions are welcome via issues or pull requests. Suggestions for features, usage tips, and questions can also be raised through [GitHub Discussions](https://github.com/WiIIson/EMGFlow-Python-Package/discussions). You can also contact us over email.
