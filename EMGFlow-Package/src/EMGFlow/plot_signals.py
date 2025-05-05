import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import random
import webbrowser
from tqdm import tqdm

from shiny import App, render, ui

import nest_asyncio
nest_asyncio.apply()

from .preprocess_signals import emg_to_psd
from .access_files import *

#
# =============================================================================
#

"""
A collection of functions for plotting subject data
"""

#
# =============================================================================
#

def plot_spectrum(inPath, outPath, samplingRate, cols=None, p=None, expression=None, fileExt='csv'):
    """
    Generate plots of the PSDs of each column of Signals in a directory

    Parameters
    ----------
    inPath : str
        Filepath to a directory to read Signal files.
    outPath : str
        Filepath to an output directory.
    samplingRate : float
        Sampling rate of the Signals.
    cols : list, optional
        List of columns of the Signal to plot. The default is None, in which case every column except
        'time' is plotted.
    p : float, optional
        Random sampling probability. If given a percentage, will have that probability to plot
        each Signal. The default is None, in which case all Signals are plotted.
    expression : str, optional
        A regular expression. If provided, will only generate plots for files whose names match the regular
        expression. The default is None.
    fileExt : str, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.

    Raises
    ------
    Exception
        An exception is raised if samplingRate is less or equal to 0.
    Exception
        An exception is raised if a column is not in a dataframe.
    Exception
        An exception is raised if p is not None and not between 0 and 1.
    Exception
        Raises an exception if a file cannot not be read in inPath.
    Exception
        Raises an exception if an unsupported file format was provided for
        fileExt.
    Exception
        Raises an exception if expression is not None or a valid regular
        expression.

    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    if (p is not None) and (p < 0 or p > 1):
        raise Exception("p must be between 0 or 1, or None")
    
    # Convert out path to absolute
    if not os.path.isabs(outPath):
        outPath = os.path.abspath(outPath)
    
    filedirs = convert_map_files(inPath, fileExt=fileExt, expression=expression)
    
    # Make plots
    for file in tqdm(filedirs):
        if (file[-len(fileExt):] == fileExt) and ((expression is None) or (re.match(expression, file))):
            
            # Randomly create signal plots if requested
            if (p is None) or (random.random() < p):
                
                # Read file
                data = read_file_type(filedirs[file], fileExt)
                
                # If no columns selected, apply filter to all columns except time
                if cols is None:
                    cols = list(data.columns)
                    if 'Time' in cols:
                        cols.remove('Time')
                
                # Create plot
                fig, axs = plt.subplots(1, len(cols), figsize=(15*len(cols),15))
                
                # Plot each column
                if len(cols) == 1:
                    col = cols[0]
                    
                    if col not in list(data.columns.values):
                        raise Exception("Column " + str(col) + " not in Signal " + str(file))
                    
                    psd = emg_to_psd(data[col], samplingRate=samplingRate)
                    axs.plot(psd['Frequency'], psd['Power'])
                    axs.set_ylabel('Power magnitude')
                    axs.set_xlabel('Frequency')
                    axs.set_title(col)
                    
                else:
                    for i in range(len(cols)):
                        col = cols[i]
                        
                        if col not in list(data.columns.values):
                            raise Exception("Column " + str(col) + " not in Signal " + str(file))
                        
                        psd = emg_to_psd(data[col], samplingRate=samplingRate)
                        axs[i].plot(psd['Frequency'], psd['Power'])
                        axs[i].set_ylabel('Power magnitude')
                        axs[i].set_xlabel('Frequency')
                        axs[i].set_title(col)
                
                # Set title and save figure
                fig.suptitle(file + ' Power Spectrum Density')
                fig.savefig(outPath + file[:-len(fileExt)] + 'jpg')
    return

#
# =============================================================================
#

def plot_compare_signals(inPath1, inPath2, outPath, samplingRate, cols=None, expression=None, fileExt='csv'):
    """
    Generate plots of the PSDs comparing different processing stages.

    Parameters
    ----------
    inPath1 : str
        Filepath to a directory containing the first set of Signals for comparison.
    inPath2 : TYPE
        Filepath to a directory containing the second set of Signals for comparison.
    outPath : str
        Filepath to an output directory.
    samplingRate : float
        Sampling rate of the Signals.
    cols : list, optional
        List of columns of the Signal to plot. The default is None, in which case every column except
        'time' is plotted.
    expression : str, optional
        A regular expression. If provided, will only generate plots for files whose names match the regular
        expression. The default is None.
    fileExt : str, optional
        File extension for files to read. Only reads files with this extension. The default is 'csv'.

    Raises
    ------
    Exception
        An exception is raised if inPath1 and inPath2 don't contain the same files.
    Exception
        An exception is raised if samplingRate is less or equal to 0.
    Exception
        An exception is raised if a column in cols is not in a dataframe.
    Exception
        Raises an exception if a file cannot not be read in inPath1 or
        inPath2.
    Exception
        Raises an exception if an unsupported file format was provided for
        fileExt.
    Exception
        Raises an exception if expression is not None or a valid regular
        expression.

    Returns
    -------
    None.

    """
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Convert out path to absolute
    if not os.path.isabs(outPath):
        outPath = os.path.abspath(outPath)
    
    # Get dictionary of file locations
    filedirs1 = convert_map_files(inPath1, fileExt=fileExt, expression=expression)
    filedirs2 = convert_map_files(inPath2, fileExt=fileExt, expression=expression)
    
    if set(filedirs1.keys()) != set(filedirs2.keys()):
        raise Exception("File mismatch between provided directories")
    
    # Make plots
    for file in tqdm(filedirs1):
        if (file[-len(fileExt):] == fileExt) and ((expression is None) or (re.match(expression, file))):
            
            # Read file
            data1 = read_file_type(filedirs1[file], fileExt)
            data2 = read_file_type(filedirs2[file], fileExt)
            
            # If no columns selected, apply filter to all columns except time
            if cols is None:
                cols = list(data1.columns)
                if 'Time' in cols:
                    cols.remove('Time')
            
            # Create plot
            fig, axs = plt.subplots(2, len(cols), figsize=(15*len(cols),30))
            
            if len(cols) == 1:
                col = cols[0]
                
                if col not in list(data1.columns.values) or col not in list(data2.columns.values):
                    raise Exception("Column " + str(col) + " not in Signal " + str(file))
                
                psd1 = emg_to_psd(data1[col], samplingRate=samplingRate)
                axs[0].plot(psd1['Frequency'], psd1['Power'])
                axs[0].set_ylabel('Power magnitude')
                axs[0].set_title(col)
                
                psd2 = emg_to_psd(data2[col], samplingRate=samplingRate)
                axs[1].plot(psd2['Frequency'], psd2['Power'])
                axs[1].set_ylabel('Power magnitude')
                axs[1].set_xlabel('Frequency')
                
            else:
                # Plot each column
                for i in range(len(cols)):
                    col = cols[i]
                    
                    if col not in list(data1.columns.values) or col not in list(data2.columns.values):
                        raise Exception("Column " + str(col) + " not in Signal " + str(file))
                    
                    psd1 = emg_to_psd(data1[col], samplingRate=samplingRate)
                    axs[0,i].plot(psd1['Frequency'], psd1['Power'])
                    axs[0,i].set_ylabel('Power magnitude')
                    axs[0,i].set_title(col)
                    
                    psd2 = emg_to_psd(data2[col], samplingRate=samplingRate)
                    axs[1,i].plot(psd2['Frequency'], psd2['Power'])
                    axs[1,i].set_ylabel('Power magnitude')
                    axs[1,i].set_xlabel('Frequency')
            
            # Set title and save figure
            fig.suptitle(file + ' Power Spectrum Density')
            fig.savefig(outPath + file[:-len(fileExt)] + 'jpg')
    
    return

#
# =============================================================================
#

# Creates a shiny app object that can be ran
def plot_dashboard(pathNames, col, units, expression=None, fileExt='csv', autorun=True):
    """
    Generate a shiny dashboard of different processing stages for a given column.

    Parameters
    ----------
    pathNames : [str] dict
        A dictionary of path names for reading data. The function will generate
        graphs for as many paths are provided in the dictionary. The dictionary
        can be created with the make_paths function.
    col : str
        String column name to display the visualization.
    units : str
        Units to use for the y axis of the plot, should be same units used for
        column values.
    expression : str, optional
        String regular expression. If provided, will only create visualizations
        for Signal files whose names match the regular expression, and will
        ignore everything else. The default is None.
    fileExt : str, optional
        String extension of the files to read. Any file in inPath with this
        extension will be considered to be a Signal file, and treated as such.
        The default is 'csv'.
    autorun : bool, optional
        Boolean controlling behavior of the function. If true (default), will
        automatically run the visual and open it in the default browser. If
        false, will return the visualization object.

    Raises
    ------
    Exception
        An exception is raised if the directories in inPaths don't contain the
        same files.
    Exception
        An exception is raised if the col is not found in a dataframe.
    Exception
        Raises an exception if a file cannot not be read in a path in inPaths.
    Exception
        Raises an exception if an unsupported file format was provided for
        fileExt.
    Exception
        Raises an exception if expression is not None or a valid regular
        expression.

    Returns
    -------
    If autorun is True, returns None. If False, returns a shiny.App instance.

    """
    
    # Remove feature path, and convert dictionary to lists
    pathNames.pop("Feature", None)
    inPaths = list(pathNames.values())
    names = list(pathNames.keys())
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Convert file paths to directories
    filedirs = []
    for path in inPaths:
        filedirs.append(convert_map_files(path))
        
    # Convert file directories to data frame
    df = map_files_fuse(filedirs, names)
    
    # Set style
    plt.style.use('fivethirtyeight')
    
    # Get colours
    colours = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    # Create shiny dashboard
    
    # =============
    # UI definition
    # =============
    app_ui = ui.page_fluid(
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select('sig_type', 'Signal Displayed:', choices=['All']+names),
                ui.input_select('file_type', 'File:', choices=df['File'])
            ),
            ui.card(
                ui.output_plot('plt_signal'),
            ),
        ),
    )
    
    legnames = names.copy()
    legnames.reverse()
    
    # =================
    # Server definition
    # =================
    def server(input, output, session):
        @render.plot
        def plt_signal():
            filename = input.file_type()
            column = input.sig_type()
            
            # Plot data
            fig, ax = plt.subplots()
            if column == 'All':
                # Read/plot each file
                for file_loc in reversed(list(df.loc[filename])[1:]):
                    sigDF = read_file_type(file_loc, fileExt)
                    
                    # Exception for column input
                    if col not in list(sigDF.columns.values):
                        raise Exception("Column " + str(col) + " not in Signal " + str(filename))
                    
                    
                    ax.plot(sigDF['Time'], sigDF[col], alpha=0.5, linewidth=1)
                # Set legend for multiple plots
                ax.legend(legnames)
            else:
                # Read/plot single file
                file_location = df.loc[filename][column]
                sigDF = read_file_type(file_location, fileExt)
                
                # Exception for column input
                if col not in list(sigDF.columns.values):
                    raise Exception("Column " + str(col) + " not in Signal " + str(filename))
                
                # Get colour data
                i = (names.index(column) + 1) % len(colours)
                # Plot file
                ax.plot(sigDF['Time'], sigDF[col], color=colours[len(names) - i], alpha=0.5, linewidth=1)
                
            
            ax.set_ylabel('Voltage (mV)')
            ax.set_xlabel('Time (s)')
            ax.set_title(column + ' filter: ' + filename)
            
            return fig
    
    app = App(app_ui, server)
    
    if autorun:
        webbrowser.open('http://127.0.0.1:8000')
        app.run()
        return
    else:
        return app