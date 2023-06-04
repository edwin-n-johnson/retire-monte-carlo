class Account:
    THRESHOLD = 5

    def __init__(self, acct_def, tax_manager):
        self.name = acct_def['name']
        self.info = acct_def
        if 'stocks' not in self.info['holdings']:
            self.info['holdings']['stocks'] = {'basis': 0, 'balance': 0}
        if 'bonds' not in self.info['holdings']:
            self.info['holdings']['bonds'] = {'basis': 0, 'balance': 0}
        self.tax_manager = tax_manager

    def get_name(self):
        return self.info['name']

    def get_values(self):
        # print(self.info['holdings'])
        retval = {}
        for t in ['cash', 'stocks', 'bonds']:
            retval[t] = self.info['holdings'][t]['balance']
        return retval

    def get_value(self, holding_type):
        return self.info['holdings'][holding_type]['balance']

    def get_total_value(self):
        return sum([self.get_value(h) for h in ['cash', 'stocks', 'bonds']])

    def set_value(self, holding_type, value):
        self.info['holdings'][holding_type]['balance'] = round(value, 2)

    def withdraw_pre(self, amount_requested_pre):
        # Iterate through the asset types to withdraw
        total_post = 0
        total_tax = 0
        holdings = self.info['holdings']
        for h in ['cash', 'stocks', 'bonds']:
            amount_of_type_pre = min(holdings[h]['balance'], amount_requested_pre)
            holdings[h]['balance'] -= amount_of_type_pre
            amount_requested_pre -= amount_of_type_pre
            post_tax, tax = self.tax_manager.split_it(self.info['type'], amount_of_type_pre)
            total_post += post_tax
            total_tax += tax
        return total_post, total_tax

    def withdraw(self, amount_requested_post):
        total_balance_pre = self.get_total_value()
        amount_requested_pre = self.tax_manager.how_much_pretax(self.info['type'], amount_requested_post)
        total_post, total_tax = self.withdraw_pre(amount_requested_pre)

        # Some sanity checks
        holdings = self.info['holdings']
        remaining_amount_post = amount_requested_post - total_post
        if remaining_amount_post < -self.THRESHOLD:
            raise RuntimeError('Badness: {}, {}, {}'.format(amount_requested_post, total_post, remaining_amount_post))
        if total_post - amount_requested_post > self.THRESHOLD:
            raise RuntimeError('Withholding more than asked: {}, {}'.format(amount_requested_post, total_post))
        if remaining_amount_post > self.THRESHOLD and \
                len([h for h in ['cash', 'stocks', 'bonds'] if holdings[h]['balance'] > 0]) > 0:
            # If there is more needed, then we should have cleaned out this account
            raise RuntimeError('Money still remaining: {}, {}'.format(remaining_amount_post, holdings))

        # Return post-tax dollars and tax paid
        return total_post, total_tax
