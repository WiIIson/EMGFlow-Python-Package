---

---

# What is EMGFLow?

_EMGFlow_ is an open-source Python package for preprocessing and extracting features from surface electromyographic (sEMG) signals. It has been designed to facilitate the analysis of large datasets through batch processing of signal files, a common requirement in machine learning.

<div class="tip custom-block" style="padding-top: 8px">

Want to see it in action? Skip to the [Quickstart](getting-started).

</div>

## Statement of need

Several existing packages support physiological and neurological signal processing, but few provide comprehensive support for sEMG data. Most tools offer only a limited set of extractable sEMG features, forcing researchers to combine multiple packages into a fragmented workflow. Other tools primarily focus on event detection within individual recordings and rely heavily on graphical user interfaces (GUIs), requiring considerable manual intervention. While suitable for processing individual, continuous recordings, these approaches become cumbersome when applied to larger datasets commonly used in machine learning.

_EMGFlow_, a portmanteau of EMG and Workflow, addresses this limitation by offering a flexible processing pipeline capable of extracting a broad array of sEMG features. Its scalable architecture is specifically designed to handle extensive datasets efficiently, facilitating analysis in machine learning contexts.

## Use cases

- **Machine learning** <br><br>Extracting features from large datasets is a common task in machine learning and quantitative domains. _EMGFlow_ supports this need through batch-processing, allowing users to either semi- or fully automate the treatment of sEMG recordings.

- **Experimental methods** <br><br> EMGFlow is ideal for analysing data recorded from participants using standard experimental techniques (e.g., within/between/mixed designs). Researchers and clinicians without extensive knowledge of sEMG processing can analyse electromyographyic recordings with only a few lines of code. _EMGFlow_ was designed with researchers in mind to streamline the process of cleaning and extraction of research-relevant features. Most functions in EMGFlow use common sense defaults, drawn from standard in the physiological and psychologcical literature, to generate reliable and reproducible results.

## Contributing

We welcome contributions to the project. These can be initiated through [GitHub](https://github.com/WiIIson/EMGFlow-Python-Package) on the project's [issue tracker](https://github.com/WiIIson/EMGFlow-Python-Package/issues) or through a pull request. Suggestions for feature enhancements, tips, as well as general questions and concerns can also be expressed through direct interaction with contributors and developers. You can also contact us over email.

If you experience any challenges with this module such as bugs, test support, or feature requests, please feel free to use this issue tracker.