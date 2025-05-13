import re
import matplotlib.pyplot as plt
import webbrowser

from shiny import App, render, ui

import nest_asyncio
nest_asyncio.apply()

from .preprocess_signals import emg_to_psd
from .access_files import *

#
# =============================================================================
#

"""
A collection of functions for plotting subject data.
"""

#
# =============================================================================
#

def plot_dashboard(pathNames, col, units, expression=None, fileExt='csv', autorun=True):
    """
    Generate a shiny dashboard of different processing stages for a given
    column.

    Parameters
    ----------
    pathNames : dict-str
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
        An exception is raised if the directories in 'inPaths' don't contain
        the same files.
    Exception
        An exception is raised if 'col' is not found as a column in a
        dataframe.
    Exception
        An exception is raised if a file cannot not be read in a path in
        'inPaths'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'fileExt'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.

    Returns
    -------
    app : None, shiny.App
        If 'autorun' is True, returns None. If False, returns a shiny.App
        instance.

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