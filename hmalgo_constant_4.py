class HMAlgoConstant4:
    CONSTANT4 = 0.04

    def __init__(self):
        pass

    def get_how_much_to_withdraw(self, prev_percentage, accounts):
        total_dollars = 0
        for acct in accounts:
            total_dollars += acct.get_value()
        withdraw_dollars = self.CONSTANT4 * total_dollars
        return withdraw_dollars
