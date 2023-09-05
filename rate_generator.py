import numpy as np


class RateGenerator:
    def __init__(self, stock_mean, stock_stddev, bond_mean, bond_stddev, inflation_mean, inflation_stddev):
        self.stocks = (stock_mean, stock_stddev)
        self.bonds = (bond_mean, bond_stddev)
        self.inflation = (inflation_mean, inflation_stddev)

    def set_stocks_params(self, mean: float, stddev: float = None):
        self.stocks = (mean, stddev)

    def set_bonds_params(self, mean: float, stddev: float = None):
        self.bonds = (mean, stddev)

    def set_inflation_params(self, mean: float, stddev: float = None):
        self.inflation = (mean, stddev)

    def generate_stock_return(self):
        # If stddev not set, just return mean
        if not self.stocks[1]:
            return self.stocks[0]
        # Generate random distribution
        return round(np.random.normal(loc=self.stocks[0], scale=self.stocks[1]), 4)

    def generate_bond_return(self):
        # If stddev not set, just return mean
        if not self.bonds[1]:
            return self.bonds[0]
        # Generate random distribution
        return round(np.random.normal(self.bonds[0], self.bonds[1]), 4)

    def generate_inflation(self):
        # If stddev not set, just return mean
        if not self.inflation[1]:
            return self.inflation[0]
        # Generate random distribution
        return round(np.random.normal(self.inflation[0], self.inflation[1]), 4)

