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

START_YEAR = 48
END_YEAR = 78
ITERATIONS = 100
# HOWMUCH_ALGORITHM = HMAlgoConstant4()
HOWMUCH_ALGORITHM = HMAlgoConstantDollars(120000)
WITHDRAW_ALGORITHM = WDAlgoPostTaxFirst()
TAX_MANAGER = TaxManager()

@click.command()
@click.argument('filename', type=click.File("r"))
@click.option('--seed', default=0, help='Random number seed')
@click.option('--iterations', default=100, help='How many iterations to run')
def cli(filename, seed, iterations):
    print("Loading account data from: {}".format(filename))

    if seed:
        np.random.seed(int(seed))

    results = []
    for i in range(ITERATIONS):
        results.append({})

        # Load account data
        data = loader.load_accounts(filename)

        the_years = range(START_YEAR, END_YEAR)
        results[i]['values'], results[i]['inflations'], results[i]['stocks'], results[i]['bonds'] = \
            run_simulation(i, the_years, data, HOWMUCH_ALGORITHM, WITHDRAW_ALGORITHM, TAX_MANAGER)


    # Print out results
    failures = 0
    for i in range(ITERATIONS):
        values = results[i]['values']
        if values[-1] < 1:
            failures += 1
    print("{:2}% scenarios succeeded".format(100 * (float(ITERATIONS) - failures) / ITERATIONS))

    plot_results(the_years, ITERATIONS, [y['values'] for y in results])


def plot_results(xvalues, numy, yvalues):
    MAX_YTICK = 20000000

    # the main Tkinter window
    window = tk.Tk()

    # setting the title
    window.title('Plotting in Tkinter')

    # dimensions of the main window
    window.geometry("500x500")

    # Plot it all
    fig = matplotlib.figure.Figure(figsize = (5, 5), dpi = 100)

    # adding the subplot
    plot1 = fig.add_subplot(111,
                            xlabel='Years', xlim=(START_YEAR, END_YEAR),
                            ylabel='Amount', ylim=(0, MAX_YTICK),
                            yticks=range(0, MAX_YTICK, 1000000))
    # plotting the graph
    for i in range(numy):
        plot1.plot(xvalues, yvalues[i])

    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()

    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()

    # run the gui
    window.mainloop()
