class WDAlgoPostTaxFirst:
    LOOP_DOLLARS = 1000

    def __init__(self):
        pass

    @staticmethod
    def run_withdrawal(accounts, amount_post):
        remaining_amount_post = amount_post
        total_tax_paid = 0
        for acct in accounts:
            amount_withdrawn_post, tax_paid = acct.withdraw(remaining_amount_post)
            remaining_amount_post -= amount_withdrawn_post
            total_tax_paid += tax_paid

            if remaining_amount_post <= 0:  # We've gotten all the money we need
                break

        return amount_post - remaining_amount_post, total_tax_paid

    def withdraw(self, accounts, amount_requested_post):
        accounts_post = [a for a in accounts if a.get_is_tax_paid()]
        amount_withdrawn_post, tax_paid = self.run_withdrawal(accounts_post, amount_requested_post)

        amount_withdrawn2_post = 0
        tax_paid2 = 0
        if amount_withdrawn_post != amount_requested_post:
            # If we didn't get what we needed, use the pre-tax accounts
            accounts_pre = [a for a in accounts if not a.get_is_tax_paid()]
            amount_needed_post = amount_requested_post - amount_withdrawn_post
            amount_withdrawn2, tax_paid2 = self.run_withdrawal(accounts_pre, amount_needed_post)

        return amount_withdrawn_post + amount_withdrawn2_post, tax_paid + tax_paid2
