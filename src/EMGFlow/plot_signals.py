import asyncio
import os
import matplotlib.pyplot as plt
import threading
import uvicorn
import webbrowser
import numpy as np

from shiny import App, render, ui, reactive

import nest_asyncio
nest_asyncio.apply()

from .access_files import *
from .preprocess_signals import emg_to_psd

#
# =============================================================================
#

"""
A collection of functions for plotting data.
"""

#
# =============================================================================
#

def plot_dashboard(path_names:dict, column_name:str, sampling_rate:float=1000.0, units:str='mV', file_ext:str='csv', use_mask:bool=False, show_legend:bool=True, auto_run:bool=True):
    """
    Generate a Shiny dashboard of different processing stages for a given
    column of signal data.
    
    'CTRL + C' can be entered in the terminal to end the display of the
    dashboard and resume code execution.

    Parameters
    ----------
    path_names : dict-str
        A dictionary of file locations with keys for stage in the processing
        pipeline. The function will generate graphs for as many paths are
        provided in the dictionary. The dictionary can be created with the
        'make_paths' function.
    column_name : str
        The column of the signals to display in the visualization.
    sampling_rate : float, optional
        The sampling rate for all signal data being plotted. The default is
        1000.0.
    units : str, optional
        Units to use for the y axis of the plot, should be the same units used
        for the values in 'column_name'. The default is 'mV'.
    file_ext : str, optional
        File extension for files to read. Only visualizes files with this
        extension. The default is 'csv'.
    use_mask : bool, optional
        An option to visualize the NaN mask If True, it will set values to NaN
        based on the NaN mask. If False, it will use the unaltered values of
        the column ignoring the NaN mask. The default is False.
    show_legend : bool, optional
        An option to show the legend on the plot. If True, it will show the
        legend. If False, the legend will be hidden. The default is True.
    auto_run : bool, optional
        An option to automatically see the visualization. If True, it will run
        the visual and open it in the default browser. If False, it will return
        the visualization object. The default is True.

    Raises
    ------
    Exception
        An exception is raised if 'column_name' is not a column of a signal file.
    
    Exception
        An exception is raised if a file contained in the first file directory
        (path_names[0]) is not found in the other file directories.
    
    Exception
        An exception is raised if a file could not be read.
    Exception
        An exception is raised if an unsupported file format was provided for
        'file_ext'.

    Returns
    -------
    app : None, shiny.App
        If 'auto_run' is True, returns None. If False, returns a shiny.App
        instance.

    """
    
    # Remove feature path, and convert dictionary to lists
    path_names = path_names.copy()
    path_names.pop("feature", None)
    
    # Try to load from each available file location
    for name in list(path_names.keys()):
        if not bool(os.listdir(path_names[name])):
            path_names.pop(name, None)
    
    names = list(path_names.keys())
    file_dirs = [map_files(p) for p in path_names.values()]
    df = map_files_fuse(file_dirs, names)
    
    # Set style
    plt.style.use('fivethirtyeight')
    
    # Get colours based on number of paths being plotted
    n = len(path_names)
    cmap = plt.cm.get_cmap('viridis', n)
    colours = [cmap(i) for i in reversed(range(n))]
    
    # Create shiny dashboard
    
    # =============
    # UI definition
    # =============
    app_ui = ui.page_fluid(
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select('sig_type', 'Signal Displayed:', choices=['All']+names),
                ui.input_select('file_type', 'File:', choices=df['File']),
                ui.input_slider('x_range', 'X-Axis Range:', min=0, max=1, value=[0, 1]),
                ui.input_slider('y_range', 'Y-Axis Range:', min=0, max=1, value=[0, 1]),
                ui.input_checkbox('use_psd', 'Show PSD', value=False),
                ui.input_action_button('stop', 'Stop Dashboard', style="background-color: #007bc2; color: white; border-color: #007bc2;")
            ),
            ui.card(
                ui.output_plot('plt_signal'),
            )
        ),
    )
    
    # Create legend names and order label
    legnames = [f"{i+1}: {nm}" for i, nm in enumerate(names)]
    
    # =================
    # Server definition
    # =================
    def server(input, output, session):
        @reactive.effect
        def update_x_slider():
            filename = input.file_type()
            column = input.sig_type()
            use_psd = input.use_psd()
        
            if column == 'All':
                min_x = float('inf')
                max_x = float('-inf')
                min_y = float('inf')
                max_y = float('-inf')
                
                for file_loc in list(df.loc[filename])[1:]:
                    data = read_file_type(file_loc, file_ext)
                    
                    if not use_psd:
                        x_val = data['Time']
                        y_val = data[column_name]
                    else:
                        PSD = emg_to_psd(data, column_name, sampling_rate=sampling_rate, normalize=False)
                        x_val = PSD['Frequency']
                        y_val = PSD['Power']
                    
                    min_x = min(min_x, x_val.min())
                    max_x = max(max_x, x_val.max())
                    min_y = min(min_y, y_val.min())
                    max_y = max(max_y, y_val.max())
                
                # Zoom out by 5% of diff(max, min)
                zoom_x = abs(max_x - min_x) * 0.05
                zoom_y = abs(max_y - min_y) * 0.05
                min_x -= zoom_x
                max_x += zoom_x
                min_y -= zoom_y
                max_y += zoom_y
                    
            else:
                file_location = df.loc[filename][column]
                data = read_file_type(file_location, file_ext)
                
                if not use_psd:
                    x_val = data['Time']
                    y_val = data[column_name]
                else:
                    PSD = emg_to_psd(data, column_name, sampling_rate=sampling_rate, normalize=False)
                    x_val = PSD['Frequency']
                    y_val = PSD['Power']
                
                max_x = x_val.max()
                min_x = x_val.min()
                max_y = y_val.max()
                min_y = y_val.min()
                # Zoom out by 5% of diff(max, min)
                zoom_x = abs(max_x - min_x) * 0.05
                zoom_y = abs(max_y - min_y) * 0.05
                min_x -= zoom_x
                max_x += zoom_x
                min_y -= zoom_y
                max_y += zoom_y

            y_step = abs(max_y - min_y) / 100
            x_step = abs(max_x - min_x) / 100
        
            ui.update_slider("x_range", min=min_x, max=max_x, value=[min_x, max_x], step=x_step)
            ui.update_slider("y_range", min=min_y, max=max_y, value=[min_y, max_y], step=y_step)


        
        @render.plot
        def plt_signal():
            filename = input.file_type()
            column = input.sig_type()
            x_min, x_max = input.x_range()  # Get slider values
            y_min, y_max = input.y_range()
            use_psd = input.use_psd()
            
            # Plot data
            fig, ax = plt.subplots()
            if column == 'All':
                # Read/plot each file
                file_locs = list(df.loc[filename])[1:]
                for i in range(len(file_locs)):
                    file_loc = file_locs[i]
                    sigDF = read_file_type(file_loc, file_ext)
                    
                    # Exception for column input
                    if column_name not in list(sigDF.columns.values):
                        raise Exception("Column " + str(column_name) + " not in Signal " + str(filename))
                    
                    if not use_psd:
                        ax.plot(sigDF['Time'], sigDF[column_name], color=colours[i], alpha=0.5, linewidth=1)
                    else:
                        PSD = emg_to_psd(sigDF, column_name, sampling_rate, normalize=False)
                        ax.plot(PSD['Frequency'], PSD['Power'], color=colours[i], alpha=0.5, linewidth=1)
                    
                # Set legend for multiple plots
                if show_legend:
                    fig.legend(legnames, loc='upper right', fontsize=10)
            else:
                # Read/plot single file
                file_location = df.loc[filename][column]
                sigDF = read_file_type(file_location, file_ext)
                
                # Exception for column input
                if column_name not in list(sigDF.columns.values):
                    raise Exception("Column " + str(column_name) + " not in Signal " + str(filename))
                
                # Get colour data
                i = names.index(column)
                # Plot file
                if not use_psd:
                    ax.plot(sigDF['Time'], sigDF[column_name], color=colours[i], alpha=0.5, linewidth=1)
                else:
                    PSD = emg_to_psd(sigDF, column_name, sampling_rate, normalize=False)
                    ax.plot(PSD['Frequency'], PSD['Power'], color=colours[i], alpha=0.5, linewidth=1)
                
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            
            if not use_psd:
                ax.set_ylabel('Voltage (' + units + ')')
                ax.set_xlabel('Time (s)')
            else:
                ax.set_ylabel('Power (dH/Hz)')
                ax.set_xlabel('Frequency (Hz)')
                
            ax.set_title(column_name)
            
            return fig
        
        @reactive.effect
        @reactive.event(input.stop)
        async def shutdown_app():
            ui.update_action_button('stop', label='Terminated', disabled=True)
            ui.notification_show('Dashboard stopped', duration=None, type='warning', close_button=False)
            os._exit(0)
    
    app = App(app_ui, server)
    
    if auto_run:
        host, port = "127.0.0.1", 8000
        url = f"http://{host}:{port}"

        def run_server():
            uvicorn.run(app, host=host, port=port)
        
        thread = threading.Thread(target=run_server)
        thread.start()
        
        webbrowser.open(url)
        return
    
    # Return the app if requested
    return app