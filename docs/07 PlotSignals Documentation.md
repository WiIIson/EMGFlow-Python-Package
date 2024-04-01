# PlotSignals Documentation

---

## `GenPlotDash`

**Description:**

Creates a HTML dashboard from a series of signal file paths to compare filtering progress at different stages. Has a side bar menu to navigate the signal file and stage being displayed.

The visualization is created in the default browser, and is opened automatically.

```python
GenPlotDash(in_paths, sampling_rate, col, units, names, expression=None, file_ext='csv')
```

**Parameters:**

`in_paths`: str list
- List of string filepaths to a directories containing Signal files. Directories should contain the same file names, but don't have to keep the same hierarchy.

`sampling_rate`: int/float
- Numerical value of the sampling rate of the `Signal`. This is the number of entries recorded per second, or the inverse of the difference in time between entries.

`col`: str
- String column name to display in the visualization.

`units`: str
- Units to use for the y axis of the plot, same units used for the column values.

`names`: str list
- List of names to use as the legend for the different paths provided

`expression`: str (None)
- String regular expression. If provided, will only create visualizations for `Signal` files whose names match the regular expression, and will ignore everything else.

`file_ext`: str ("csv")
- String extension of the files to read. Any file in `in_path` with this extension will be considered to be a `Signal` file, and treated as such. The default is `'csv'`.

**Returns:**

`GenPlotDash`: None

**Example:**

```python
raw_path = '/data/raw/'
notch_path = '/data/notch/'
band_path = '/data/bandpass/'
s_paths = [raw_path, notch_path, band_path]

sr = 2000
col = 'col1'
units = 'mV'
names = ['raw', 'notch', 'bandpass']

GenPlotDash(s_paths, sr, col, units, names)
```