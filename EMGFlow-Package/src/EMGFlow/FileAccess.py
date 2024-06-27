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

def ReadFileType(path, file_ext):
    """
    Safe wrapper for reading files of a given extension.

    Parameters
    ----------
    path : str
        Path of file to read.
    file_ext : str
        File extension to read.

    Raises
    ------
    Exception
        Raises an exception if the file could not be read.
    Exception
        Raises an exception if an unsupported file format was provided for
        file_ext.

    Returns
    -------
    file : pd.DataFrame
        Returns a Pandas data frame of the file contents.

    """
    
    if file_ext == 'csv':
        try:
            file = pd.read_csv(path)
        except:
            raise Exception("CSV file could not be read: " + path)
    else:
        raise Exception("Unsupported file format provided: " + file_ext)
        
    return file

#
# =============================================================================
#

def MapFiles(in_path, file_ext='csv', expression=None):
    """
    Generate a dictionary of file names and locations from the subfiles of a
    folder.
    
    Parameters
    ----------
    in_path : str
        The filepath to a directory to read Signal files.
    file_ext : str, optional
        File extension for files to read. The default is 'csv'.
    expression : str, optional
        A regular expression. If provided, will only count files whose names
        match the regular expression. The default is None.

    Raises
    ------
    Exception
        Raises an exception if expression is not None or a valid regular
        expression.

    Returns
    -------
    filedirs : dict
        A dictionary of file name keys and file path location values.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    filedirs = {}
    for file in os.listdir(in_path):
        new_path = os.path.join(in_path, file)
        if os.path.isdir(new_path):
            subDir = MapFiles(new_path, file_ext=file_ext, expression=expression)
            filedirs.update(subDir)
        elif (file[-len(file_ext):] == file_ext) and ((expression is None) or (re.match(expression, file))):
            filedirs[file] = new_path
    return filedirs

#
# =============================================================================
#

def ConvertMapFiles(fileObj, file_ext='csv', expression=None):
    """
    Generate a dictionary of file names and locations from different forms of
    input.

    Parameters
    ----------
    fileObj : str
        The file location object. This can be a string to a file location, or
        an already formed dictionary of file locations.
    file_ext : str, optional
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
        Raises an exception if expression is not None or a valid regular
        expression.

    Returns
    -------
    filedirs : dict
        A dictionary of file name keys and file path location values.
    
    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # User provided a path to a folder
    if type(fileObj) is str:
        if not os.path.isabs(fileObj):
            fileObj = os.path.abspath(fileObj)
        filedirs = MapFiles(in_path=fileObj, file_ext=file_ext, expression=expression)
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


def MapFilesFuse(filedirs, names):
    """
    Generate a dictionary of file names and locations from different forms of
    input. Each directory should contain the same file at different stages with
    the same name, and will create a dataframe of the location of this file in
    each of the directories provided.

    Parameters
    ----------
    filedirs : dict list
        List of file location directories
    names : str
        List of names to use for file directory columns. Same order as file
        directories.

    Raises
    ------
    Exception
        An exception is raised if a file contained in the first file directory
        is not found in the other file directories.

    Returns
    -------
    filedirs : pd.DataFrame
        A DataFrame of file names, and their locations in each file directory.
    
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
                raise Exception('File ' + file + ' does not exist in file directory ' + names[i])
            row.append(filedir[file])
        # Add row to data frame
        data.append(row)
    # Create data frame
    df = pd.DataFrame(data, columns=['ID', 'File'] + names)
    df.set_index('ID',inplace=True)
    
    return df