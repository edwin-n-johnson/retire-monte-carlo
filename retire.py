import sys
import argparse
from tax_manager import TaxManager
from hmalgo_constant_4 import HMAlgoConstant4
from hmalgo_constant_dollars import HMAlgoConstantDollars
from wdalgo_post_tax_first import WDAlgoPostTaxFirst
from simulator import run_simulation
import loader
import matplotlib.pyplot as plt
import numpy as np
import pprint

START_YEAR = 48
END_YEAR = 78
ITERATIONS = 100
# HOWMUCH_ALGORITHM = HMAlgoConstant4()
HOWMUCH_ALGORITHM = HMAlgoConstantDollars(120000)
WITHDRAW_ALGORITHM = WDAlgoPostTaxFirst()
TAX_MANAGER = TaxManager()

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('--seed', '-s')
args = parser.parse_args()
print("Loading account data from: {}".format(args.filename))

if args.seed:
    np.random.seed(int(args.seed))

results = []
for i in range(ITERATIONS):
    results.append({})

    # Load account data
    data = loader.load_accounts(args.filename)

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

# Plot it all
MAX_YTICK = 15000000
plt.xlabel('Years')
plt.xlim(START_YEAR, END_YEAR)
plt.ylabel('Amount')
plt.ylim(0, MAX_YTICK)
plt.yticks(range(0, MAX_YTICK, 1000000))
for i in range(ITERATIONS):
    plt.plot(the_years, results[i]['values'])
# Show it
plt.show()
