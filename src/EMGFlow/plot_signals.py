import re
import matplotlib.pyplot as plt
import webbrowser

from shiny import App, render, ui, reactive

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

def plot_dashboard(path_names, col, units, expression=None, file_ext='csv', auto_run=True):
    """
    Generate a shiny dashboard of different processing stages for a given
    column.
    
    'CTRL + C' can be entered in the terminal to end the display of the
    dashboard and resume code execution.

    Parameters
    ----------
    path_names : dict-str
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
    file_ext : str, optional
        String extension of the files to read. Any file in in_path with this
        extension will be considered to be a Signal file, and treated as such.
        The default is 'csv'.
    auto_run : bool, optional
        Boolean controlling behavior of the function. If true (default), will
        automatically run the visual and open it in the default browser. If
        false, will return the visualization object.

    Raises
    ------
    Exception
        An exception is raised if the directories in 'path_names' don't contain
        the same files.
    Exception
        An exception is raised if 'col' is not found as a column in a
        dataframe.
    Exception
        An exception is raised if a file cannot not be read in a path in
        'path_names'.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.
    Exception
        An exception is raised if 'expression' is not None or a valid regular
        expression.

    Returns
    -------
    app : None, shiny.App
        If 'auto_run' is True, returns None. If False, returns a shiny.App
        instance.

    """
    
    # Remove feature path, and convert dictionary to lists
    path_names.pop("Feature", None)
    in_paths = list(path_names.values())
    names = list(path_names.keys())
    
    if expression is not None:
        try:
            re.compile(expression)
        except:
            raise Exception("Invalid regex expression provided")
    
    # Convert file paths to directories
    file_dirs = []
    for path in in_paths:
        file_dirs.append(convert_map_files(path))
        
    # Convert file directories to data frame
    df = map_files_fuse(file_dirs, names)
    
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
                ui.input_select('file_type', 'File:', choices=df['File']),
                ui.input_slider('x_range', 'X-Axis Range:', min=0, max=1, value=[0, 1])
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
        @reactive.effect
        def update_x_slider():
            filename = input.file_type()
            column = input.sig_type()
        
            if column == 'All':
                max_x = max(
                    read_file_type(file_loc, file_ext)['Time'].max()
                    for file_loc in list(df.loc[filename])[1:]
                )
                min_x = min(
                    read_file_type(file_loc, file_ext)['Time'].min()
                    for file_loc in list(df.loc[filename])[1:]
                )
            else:
                file_location = df.loc[filename][column]
                sigDF = read_file_type(file_location, file_ext)
                max_x = sigDF['Time'].max()
                min_x = sigDF['Time'].min()
        
            ui.update_slider("x_range", min=min_x, max=max_x, value=[min_x, max_x])


        
        @render.plot
        def plt_signal():
            filename = input.file_type()
            column = input.sig_type()
            x_min, x_max = input.x_range()  # Get slider values

            
            # Plot data
            fig, ax = plt.subplots()
            if column == 'All':
                # Read/plot each file
                for file_loc in reversed(list(df.loc[filename])[1:]):
                    sigDF = read_file_type(file_loc, file_ext)
                    
                    # Exception for column input
                    if col not in list(sigDF.columns.values):
                        raise Exception("Column " + str(col) + " not in Signal " + str(filename))
                    
                    
                    ax.plot(sigDF['Time'], sigDF[col], alpha=0.5, linewidth=1)
                # Set legend for multiple plots
                ax.legend(legnames)
            else:
                # Read/plot single file
                file_location = df.loc[filename][column]
                sigDF = read_file_type(file_location, file_ext)
                
                # Exception for column input
                if col not in list(sigDF.columns.values):
                    raise Exception("Column " + str(col) + " not in Signal " + str(filename))
                
                # Get colour data
                i = (names.index(column) + 1) % len(colours)
                # Plot file
                ax.plot(sigDF['Time'], sigDF[col], color=colours[len(names) - i], alpha=0.5, linewidth=1)
                
            ax.set_xlim(x_min, x_max)
            ax.set_ylabel('Voltage (mV)')
            ax.set_xlabel('Time (s)')
            ax.set_title(column + ' filter: ' + filename)
            
            return fig
    
    app = App(app_ui, server)
    
    if auto_run:
        webbrowser.open('http://127.0.0.1:8000')
        app.run()
        return
    else:
        return app