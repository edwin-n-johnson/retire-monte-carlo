import sys
import csv
import locale
import pprint
import logging

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


def stof(string):
    return round(locale.atof(string))


def load_accounts_cost_basis(lines, enable_logging=True):
    # Parse the lines
    data = []
    account = None
    for line in lines:
        if len(line) == 1:
            account = {'name': line[0], 'type': NAMES_TO_TYPES[line[0]], 'holdings': {}}
        elif len(line) == 3 and 'TOTAL Investments' in line[0]:
            pass
        elif len(line) == 3 and 'TOTAL' in line[0]:
            account['total'] = {'basis': stof(line[1]), 'balance': stof(line[2])}
            data.append(account)
            account = None
        elif len(line) == 3 and 'TOTAL' not in line[0]:
            t = FUNDS_TO_TYPES[line[0]]
            if t not in account['holdings'].keys():
                account['holdings'][t] = {'basis': 0, 'balance': 0}
            account['holdings'][t]['basis'] += stof(line[1])
            account['holdings'][t]['balance'] += stof(line[2])
        else:
            raise RuntimeError('Invalid line: {}'.format(line))

    return data


def load_accounts_asset_alloc(lines, enable_logging=True):
    # Parse the lines
    data = []
    account = None
    for line in lines:
        if len(line) == 1:
            if enable_logging:
                logging.debug('Found acct start: {}'.format(line[0]))
            account = {'name': line[0], 'type': NAMES_TO_TYPES[line[0]], 'holdings': {}}
        elif len(line) == 3 and 'TOTAL Investments' in line[0]:
            pass
        elif len(line) == 4 and 'TOTAL' in line[0]:
            if enable_logging:
                logging.debug('Found acct total: {} -> {}'.format(account['name'], line[3]))
            basis_s = line[1]
            if '*' in basis_s:
                basis_s = basis_s[:-1]
            account['total'] = {'basis': stof(basis_s), 'balance': stof(line[3])}
            data.append(account)
            account = None
        elif len(line) in [4, 7, 8] and 'TOTAL' not in line[0]:
            t = FUNDS_TO_TYPES[line[0]]
            if t not in account['holdings'].keys():
                account['holdings'][t] = {'basis': 0, 'balance': 0}
            if len(line) == 4:
                basis = stof(line[1])
                balance = stof(line[3])
            elif len(line) == 7:
                basis = stof(line[4])
                balance = stof(line[6])
            elif len(line) == 8:
                basis = stof(line[5])
                balance = stof(line[7])
            else:
                raise RuntimeError('Invalid line: {}'.format(line))

            if enable_logging:
                logging.debug('  Found fund {} ({}) -> ${:,.2f}'.format(line[0], t, balance))
            account['holdings'][t]['basis'] += basis
            account['holdings'][t]['balance'] += balance

        else:
            raise RuntimeError('Invalid line: {}'.format(line))

    return data


def load_accounts(filename, enable_logging=True):
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
    if enable_logging:
        logging.debug("Initial parsing:")
        logging.debug(lines)
    file_obj.close()

    first_line = lines[0][0]
    # Remove a few lines that are not needed
    for i in [-2, -1, 1, 0]:
        del lines[i]
    if enable_logging:
        logging.debug("After cleanup")
        logging.debug(lines)

    # What type are we
    data = None
    if 'Cost Basis' in first_line:
        data = load_accounts_cost_basis(lines, enable_logging=enable_logging)
    elif 'Asset Allocation' in first_line:
        data = load_accounts_asset_alloc(lines, enable_logging=enable_logging)
    else:
        raise RuntimeError('Invalid first line: {}'.format(first_line))

    return data
