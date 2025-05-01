# `FileAccess` Module Documentation

These functions provide helper methods for accessing files, and are mostly used internally by the package.

## Module Structure

```mermaid
mindmap
    root((EMGFlow))
        AF(File Access)
            MakePaths
            MakeSampleData
            ReadFileType
            MapFiles
            ConvertMapFiles
        DO(Detect Outliers)
        EF(Extract Features)
        PlS(Plot Signals)
        PrS(Preprocess Signals)
```

## `MakePaths`

**Description**

`MakePaths` generates a file structure for signal file processing, and returns a dictionary of the locations of these files.

A "Data" folder is created, with "Raw", "Notch", "Bandpass", "Smooth" and "Feature" subfolders. Alternatively, a path can be provided for these subfolders to be created in instead.

```python
MakePaths(root=None)
```

**Parameters**

`root`: str (None)
- Root of the data to be generated. The default is None.

**Returns**

`path_dict`: dict (str)
- A dictionary of file locations with keys for the stage in the processing pipeline.

**Example**

```python
# Create folders and get locations
path_names = EMGFlow.MakePaths()
```

## `MakeSampleData`

**Description**

`MakeSampleData` generates sample data in the "Raw" folder of a provided dictionary of file locations.

```python
MakeSampleData(path_names)
```

**Parameters**

`path_names`: dict (str)
- A dictionary of file locations

**Returns**

`None`

**Error**

Raises an error if `path_names` does not contain a `Raw` path key.

**Example**

```python
# Create file paths, then create sample data
path_names = EMGFlow.MakePaths()
EMGFlow.MakeSampleData(path_names)
```

## `ReadFileType`

**Description**

`ReadFileType` is a safe wrapper for reading files of a given extension.

```python
ReadFileType(path, file_ext)
```

**Parameters**

`path`: str
- String filepath of file to read.

`file_ext`: str
- String extension of the files to read.

**Returns**

`ReadFileType`: pd.DataFrame
- Returns a Pandas dataframe of the file contents.

**Error**

Raises an error if the file could not be read.

Raises an error if an unsupported file format was provided for `file_ext`.

**Example**

```python
# Read a csv file
path = 'data/raw/file01.csv'
ext = 'csv'
df = EMGFlow.ReadFileType(path, ext)
```



## `MapFiles`

**Description**

`MapFiles` generates a dictionary of file name and location keys/values from a folder and its subfolders.

```python
MapFiles(in_path, file_ext='csv', expression=None)
```

**Parameters**

`in_path`: str
- String filepath to a directory containing Signal files.

`file_ext`: str ("csv")
- String extension of the files to read. The default is `'csv'`.

`expression`: str (None)
- Optional regular expression. If provided, only maps files whose names match the regular expression matches.

**Returns**

`MapFiles`: dict
- Returns a dictionary of file names and locations keys/values.

**Error**

Raises an error if `expression` is not a valid regular expression.

**Example**

```python
# Map all csv files in 'dataFiles' folder and subfolders
file_loc1 = EMGFlow.MapFiles('/data')

# Map all csv files in 'dataFiles' folder and subfolders
# that start with 'DATA_'
file_loc2 = EMGFlow.MapFiles('/data', expression='^DATA_')
```



## `ConvertMapFiles`

**Description**

A more advanced version of `MapFiles` that can coerce other data types into the `MapFiles` format.

If provided a dictionary (assumed to be a file location map), it will return it, filtered by `expression` if provided.

```python
ConvertMapFiles(fileObj, file_ext='csv', experssion=None)
```

**Parameters**

`fileObj`: str, dict
- Any filepath data type supported by the function. Supported data types are: string filepath, or filepath dictionary.

`file_ext`: str ("csv")
- Extension of the files to read. The default is 'csv'.

`expression`: str (None)
- Optional regular expression. If provided, only maps files whose names match the regular expression matches.

**Returns**

`ConvertMapFiles`: dict
- Returns a dictionary of file names and locations keys/values.

**Error**

Raises an error if provided an unsupported file type for `fileObj` is provided.

Raises an error if `expression` is not a valid regular expression.

**Example**

```python
# Read in file locations normally
file_loc1 = EMGFlow.ConvertMapFiles('/data')

# Filter an existing dataframe with a regular expression
file_loc2 = EMGFlow.ConvertMapFiles(file_loc1, expression='^01')
```



## `MapFilesFuse`


**Description**

Combines multiple dictionaries of mapped files (see `MapFiles`) into a Pandas DataFrame.

Assumes that the files contained in the first dictionary are present in each of the following dictionaries.

```python
MapFilesFuse(filedirs, names)
```

**Parameters**

`filedirs`:  dict list
- List of dictionaries assumed to contain file maps.

`names`: str list
- List of names to use for columns, same order as filedirs

**Returns**

`MapFilesFuse`: pd.DataFrame
- Returns a Pandas DataFrame containing each file, and their location for each directory.

**Error**

Raises an error if files contained in the first element of `filedirs` is not contained in the other directories

**Example**

```python
# Create file directory dictionaries
dir_raw = EMGFlow.ConvertMapFiles('/data/raw')
notch_path = EMGFlow.ConvertMapFiles('/data/notch')
band_path = EMGFlow.ConvertMapFiles('/data/bandpass')

# Create dictionary list and names
filedirs = [dir_raw, notch_path, band_path]
names = ['raw', 'notch', 'bandpass']

# Create data frame
df_dirs = EMGFlow.MapFilesFuse(filedirs, names)
```