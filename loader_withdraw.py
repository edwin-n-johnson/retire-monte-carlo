import json
import logging


class WithdrawAlgo:
    LOOP_DOLLARS = 1000

    def __init__(self, fname):
        self._fname = fname
        with open(fname) as f:
            self._strategy = json.load(f)

    def _run_withdrawal(self, accounts, amount_post):
        remaining_amount_post = amount_post
        total_tax_paid = 0
        for acct in accounts:
            amount_withdrawn_post, tax_paid = acct.withdraw(remaining_amount_post)
            remaining_amount_post -= amount_withdrawn_post
            total_tax_paid += tax_paid

            if remaining_amount_post <= 0:  # We've gotten all the money we need
                break

        return amount_post - remaining_amount_post, total_tax_paid

    def withdraw(self, account_manager, amount_requested):
        amount_remaining = amount_requested
        total_tax_paid = 0
        for account_json in self._strategy:
            name = account_json['account']
            # Get the account with matching name
            account = account_manager.get_account_by_name(name)
            # See how much money we can get from this account including taxes
            amount_withdrawn, tax_paid = account.withdraw(amount_remaining)
            logging.info("[{}] withdraw ${:,.2f} tax ${:,.2f}".format(name, amount_withdrawn, tax_paid))
            amount_remaining -= amount_withdrawn
            total_tax_paid += tax_paid
            # Did we get what we needed?
            if amount_remaining == 0:
                break
        return amount_requested - amount_remaining, total_tax_paid

    # def withdraw_old(self, account_manager, amount_requested):
    #     accounts_post = [a for a in accounts if a.get_is_tax_paid()]
    #     amount_withdrawn_post, tax_paid = self._run_withdrawal(accounts_post, amount_requested_post)
    #
    #     amount_withdrawn2_post = 0
    #     tax_paid2 = 0
    #     if amount_withdrawn_post != amount_requested_post:
    #         # If we didn't get what we needed, use the pre-tax accounts
    #         accounts_pre = [a for a in accounts if not a.get_is_tax_paid()]
    #         amount_needed_post = amount_requested_post - amount_withdrawn_post
    #         amount_withdrawn2, tax_paid2 = self.run_withdrawal(accounts_pre, amount_needed_post)
    #
    #     return amount_withdrawn_post + amount_withdrawn2_post, tax_paid + tax_paid2
