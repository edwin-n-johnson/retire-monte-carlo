import locale
import logging
import csv
from account import Account
from brokerage import Brokerage
from four_01k import FourOhOneKay
from rollover_ira import RolloverIRA
from roth_ira import RothIRA
from trad_ira import TradIRA


class AccountManager:
    NAMES_TO_TYPES = {
        'Ed Brokerage': 'Brokerage',
        'Ed rIRA': 'RothIRA',
        'Ed rollover IRA': 'RolloverIRA',
        'Ed tIRA': 'TradIRA',
        'Joint E*Trade': 'Brokerage',
        'Wendy Fidelity': 'Brokerage',
        'Wendy GHX 401(k)': '401k',
        'Wendy Maxar 401(k)': '401k',
        'Wendy Rollover IRA': 'RolloverIRA',
        'Wendy tIRA': 'TradIRA',
    }

    FUNDS_TO_TYPES = {
        '-Cash-': 'cash',
        'Vanguard Total Stock Mkt Idx Adm': 'stocks',
        'Market Vextors Fallen Angel High Yield Bond ETF': 'bonds',
        'Vanguard Emerging Markets Govt Bond ETF': 'bonds',
        'Vanguard REIT ETF': 'stocks',
        'Vanguard S&P Small-Cap 600 ETF': 'stocks',
        'Vanguard Total Bond Mkt Index Adm': 'bonds',
        "iShares Int'l Select Dividend ETF": 'stocks',
        'Vanguard Inflation-Protected Inv': 'bonds',
        'Vanguard Tax Managed Small Cap Index': 'stocks',
        'Vanguard Total Internation Stock Ind Adm': 'stocks',
        'Fidelity Freedom Index 2030 Investor': 'stocks',
        'Fidelity Freedom 2030 IPR': 'stocks',
        'Fidelity Freedom 2040': 'stocks',
    }

    def __init__(self, tax_manager):
        self.tax_manager = tax_manager
        self.logging_enabled = False
        self.accounts = []
        self.data = []

    def clear(self):
        self.accounts = []
        self.data = []

    def get_data(self):
        return self.data

    def toggle_logging(self):
        self.logging_enabled = not self.logging_enabled

    def get_total_value(self):
        return round(sum([item for a in self.accounts for item in list(a.get_values().values())]))

    def get_accounts_values(self):
        return [{**{'Name': a.get_name()}, **a.get_values()} for a in self.accounts]

    def get_account_by_name(self, name):
        return [a for a in self.accounts if a.get_name() == name][0]

    def apply_stock_return(self, stock_return: float):
        for acct in self.accounts:
            acct.set_value('stocks', acct.get_value('stocks') * (1 + stock_return))

    def apply_bond_return(self, bond_return: float):
        for acct in self.accounts:
            acct.set_value('bonds', acct.get_value('bonds') * (1 + bond_return))

    def apply_inflation(self, inflation: float):
        for acct in self.accounts:
            acct.set_value('stocks', acct.get_value('stocks') / (1 + inflation))
            acct.set_value('bonds', acct.get_value('bonds') / (1 + inflation))

    @staticmethod
    def _stof(string):
        return round(locale.atof(string))

    def load_accounts(self, filename):
        # Clear out old account info
        self.clear()
        # Open the file
        file_obj = open(filename, "r")
        file_obj.seek(0)
        locale.setlocale(locale.LC_ALL, '')
        reader = csv.reader(file_obj, dialect='excel-tab')
        lines = []
        # Read the file and create a list of lines skipping blanks
        for line in reader:
            items = [x for x in line if x]
            if items:
                lines.append(items)
        if self.logging_enabled:
            logging.debug("Initial parsing:")
            logging.debug(lines)
        file_obj.close()

        first_line = lines[0][0]
        # Remove a few lines that are not needed
        for i in [-2, -1, 1, 0]:
            del lines[i]
        if self.logging_enabled:
            logging.debug("After cleanup")
            logging.debug(lines)

        # What type are we
        if 'Cost Basis' in first_line:
            self._load_accounts_cost_basis(lines)
        elif 'Asset Allocation' in first_line:
            self._load_accounts_asset_alloc(lines)
        else:
            raise RuntimeError('Invalid first line: {}'.format(first_line))

        # Build the actual accounts
        self._build_accounts()

    def _build_accounts(self):
        for the_data in self.data:
            match the_data['type']:
                case 'Brokerage':
                    self.accounts.append(Brokerage(the_data, self.tax_manager))
                case '401k':
                    self.accounts.append(FourOhOneKay(the_data, self.tax_manager, year=60))
                case 'RolloverIRA':
                    self.accounts.append(RolloverIRA(the_data, self.tax_manager, year=60))
                case 'RothIRA':
                    self.accounts.append(RothIRA(the_data, self.tax_manager, year=60))
                case 'TradIRA':
                    self.accounts.append(TradIRA(the_data, self.tax_manager, year=60))
                case _:
                    raise RuntimeError('Unknown account type: {}'.format(the_data['type']))

    def _load_accounts_cost_basis(self, lines):
        # Parse the lines
        account = None
        for line in lines:
            if len(line) == 1:
                account = {'name': line[0], 'type': self.NAMES_TO_TYPES[line[0]], 'holdings': {}}
            elif len(line) == 3 and 'TOTAL Investments' in line[0]:
                pass
            elif len(line) == 3 and 'TOTAL' in line[0]:
                account['total'] = {'basis': self._stof(line[1]), 'balance': self._stof(line[2])}
                self.data.append(account)
                account = None
            elif len(line) == 3 and 'TOTAL' not in line[0]:
                t = self.FUNDS_TO_TYPES[line[0]]
                if t not in account['holdings'].keys():
                    account['holdings'][t] = {'basis': 0, 'balance': 0}
                account['holdings'][t]['basis'] += self._stof(line[1])
                account['holdings'][t]['balance'] += self._stof(line[2])
            else:
                raise RuntimeError('Invalid line: {}'.format(line))

    def _load_accounts_asset_alloc(self, lines):
        # Parse the lines
        account = None
        for line in lines:
            if len(line) == 1:
                if self.logging_enabled:
                    logging.debug('Found acct start: {}'.format(line[0]))
                account = {'name': line[0], 'type': self.NAMES_TO_TYPES[line[0]], 'holdings': {}}
            elif len(line) == 3 and 'TOTAL Investments' in line[0]:
                pass
            elif len(line) == 4 and 'TOTAL' in line[0]:
                if self.logging_enabled:
                    logging.debug('Found acct total: {} -> {}'.format(account['name'], line[3]))
                basis_s = line[1]
                if '*' in basis_s:
                    basis_s = basis_s[:-1]
                account['total'] = {'basis': self._stof(basis_s), 'balance': self._stof(line[3])}
                self.data.append(account)
                account = None
            elif len(line) in [4, 7, 8] and 'TOTAL' not in line[0]:
                t = self.FUNDS_TO_TYPES[line[0]]
                if t not in account['holdings'].keys():
                    account['holdings'][t] = {'basis': 0, 'balance': 0}
                if len(line) == 4:
                    basis = self._stof(line[1])
                    balance = self._stof(line[3])
                elif len(line) == 7:
                    basis = self._stof(line[4])
                    balance = self._stof(line[6])
                elif len(line) == 8:
                    basis = self._stof(line[5])
                    balance = self._stof(line[7])
                else:
                    raise RuntimeError('Invalid line: {}'.format(line))

                if self.logging_enabled:
                    logging.debug('  Found fund {} ({}) -> ${:,.2f}'.format(line[0], t, balance))
                account['holdings'][t]['basis'] += basis
                account['holdings'][t]['balance'] += balance

            else:
                raise RuntimeError('Invalid line: {}'.format(line))
