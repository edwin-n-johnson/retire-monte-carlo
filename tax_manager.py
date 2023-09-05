class TaxManager:
    CAPITAL_GAINS = 0.15  # 15% for $120,000 income
    INCOME = 0.147  # 14.7% for $120,000

    CAPITAL_GAINS_TABLE = [
        {'rate': 0.00, 'end': 41675},
        {'rate': 0.15, 'end': 459750},
        {'rate': 0.20, 'end': 1000000000000}
    ]

    INCOME_TAX_TABLE = [
        {'rate': 0.10, 'end':  20550, 'prev_tax': 0},
        {'rate': 0.12, 'end':  83550, 'prev_tax': 2055},
        {'rate': 0.22, 'end': 178150, 'prev_tax': 9615},
        {'rate': 0.24, 'end': 340100, 'prev_tax': 30427},
        {'rate': 0.32, 'end': 431900, 'prev_tax': 69295},
        {'rate': 0.35, 'end': 647850, 'prev_tax': 98671},
        {'rate': 0.37, 'end': 1000000000000, 'prev_tax': 174253.50},
    ]

    def __init__(self):
        pass

    def tax_gains(self, amount):
        return round(self.CAPITAL_GAINS * amount)

    def tax_income(self, amount):
        return round(self.INCOME * amount)

    def get_rate(self, account_type):
        match account_type:
            case 'Brokerage':
                return self.CAPITAL_GAINS
            case '401k':
                return self.INCOME
            case 'RolloverIRA':
                return self.INCOME
            case 'RothIRA':
                return 0
            case 'TradIRA':
                return self.INCOME
            case _:
                raise RuntimeError('Unknown account type: {}'.format(account_type))

    def split_it(self, account_type, amount):
        rate = self.get_rate(account_type)
        tax = round(rate * amount)
        money_post = amount - tax

        return money_post, tax

    def how_much_pretax(self, account_type, amount_post):
        rate = self.get_rate(account_type)
        return round(amount_post / (1 - rate))

    @staticmethod
    def lookup_rate(table, value):
        start = 0
        for i in range(len(table)):
            row = table[i]
            # Get the end value
            end = row['end']
            # Is it in the right range
            if start <= value <= end:
                prev_tax = row['prev_tax'] if 'prev_tax' in row else None
                return row['rate'], prev_tax
            # Move start value
            start = end + 1
        raise RuntimeError("Unable to find a matching rate: {}, {}".format(table, value))
