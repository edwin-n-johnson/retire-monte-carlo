from brokerage import Brokerage
from four_01k import FourOhOneKay
from rollover_ira import RolloverIRA
from roth_ira import RothIRA
from trad_ira import TradIRA


class AccountFactory:

    @staticmethod
    def build_accounts(multiple_data, tax_manager):
        accounts = []
        for data in multiple_data:
            match data['type']:
                case 'Brokerage':
                    accounts.append(Brokerage(data, tax_manager))
                case '401k':
                    accounts.append(FourOhOneKay(data, tax_manager, year=60))
                case 'RolloverIRA':
                    accounts.append(RolloverIRA(data, tax_manager, year=60))
                case 'RothIRA':
                    accounts.append(RothIRA(data, tax_manager, year=60))
                case 'TradIRA':
                    accounts.append(TradIRA(data, tax_manager, year=60))
                case _:
                    raise RuntimeError('Unknown account type: {}'.format(data['type']))
        return accounts
