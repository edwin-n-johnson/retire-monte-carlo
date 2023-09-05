import os.path
import pprint
import sys
import click
import matplotlib.figure
import numpy as np
import logging
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from simulator import run_simulation
from tax_manager import TaxManager
from account_manager import AccountManager
from hmalgo_constant_percentage import HMAlgoConstantPercentage
from hmalgo_constant_dollars import HMAlgoConstantDollars
from loader_withdraw import WithdrawAlgo

TAX_MANAGER = TaxManager()


class Options:
    def __init__(self, start, end, iterations, how_much):
        self.start = start
        self.end = end
        self.iterations = iterations
        self.how_much = how_much

    def __str__(self):
        return pprint.pformat({
            'start': self.start,
            'end': self.end,
            'iterations': self.iterations,
            'how_much': self.how_much,
        })


def howmuch_algo_chooser(how_much):
    hm_type, hm_value = how_much

    if hm_type == 'c%':
        hm_algo = HMAlgoConstantPercentage(float(hm_value))
    elif hm_type == 'c$':
        hm_algo = HMAlgoConstantDollars(int(hm_value))
    else:
        hm_algo = None

    return hm_algo


def run_simulator_and_plot_results(window, balances, withdraws, options, result_label=None):
    max_ytick = 20000000

    account_manager = AccountManager(TAX_MANAGER)
    howmuch_algo = howmuch_algo_chooser(options.how_much)
    withdraw_algo = WithdrawAlgo(withdraws)

    the_years = range(options.start, options.end)

    # Run the simulator
    results = []
    first_time = True
    for i in range(options.iterations):
        results.append({})

        # Load account data
        if first_time:
            account_manager.toggle_logging()
            first_time = False
        account_manager.load_accounts(balances)

        results[i]['values'], results[i]['inflations'], results[i]['stocks'], results[i]['bonds'] = \
            run_simulation(i, the_years, account_manager, howmuch_algo, withdraw_algo, TAX_MANAGER)

    # Print out summary of results
    failures = 0
    for i in range(options.iterations):
        values = results[i]['values']
        if values[-1] < 1:
            failures += 1
    overall_result = "{:2}% scenarios succeeded"\
        .format(100 * (float(options.iterations) - failures) / options.iterations)
    logging.info(result_label)
    print(overall_result)
    if result_label:
        result_label.config(text=overall_result)

    # Plot it all
    # fig = matplotlib.figure.Figure(figsize = (8, 8), dpi = 100)
    fig = matplotlib.figure.Figure()

    # adding the subplot
    plot1 = fig.add_subplot(111,
                            xlabel='Years', xlim=(options.start, options.end),
                            ylabel='Amount', ylim=(0, max_ytick),
                            yticks=range(0, max_ytick, 1000000))
    # plotting the graph
    for i in range(options.iterations):
        plot1.plot(the_years, results[i]['values'])

    # creating the Tkinter canvas containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().grid(row=8, column=0, columnspan=2)


def validate_and_next_step(root, balances_label, balances, withdraws_label, withdraws,
                           start_label, start, end_label, end,
                           iterations_label, iterations, howmuchtype, howmuchval,
                           result_label):
    elements = [
        { 'label': balances_label, 'entry': balances},
        { 'label': withdraws_label, 'entry': withdraws},
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
    if not os.path.exists(balances.get()):
        balances_label.config(fg="red")
        valid = False
    if not os.path.exists(withdraws.get()):
        withdraws_label.config(fg="red")
        valid=False

    if valid:
        howmuch = (howmuchtype.get(), float(howmuchval.get()))
        options = Options(int(start.get()), int(end.get()), int(iterations.get()), howmuch)
        run_simulator_and_plot_results(root, balances.get(), withdraws.get(), options, result_label)


def run_gui(root, balances, withdraws, options):
    # create main frame
    frame = tk.Frame(root)
    frame.grid(row=0, column=0)

    # Start Year
    start_label = tk.Label(frame, text="Start Year")
    start_label.grid(row=0, column=0)
    start_var = tk.StringVar()
    if options.start:
        start_var.set(options.start)
    tk.Entry(frame, textvariable=start_var).grid(row=1, column=0)

    # End Year
    end_label = tk.Label(frame, text="End Year")
    end_label.grid(row=0, column=1)
    end_var = tk.StringVar()
    if options.end:
        end_var.set(options.end)
    tk.Entry(frame, textvariable=end_var).grid(row=1, column=1)

    # Iterations
    iterations_label = tk.Label(frame, text="Iterations")
    iterations_label.grid(row=2, column=0)
    iterations_var = tk.StringVar()
    if options.iterations:
        iterations_var.set(options.iterations)
    tk.Entry(frame, textvariable=iterations_var).grid(row=3, column=0)

    # Balances
    balances_label = tk.Label(frame, text='Balances File')
    balances_label.grid(row=4, column=0, columnspan=2)
    balances_var = tk.StringVar()
    if balances:
        balances_var.set(balances)
    tk.Entry(frame, textvariable=balances_var).grid(row=5, column=0, columnspan=2)

    # Withdraws
    withdraws_label = tk.Label(frame, text='Withdraws File')
    withdraws_label.grid(row=6, column=0, columnspan=2)
    withdraws_var = tk.StringVar()
    if withdraws:
        withdraws_var.set(withdraws)
    tk.Entry(frame, textvariable=withdraws_var).grid(row=7, column=0, columnspan=2)

    # How much
    howmuch_label = tk.Label(frame, text='How much algorithm')
    howmuch_label.grid(row=8, column = 0)
    howmuchtype_var = tk.StringVar()
    if options.how_much:
        howmuchtype_var.set(options.how_much[0])
        logging.debug("Setting how much type to: {}".format(howmuchtype_var.get()))
    tk.Radiobutton(frame, text='Const %', variable=howmuchtype_var, value='c%').grid(row=9, column=0)
    tk.Radiobutton(frame, text='Const $', variable=howmuchtype_var, value='c$').grid(row=10, column=0)
    howmuchval_var = tk.StringVar()
    if options.how_much:
        howmuchval_var.set(options.how_much[1])
        logging.debug("Setting how much val to: {}".format(howmuchval_var.get()))
    tk.Entry(frame, textvariable=howmuchval_var).grid(row=9, column=1)

    # Results (below button)
    result_label = tk.Label(frame)
    result_label.grid(row=12, column=0, columnspan=2)
    # Button to run simulation
    btn = tk.Button(frame, text="Try It",
              command=lambda: validate_and_next_step(root,
                                                     balances_label, balances_var,
                                                     withdraws_label, withdraws_var,
                                                     start_label, start_var,
                                                     end_label, end_var,
                                                     iterations_label, iterations_var,
                                                     howmuchtype_var, howmuchval_var,
                                                     result_label))
    btn.grid(row=11, column=0, columnspan=2)

    frame.columnconfigure(0, weight=3)

@click.command()
@click.argument('balances', type=click.Path(exists=True))
@click.argument('withdraws', type=click.Path(exists=True))
@click.option('--start', type=click.INT, default=48, help='Age at the start of the simulation')
@click.option('--end', type=click.INT, default=90, help='Age at the end of the simulation')
@click.option('--iterations', type=click.INT, default=100, help='How many iterations to run')
@click.option('--how-much', '-hm', nargs=2, default=('c%',4.0))
@click.option('--gui/--no-gui', default=False, help='Launch gui')
@click.option('--debug', '-d', type=click.IntRange(0, 2, clamp=True), default=0)
@click.option('-s', '--seed', default=0, help='Random number seed')
def cli(balances, withdraws, start, end, iterations, how_much, gui, debug, seed):
    level = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}[debug]
    logging.basicConfig(filename='logs/debug.log', filemode='w',
                        format='%(levelname)s %(filename)s %(message)s',
                        level=level,
                        datefmt='%H:%M:%S')
    logging.info("Loading account data from: {}".format(balances))

    if seed:
        np.random.seed(int(seed))

    # the main Tkinter window
    window = tk.Tk()
    # setting the title
    window.title('Monte Carlo Retirement Simulation')
    # dimensions of the main window
    window.geometry("800x800")

    options = Options(start, end, iterations, how_much)
    logging.debug("Created options: \n{}".format(str(options)))

    if gui:
        run_gui(window, balances, withdraws, options)
    else:
        run_simulator_and_plot_results(window, balances, withdraws, options)

    # run the gui
    window.mainloop()
