# `access_files` Module

These functions access files, set up file structures for working with sEMG signals, and load EMGFlow's built-in dataset. The functions are mostly used internally by the package.

## Module Structure

```mermaid
mindmap
    root((EMGFlow))
        AF(Access Files)
            make_paths
            make_sample_data
            map_files
            map_files_fuse
            package_citation
            package_version
            read_file_type
        PrS(Preprocess Signals)
        PlS(Plot Signals)
        EF(Extract Features)
```





## `make_paths`

**Description**

Generates a file structure for an EMG workflow, and returns a dictionary of the locations for these files for easy use with EMG processing functions.

Creates '1_raw', '2_notch', '3_bandpass', '4_fwr', '5_screened', '6_filled', '7_smoothed', and '8_feature' subfolders at a given location. If no path is given, will create a 'Data' folder in the current working directory, with these subfolders inside.

```python
def make_paths(root:str=None, raw:str=None)
```

**Parameters**

`root` : str, optional (None)
- The root where the data is generated. The default is None.

`raw` : str, optional (None)
- The path for the raw data. The default is None, in which case a default location is generated.

**Returns**

`path_names` : dict-str
- A dictionary of file locations with keys for stage in the processing pipeline.

**Example**

```python
# Create folders and get locations
path_names = EMGFlow.make_paths()
```





## `make_sample_data`

**Description**

Generates sample data in the 'raw' folder of a provided dictionary of file locations.

Creates '01' and '02' folders, which each contain two sample data files ('01/sample_data_01.csv', '01/sample_data_02.csv', '02/sample_data_03.csv', '02/sample_data_04.csv')

The sample data will not be written if it already exists in the folder.

```python
def make_sample_data(path_names:dict)
```

**Parameters**

`path_names` : dict-str
- A dictionary of file locations with keys for stage in the processing pipeline.

**Raises**

An exception is raised if 'raw' is not a key of the `path_names` dictionary provided.

An exception is raised if the sample data cannot be loaded.

**Returns**

None.

**Example**

```python
# Create file paths, then create sample data
path_names = EMGFlow.make_paths()
EMGFlow.make_sample_data(path_names)
```




## `map_files`

**Description**

Generate a dictionary of file names and locations (keys/values) from the subfiles of a folder.

```python
def map_files(in_path:str, file_ext:str='csv', expression:str=None, base:str=None)
```

**Parameters**

`in_path` : str
- The filepath to a directory to read files.

`file_ext` : str, optional ('csv')
- The file extension for files to read. Only reads files with this extension. The default is 'csv'.

`expression` : str, optional (None)
- A regular expression. If provided, will only count files whose relative paths from 'base' match the regular expression. The default is None.

`base` : str, optional (None)
- The path of the root folder the path keys should start from. Used to track the relative path during recursion. The default is None. 

**Raises**

An exception is raised if `expression` is not None or a valid regular expression.

**Returns**

`file_dirs`: dict-str
- Returns dictionary of file name keys and file path location values.

**Example**

```python
# Map all csv files in 'data' folder and subfolders
file_loc_1 = EMGFlow.map_files('data')

# Map all csv files in 'data' folder that start with 'DATA',
# or in folders that start with 'DATA'
file_loc_2 = EMGFlow.map_files('data', expression='^DATA')
```





## `map_files_fuse`

**Description**

Merge mapped file dictionaries into a single dataframe. Uses 'names' as the column names, and stores the file path to a file in different stages of the processing pipeline.

```python
def map_files_fuse(file_dirs, names)
```

**Parameters**

`file_dirs` :  list-dict-str
- List of file location directories.

`names` : list-str
- List of names to use for file directory columns. Same order as `file_dirs`.

**Raises**

An exception is raised if a file contained in the first file directory (`file_dirs[0]`) is not found in the other file directories.

**Returns**

`path_df` : pd.DataFrame
- A dataframe of file names, and their locations in each file directory.

**Example**

```python
# Create file directory dictionaries
raw_path = EMGFlow.map_files('Data/1_raw')
notch_path = EMGFlow.map_files('Data/2_notch')
band_path = EMGFlow.map_files('Data/3_bandpass')

# Create dictionary list and names
file_dirs = [raw_path, notch_path, band_path]
names = ['1_raw', '2_notch', '3_bandpass']

# Create data frame
dfDirs = EMGFlow.map_files_fuse(file_dirs, names)
```





## `package_citation`

**Description**

Prints citation information.

```python
def package_citation(pkg:str='emgflow')
```

**Parameters**

`pkg` : str, optional ('emgflow')
- The package to print citation information for. The default is 'emgflow'

**Returns**

None.

**Example**

```python
EMGFlow.package_citation()
```





## `package_version`

**Description**

Prints the package version.

```python
def package_version()
```

**Parameters**

None.

**Returns**

None.

**Example**

```python
EMGFlow.package_version()
```





## `read_file_type`

**Description**

Wrapper for reading files of a given extension.

Switches between different reading methods based on the extension provided.

Supported formats that can be read are: 'csv'.

```python
def read_file_type(path:str, file_ext:str)
```

**Parameters**

`path` : str
- The path of the file to read.

`file_ext` : str
- The file extension for files to read. Only reads files with this extension. The default is 'csv'.

**Raises**

An exception is raised if the file could not be read.

An exception is raised if an unsupported file format was provided for `file_ext`.

**Returns**

`file` : pd.DataFrame
- Returns a Pandas dataframe of the file contents.

**Example**

```python
# Read a csv file
path = '/Data/1_raw/01/sample_data_01.csv'
ext = 'csv'
df = EMGFlow.read_file_type(path, ext)
```