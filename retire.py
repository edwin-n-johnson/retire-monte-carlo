import os.path
import sys
import click
import matplotlib.figure
import numpy as np
import pprint
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from simulator import run_simulation
import loader
from tax_manager import TaxManager
from hmalgo_constant_4 import HMAlgoConstant4
from hmalgo_constant_dollars import HMAlgoConstantDollars
from wdalgo_post_tax_first import WDAlgoPostTaxFirst

#START_YEAR = 48
#END_YEAR = 78
#ITERATIONS = 100
# HOWMUCH_ALGORITHM = HMAlgoConstant4()
HOWMUCH_ALGORITHM = HMAlgoConstantDollars(120000)
WITHDRAW_ALGORITHM = WDAlgoPostTaxFirst()
TAX_MANAGER = TaxManager()

class Config:
    def __init__(self, filename, start, end, iterations):
        self.filename = filename
        self.start = start
        self.end = end
        self.iterations = iterations

def run_simulator_and_plot_results(window, config, result_label):
    MAX_YTICK = 20000000

    # Run the simulator
    results = []
    for i in range(config.iterations):
        results.append({})

        # Load account data
        data = loader.load_accounts(config.filename)

        the_years = range(config.start, config.end)
        results[i]['values'], results[i]['inflations'], results[i]['stocks'], results[i]['bonds'] = \
            run_simulation(i, the_years, data, HOWMUCH_ALGORITHM, WITHDRAW_ALGORITHM, TAX_MANAGER)

    # Print out summary of results
    failures = 0
    for i in range(config.iterations):
        values = results[i]['values']
        if values[-1] < 1:
            failures += 1
    overall_result = "{:2}% scenarios succeeded"\
        .format(100 * (float(config.iterations) - failures) / config.iterations)
    result_label.config(text=overall_result)
    print(overall_result)

    # Plot it all
    #fig = matplotlib.figure.Figure(figsize = (8, 8), dpi = 100)
    fig = matplotlib.figure.Figure()

    # adding the subplot
    plot1 = fig.add_subplot(111,
                            xlabel='Years', xlim=(config.start, config.end),
                            ylabel='Amount', ylim=(0, MAX_YTICK),
                            yticks=range(0, MAX_YTICK, 1000000))
    # plotting the graph
    for i in range(config.iterations):
        plot1.plot(the_years, results[i]['values'])

    # creating the Tkinter canvas containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().grid(row=8, column=0, columnspan=2)


def validate_and_next_step(root, filename_label, filename, start_label, start,
                           end_label, end, iterations_label, iterations,
                           result_label):
    elements = [
        { 'label': filename_label, 'entry': filename},
        { 'label': start_label, 'entry': start },
        { 'label': end_label, 'entry': end},
        { 'label': iterations_label, 'entry': iterations},
    ]
    valid = True
    for elem in elements:
        if not elem['entry'].get():
            elem['label'].config(fg="red")
            valid = False
        else:
            elem['label'].config(fg="black")
    if not os.path.exists(filename.get()):
        filename_label.config(fg="red")
        valid = False

    if valid:
        config = Config(filename.get(), int(start.get()), int(end.get()), int(iterations.get()))
        run_simulator_and_plot_results(root, config, result_label)

def run_gui(root, filename, config):
    # create main frame
    frame = tk.Frame(root)
    frame.grid(row=0, column=0)
    # Start Year
    start_label = tk.Label(frame, text="Start Year")
    start_label.grid(row=0, column=0)
    start_var = tk.StringVar()
    if config.start:
        start_var.set(config.start)
    tk.Entry(frame, textvariable=start_var).grid(row=1, column=0)
    # End Year
    end_label = tk.Label(frame, text="End Year")
    end_label.grid(row=0, column=1)
    end_var = tk.StringVar()
    if config.end:
        end_var.set(config.end)
    tk.Entry(frame, textvariable=end_var).grid(row=1, column=1)
    # Iterations
    iterations_label = tk.Label(frame, text="Iterations")
    iterations_label.grid(row=2, column=0)
    iterations_var = tk.StringVar()
    if config.iterations:
        iterations_var.set(config.iterations)
    tk.Entry(frame, textvariable=iterations_var).grid(row=3, column=0)
    # Filename
    filename_label = tk.Label(frame, text='Filename')
    filename_label.grid(row=4, column=0, columnspan=2)
    filename_var = tk.StringVar()
    if config.filename:
        filename_var.set(config.filename)
    tk.Entry(frame, textvariable=filename_var).grid(row=5, column=0, columnspan=2)
    # Results (below button)
    result_label = tk.Label(frame)
    result_label.grid(row=7, column=0, columnspan=2)
    # Button to run simulation
    btn = tk.Button(frame, text="Try It",
              command=lambda: validate_and_next_step(root,
                                                     filename_label, filename_var,
                                                     start_label, start_var,
                                                     end_label, end_var,
                                                     iterations_label, iterations_var,
                                                     result_label))
    btn.grid(row=6, column=0, columnspan=2)

    frame.columnconfigure(0, weight=3)

@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--start', type=click.INT, default=48, help='Age at the start of the simulation')
@click.option('--end', type=click.INT, default=90, help='Age at the end of the simulation')
@click.option('--iterations', type=click.INT, default=100, help='How many iterations to run')
#@click.option('--withdraw', type=click.Choice(['']))
@click.option('--gui/--no-gui', default=False, help='Launch gui')
@click.option('--seed', default=0, help='Random number seed')
def cli(gui, start, end, iterations, filename, seed):
    print("Loading account data from: {}".format(filename))

    if seed:
        np.random.seed(int(seed))

    # the main Tkinter window
    window = tk.Tk()
    # setting the title
    window.title('Monte Carlo Retirement Simulation')
    # dimensions of the main window
    window.geometry("800x800")

    cfg = Config(filename, start, end, iterations)

    if gui:
        run_gui(window, filename, cfg)
    else:
        run_simulator_and_plot_results(window, filename, cfg)

    # run the gui
    window.mainloop()
