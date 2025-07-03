import importlib_resources
import pandas as pd
import re
import os

#
# =============================================================================
#

"""
A collection of functions for accessing files.
"""

#
# =============================================================================
#

def make_paths(root=None):
    """
    Generates a file structure for signal files, and returns a dictionary of
    the locations for these files.
    
    Creates 'Raw', 'Notch', 'Bandpass', 'Smooth', 'Filled', and 'Feature'
    subfolders at a given location. If no path is given, will create a 'Data'
    folder in the current working directory, with these subfolders inside.

    Parameters
    ----------
    root : str, optional
        Root of the data to be generated. The default is None.

    Returns
    -------
    path_names : dict-str
        A dictionary of file locations with keys for stage in the processing
        pipeline.

    """
    
    if root is None:
        root = os.path.join(os.getcwd(), 'Data')
    else:
        root = os.path.normpath(root)
    
    # Create dictionary
    path_names = {
        'Raw':os.path.join(root, '1_raw'),
        'Notch':os.path.join(root, '2_notch'),
        'Bandpass':os.path.join(root, '3_bandpass'),
        'Smooth':os.path.join(root, '4_smooth'),
        'Filled':os.path.join(root, '5_filled'),
        'Feature':os.path.join(root, '6_feature')
    }
    
    # Create folders
    for value in path_names.values():
        os.makedirs(value, exist_ok=True)
    
    # Return dictionary
    return path_names

#
# =============================================================================
#

def make_sample_data(path_names):
    """
    Generates sample data in the 'Raw' folder of a provided dictionary of file
    locations.
    
    Creates '01' and '02' folders, which each contain two sample
    data files ('01/sample_data_01.csv', '01/sample_data_02.csv',
    '02/sample_data_03.csv', '02/sample_data_04.csv')
    
    The sample data will not be written if it already exists in the folder.

    Parameters
    ----------
    path_names : dict-str
        Dictionary of file locations.

    Raises
    ------
    Exception
        An exception is raised if the provided 'path_names' dictionary doesn't
        contain a 'Raw' path key.
    Exception
        An exception is raised if the sample data cannot be loaded.

    Returns
    -------
    None.

    """
    
    # An exception is raised if the provided 'path_names' dictionary doesn't
    # contain a 'Raw' path key.
    if 'Raw' not in path_names:
        raise Exception('Raw path not detected in path_names.')
    
    # Load the sample data
    try:
        sample_data_01 = pd.read_csv(importlib_resources.files("EMGFlow").joinpath(os.path.join("data", "sample_data_01.csv")))
        sample_data_02 = pd.read_csv(importlib_resources.files("EMGFlow").joinpath(os.path.join("data", "sample_data_02.csv")))
        sample_data_03 = pd.read_csv(importlib_resources.files("EMGFlow").joinpath(os.path.join("data", "sample_data_03.csv")))
        sample_data_04 = pd.read_csv(importlib_resources.files("EMGFlow").joinpath(os.path.join("data", "sample_data_04.csv")))
    except:
        # An exception is raised if the sample data cannot be loaded.
        raise Exception('Failed to load EMGFlow sample data.')
    
    # Write the sample data
    os.makedirs(os.path.join(path_names['Raw'], '01'), exist_ok=True)
    os.makedirs(os.path.join(path_names['Raw'], '02'), exist_ok=True)
    
    data_path_01 = os.path.join(path_names['Raw'], '01', 'sample_data_01.csv')
    data_path_02 = os.path.join(path_names['Raw'], '01', 'sample_data_02.csv')
    data_path_03 = os.path.join(path_names['Raw'], '02', 'sample_data_03.csv')
    data_path_04 = os.path.join(path_names['Raw'], '02', 'sample_data_04.csv')
    
    if not os.path.exists(data_path_01):
        sample_data_01.to_csv(data_path_01, index=False)
    if not os.path.exists(data_path_02):
        sample_data_02.to_csv(data_path_02, index=False)
    if not os.path.exists(data_path_03):
        sample_data_03.to_csv(data_path_03, index=False)
    if not os.path.exists(data_path_04):
        sample_data_04.to_csv(data_path_04, index=False)
        

#
# =============================================================================
#

def read_file_type(path, file_ext):
    """
    Safe wrapper for reading files of a given extension.
    
    Switches between different reading methods based on the instructions
    provided.
    
    Supported formats that can be read are: 'csv'.

    Parameters
    ----------
    path : str
        Path of the file to read.
    file_ext : str
        File extension to read.

    Raises
    ------
    Exception
        An exception is raised if the file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.

    Returns
    -------
    file : pd.DataFrame
        Returns a Pandas dataframe of the file contents.

    """
    
    if file_ext == 'csv':
        try:
            file = pd.read_csv(path)
        except:
            raise Exception("CSV file could not be read: " + str(path))
    else:
        raise Exception("Unsupported file format provided: " + str(file_ext))
        
    return file

#
# =============================================================================
#

def map_files(in_path, file_ext='csv', expression=None, base=None):
    """
    Generate a dictionary of file names and locations (keys/values) from the
    subfiles of a folder.
    
    Parameters
    ----------
    in_path : str
        The filepath to a directory to read files.
    file_ext : str, optional
        File extension for files to read. The default is 'csv'.
    expression : str, optional
        A regular expression. If provided, will only count files whose names
        match the regular expression. The default is None.
    base : str, optional
        Path of the root folder the path keys should start from. Used to track
        the relative path during recursion. The default is None. 

    Raises
    ------
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.

    Returns
    -------
    file_dirs : dict-str
        A dictionary of file name keys and file path location values.

    """
    
    # Throw error if Regex does not compile
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Set base path and ensure in_path is absolute
    if base is None:
        if not os.path.isabs(in_path):
            in_path = os.path.join(os.getcwd(), in_path)
        base = in_path
    
    # Build file directory dictionary
    file_dirs = {}
    for file in os.listdir(in_path):
        new_path = os.path.join(in_path, file)
        # Recursively check folders
        if os.path.isdir(new_path):
            subDir = map_files(new_path, file_ext=file_ext, expression=expression, base=base)
            file_dirs.update(subDir)
        # Record the file path (from base to current folder) and absolute path
        elif (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            fileName = os.path.relpath(new_path, base)
            file_dirs[fileName] = new_path
    return file_dirs

#
# =============================================================================
#

def map_files_fuse(file_dirs, names):
    """
    Merge mapped file dictionaries into a single dataframe. Uses 'names' as the
    column names, and stores the file path to a file in different stages of the
    processing pipeline.

    Parameters
    ----------
    file_dirs : list-dict-str
        List of file location directories.
    names : list-str
        List of names to use for file directory columns. Same order as
        'file_dirs'.

    Raises
    ------
    Exception
        An exception is raised if a file contained in the first file directory
        is not found in the other file directories.

    Returns
    -------
    path_df : pd.DataFrame
        A dataframe of file names, and their locations in each file directory.
    
    """
    
    data = []
    # Assumes all files listed in first file directory
    # exists in the others
    for file in file_dirs[0].keys():
        # Create row
        row = [file, file]
        for i, filedir in enumerate(file_dirs):
            if file not in filedir:
                # Raise exception if file does not exist
                raise Exception('File ' + str(file) + ' does not exist in file directory ' + str(names[i]) + '.')
            row.append(filedir[file])
        # Add row to data frame
        data.append(row)
    # Create data frame
    path_df = pd.DataFrame(data, columns=['ID', 'File'] + names)
    path_df.set_index('ID',inplace=True)
    
    return path_df