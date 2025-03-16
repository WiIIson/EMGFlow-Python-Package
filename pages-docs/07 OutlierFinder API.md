# `OutlierFinder` Module Documentation

This module provides methods to help detect signal files that contain outliers. This helps for workflows involving batch processing of files, where it might be harder to determine if there are any patterns, or specific files that need additional filters applied.

---

## `DetectOutliers`

**Description:**

Analyzes signal files and returns a dictionary of file names and locations that are flagged as having outliers in their spectral composition. This can indicate the need for additional filters to be applied.

The function works by interpolating an inverse function from the peaks of the signal's spectrum. The function then calculates the metric average of the differences between the predicted spectrum intensity of the inverse function, and the actual spectrum intensity of the peaks. Finally, if the largest difference between the predicted and actual values is greater than the metric average multiplied by the threshold value, the file is flagged for having an outlier and is added to the dictionary.

```python
DetectOutliers(in_path, sampling_rate, threshold, cols=None, low=None, high=None, metirc=np.median, expression=None, file_ext='csv')
```

**Parameters:**

`in_path`: str
- String filepath to a directory containing Signal files.

`sampling_rate`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`threshold`: int/float
- Number of times greater than the metric calculated for the file to be considered an outlier

`cols`: str (None)
- List of string column names. If provided, will only search for outliers in the specified columns. If left `None`, will search for outliers in each column except for the `'Time'` column.

`low`: int/float
- Minimum frequency range to search for outliers in.

`high`: int/float
- Maximum frequency range to search for outliers in.

`metric`: int/float
- Aggregation metric used to calculate outliers. Can be any function that takes a list of numeric values, and returns a single value. Recommended functions are: `np.median` and `np.mean`.

`expression`: str (None)
- String regular expression. If provided, will only search for outliers in `Signal` files whose names match the regular expression, and will ignore everything else.

`file_ext`: str ("csv")
- String extension of the files to read. Any file in `in_path` with this extension will be considered to be a `Signal` file, and treated as such. The default is `'csv'`.

**Returns:**

`DetectOutliers`: dict
- Returns a dictionary of file names and locations keys/values.

**Error**

Raises an error if `sampling_rate` is less or equal to 0.

Raises an error if `threshold` is less or equal to 0.

Raises an error is `low` is greater than `high`.

Raises an error if `low` or `high` are negative.

Raises an error if `metric` is not a valid summary function.

Raises an error if a column in `cols` is not in a data file.

Raises an error if a file cannot be read in `in_path`.

Raises an error if an unsupported file format was provided for `file_ext`.

**Example:**

```python
in_path = '/data/notch'
sr = 2000
threshold = 5

EMGFlow.DetectOutliers(in_path, sr, threshold)
```