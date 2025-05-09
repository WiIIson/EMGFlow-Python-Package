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
    
    A 'Data' folder is created, with 'Raw', 'Notch', 'Bandpass', 'Smooth' and
    'Feature' subfolders.

    Parameters
    ----------
    root : str, optional
        Root of the data to be generated. The default is None.

    Returns
    -------
    pathNames : dict-str
        A dictionary of file locations with keys for stage in the processing
        pipeline.

    """
    
    if root is None:
        root = os.path.join(os.getcwd(), 'Data')
    else:
        root = os.path.normpath(root)
    
    # Create dictionary
    pathNames = {
        'Raw':os.path.join(root, 'Raw'),
        'Notch':os.path.join(root, 'Notch'),
        'Bandpass':os.path.join(root, 'Bandpass'),
        'Smooth':os.path.join(root, 'Smooth'),
        'Feature':os.path.join(root, 'Feature')
    }
    
    # Create folders
    for value in pathNames.values():
        os.makedirs(value, exist_ok=True)
    
    # Return dictionary
    return pathNames

#
# =============================================================================
#

def make_sample_data(pathNames):
    """
    Generates sample data in the 'Raw' folder of a provided dictionary of file
    locations.

    Parameters
    ----------
    pathNames : dict-str
        Dictionary of file locations.

    Raises
    ------
    Exception
        An exception is raised if the provided 'pathNames' dictionary doesn't
        contain a 'Raw' path key.
    Exception
        An exception is raised if the sample data cannot be loaded.

    Returns
    -------
    None.

    """
    
    # Check that a 'raw' folder exists
    if 'Raw' not in pathNames:
        raise Exception('Raw path not detected in pathNames.')
    
    # Load the sample data
    try:
        sample_data_01 = pd.read_csv(importlib_resources.files("EMGFlow").joinpath(os.path.join("data", "sample_data_01.csv")))
        sample_data_02 = pd.read_csv(importlib_resources.files("EMGFlow").joinpath(os.path.join("data", "sample_data_02.csv")))
        sample_data_03 = pd.read_csv(importlib_resources.files("EMGFlow").joinpath(os.path.join("data", "sample_data_03.csv")))
        sample_data_04 = pd.read_csv(importlib_resources.files("EMGFlow").joinpath(os.path.join("data", "sample_data_04.csv")))
    except:
        raise Exception('Failed to load EMGFlow sample data.')
    
    # Write the sample data
    os.makedirs(os.path.join(pathNames['Raw'], '01'), exist_ok=True)
    os.makedirs(os.path.join(pathNames['Raw'], '02'), exist_ok=True)
    
    data_path_01 = os.path.join(pathNames['Raw'], '01', 'sample_data_01.csv')
    data_path_02 = os.path.join(pathNames['Raw'], '01', 'sample_data_02.csv')
    data_path_03 = os.path.join(pathNames['Raw'], '02', 'sample_data_03.csv')
    data_path_04 = os.path.join(pathNames['Raw'], '02', 'sample_data_04.csv')
    
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

def read_file_type(path, fileExt):
    """
    Safe wrapper for reading files of a given extension.
    
    Switches between different reading methods based on the instructions
    provided.
    
    Supported formats that can be read are: 'csv'.

    Parameters
    ----------
    path : str
        Path of the file to read.
    fileExt : str
        File extension to read.

    Raises
    ------
    Exception
        An exception is raised if the file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'fileExt'.

    Returns
    -------
    file : pd.DataFrame
        Returns a Pandas data frame of the file contents.

    """
    
    if fileExt == 'csv':
        try:
            file = pd.read_csv(path)
        except:
            raise Exception("CSV file could not be read: " + str(path))
    else:
        raise Exception("Unsupported file format provided: " + str(fileExt))
        
    return file

#
# =============================================================================
#

def map_files(inPath, fileExt='csv', expression=None, base=None):
    """
    Generate a dictionary of file names and locations from the subfiles of a
    folder.
    
    Parameters
    ----------
    inPath : str
        The filepath to a directory to read Signal files.
    fileExt : str, optional
        File extension for files to read. The default is 'csv'.
    expression : str, optional
        A regular expression. If provided, will only count files whose names
        match the regular expression. The default is None.
    base : str, optional
        Path of the root folder the path keys should start from. The default is
        None. 

    Raises
    ------
    Exception
        An exception is raised if expression is not None or a valid regular
        expression.

    Returns
    -------
    filedirs : dict-str
        A dictionary of file name keys and file path location values.

    """
    
    # Throw error if Regex does not compile
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Set base path and ensure inPath is absolute
    if base is None:
        if not os.path.isabs(inPath):
            inPath = os.path.join(os.getcwd(), inPath)
        base = inPath
    
    # Build file directory dictionary
    filedirs = {}
    for file in os.listdir(inPath):
        new_path = os.path.join(inPath, file)
        # Recursively check folders
        if os.path.isdir(new_path):
            subDir = map_files(new_path, fileExt=fileExt, expression=expression, base=base)
            filedirs.update(subDir)
        # Record the file path (from base to current folder) and absolute path
        elif (file[-len(fileExt):] == fileExt) and ((expression is None) or (re.match(expression, file))):
            fileName = os.path.relpath(new_path, base)
            filedirs[fileName] = new_path
    return filedirs

#
# =============================================================================
#

def convert_map_files(fileObj, fileExt='csv', expression=None):
    """
    Generate a dictionary of file names and locations from different forms of
    input.

    Parameters
    ----------
    fileObj : str
        The file location object. This can be a string to a file location, or
        an already formed dictionary of file locations.
    fileExt : str, optional
        File extension for files to read. Only reads files with this extension.
        The default is 'csv'.
    expression : str, optional
        A regular expression. If provided, will only count files whose names
        match the regular expression. The default is None.

    Raises
    ------
    Exception
        An exception is raised if an unsupported file location format is
        provided.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.

    Returns
    -------
    filedirs : dict-str
        A dictionary of file name keys and file path location values.
    
    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided.")
    
    # User provided a path to a folder
    if type(fileObj) is str:
        if not os.path.isabs(fileObj):
            fileObj = os.path.abspath(fileObj)
        filedirs = map_files(inPath=fileObj, fileExt=fileExt, expression=expression)
    # User provided a processed file directory
    elif type(fileObj) is dict:
        # If expression is provided, filters the dictionary
        # for all entries matching it
        fd = fileObj.copy()
        if expression != None:
            for file in fd:
                if not (re.match(expression, fd[file])):
                    del fd[file]
        filedirs = fd
    # Provided file location format is unsupported
    else:
        raise Exception("Unsupported file location format:", type(fileObj))
    
    return filedirs

#
# =============================================================================
#

def map_files_fuse(filedirs, names):
    """
    Generate a dictionary of file names and locations from different forms of
    input. Each directory should contain the same file at different stages with
    the same name, and will create a dataframe of the location of this file in
    each of the directories provided.

    Parameters
    ----------
    filedirs : list-dict-str
        List of file location directories
    names : list-str
        List of names to use for file directory columns. Same order as file
        directories.

    Raises
    ------
    Exception
        An exception is raised if a file contained in the first file directory
        is not found in the other file directories.

    Returns
    -------
    pathDF : pd.DataFrame
        A dataframe of file names, and their locations in each file directory.
    
    """
    
    data = []
    # Assumes all files listed in first file directory
    # exists in the others
    for file in filedirs[0].keys():
        # Create row
        row = [file, file]
        for i, filedir in enumerate(filedirs):
            if file not in filedir:
                # Raise exception if file does not exist
                raise Exception('File ' + str(file) + ' does not exist in file directory ' + str(names[i]) + '.')
            row.append(filedir[file])
        # Add row to data frame
        data.append(row)
    # Create data frame
    pathDF = pd.DataFrame(data, columns=['ID', 'File'] + names)
    pathDF.set_index('ID',inplace=True)
    
    return pathDF