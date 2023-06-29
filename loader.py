import csv
import locale

NAMES_TO_TYPES = {
    'Ed Brokerage': 'Brokerage',
    'Ed rIRA': 'RothIRA',
    'Ed rollover IRA': 'RolloverIRA',
    'Ed tIRA': 'TradIRA',
    'Joint E*Trade': 'Brokerage',
    'Wendy Fidelity': 'Brokerage',
    'Wendy GHX 401(k)': '401k',
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


def load_accounts(filename):
    locale.setlocale(locale.LC_ALL, '')
    with open(filename, newline='') as f:
        reader = csv.reader(f, dialect='excel-tab')
        lines = []
        # Read the file and create a list of lines skipping blanks
        for line in reader:
            items = [x for x in line if x]
            if items:
                lines.append(items)

        # Remove a few lines that are not needed
        del lines[-1]
        del lines[1]
        del lines[0]

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
