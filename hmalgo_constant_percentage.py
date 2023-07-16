import logging

class HMAlgoConstantPercentage:
    def __init__(self, percentage):
        self.percentage = percentage
        if self.percentage > 1:
            self.percentage /= 100
            logging.info("Auto-adjusting percentage from {:.2}%".format(percentage))
        logging.info("HMAlgo = {:.4}".format(self.percentage))

    def get_how_much_to_withdraw(self, prev_percentage, accounts):
        total_dollars = 0
        for acct in accounts:
            total_dollars += acct.get_total_value()
        logging.debug("Total dollars = ${:,.2f}".format(total_dollars))
        withdraw_dollars = self.percentage * total_dollars
        logging.debug("How much to withdraw = ${:,.2f}".format(withdraw_dollars))
        return withdraw_dollars
