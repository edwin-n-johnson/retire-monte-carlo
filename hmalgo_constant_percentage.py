import logging

class HMAlgoConstantPercentage:
    def __init__(self, percentage):
        self.withdrawal = 0
        self.percentage = percentage
        if self.percentage > 1:
            self.percentage /= 100
            logging.info("Auto-adjusting percentage from {:.2}%".format(percentage))
        logging.info("HMAlgo %age = {:.4}".format(self.percentage))


    def get_how_much_to_withdraw(self, prev_percentage, accounts):
        total_dollars = sum([a.get_total_value() for a in accounts])
        logging.debug("Total dollars = ${:,.2f}".format(total_dollars))
        if self.withdrawal == 0:
            self.withdrawal = self.percentage * total_dollars
            logging.info("HMAlgo {:.2}% of ${:,.2f} = ${:,.2f}"
                         .format(self.percentage, total_dollars, self.withdrawal))

        return self.withdrawal
