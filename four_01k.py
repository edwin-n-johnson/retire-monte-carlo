from account import Account


class FourOhOneKay(Account):
    def __init__(self, info, tax_manager):
        super().__init__(info, tax_manager)

    @staticmethod
    def get_is_tax_paid():
        return False
