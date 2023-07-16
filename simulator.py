import json
import logging
import numpy as np
from account_factory import AccountFactory

# SPY_MEAN = 0.1151
# SPY_STDDEV = 0.1960
SPY_MEAN = 0.0902  # 9.02% from https://www.lazyportfolioetf.com/etf/spdr-sp-500-spy/
SPY_STDDEV = 0.1649  # 16.49% from https://www.lazyportfolioetf.com/etf/spdr-sp-500-spy/
BND_MEAN = .0451  # 4.51% from https://www.lazyportfolioetf.com/etf/vanguard-total-bond-market-bnd/
BND_STDDEV = .0433
INFLATION_MEAN = 0.03  # 3.0% from https://www.bogleheads.org/forum/viewtopic.php?t=147583
INFLATION_STDDEV = 0.013  # From above


def run_simulation(iteration, years, account_data, how_much_alg, withdraw_alg, tax_manager):
    accounts = AccountFactory.build_accounts(account_data, tax_manager)
    prev_withdraw_rate = 0
    values_list = []
    inflation_list = []
    stock_return_list = []
    bond_return_list = []
    log_events = []
    logged = False

    # Log first year values
    log_events.append({
        'Year': 'Start',
        'Total Value': round(sum([item for a in accounts for item in list(a.get_values().values())])),
        'Account Values': [{**{'Name': a.get_name()}, **a.get_values()} for a in accounts],
    })

    logging.info("=================== Iterations {} ====================".format(iteration))
    for year in years:
        inflation = 0.02 # max(0, round(np.random.normal(INFLATION_MEAN, INFLATION_STDDEV), 4))
        inflation_list.append(inflation)
        stock_return = round(np.random.normal(SPY_MEAN, SPY_STDDEV), 4)
        stock_return_list.append(stock_return)
        bond_return = round(np.random.normal(BND_MEAN, BND_STDDEV), 4)
        bond_return_list.append(bond_return)

        total_value = sum([item for a in accounts for item in list(a.get_values().values())])
        logging.info("Year {}: Total ${:,.2f}. inflation {:.2}% stocks {:.2}% bonds {:.2}%"
                     .format(year, total_value, 100*inflation, 100*stock_return, 100*bond_return))

        values_list.append(total_value)
        num = 5
        if total_value == 0 and not logged:
            logging.warn("Iteration {} hit zero on year {}".format(iteration, year))
            logging.warn(" * First {} inflation: {}".format(num, ", ".join([str(x) for x in inflation_list[:num]])))
            logging.warn(" * First {} stock returns: {}".format(num, ", ".join([str(x) for x in stock_return_list[:num]])))
            logging.warn(" * First {} bond returns: {}".format(num, ", ".join([str(x) for x in bond_return_list[:num]])))
            logged = True

        requested_dollars = how_much_alg.get_how_much_to_withdraw(prev_withdraw_rate, accounts)

        withdrawal, tax_paid = withdraw_alg.withdraw(accounts, requested_dollars)
        total_pre = withdrawal + tax_paid
        logging.info("         Withdrew ${:,.2f} + taxes ${:,.2f} = ${:,.2f}. Delta ${:,.2f}."
                     .format(withdrawal, tax_paid, total_pre, withdrawal - requested_dollars))

        percentage_of_portfolio = round(withdrawal / total_value, 4) if total_value else 0

        log_events.append({
            'Year': year,
            'Total Value': '${:,.2f}'.format(total_value),
            'Withdraw Request': '${:,.2f}'.format(requested_dollars),
            'Withdraw Actual': '${:,.2f}'.format(withdrawal),
            'Percentage': '{:2}%'.format(round(percentage_of_portfolio * 100, 2)),
            'Tax Paid': '${:,.2f}'.format(tax_paid),
            'Inflation': '{:2}%'.format(round(inflation * 100, 2)),
            'Stock Return': '{:2}%'.format(round(stock_return * 100, 2)),
            'Bond Return': '{:2}%'.format(round(bond_return * 100, 2)),
            'Account Values': [{**{'Name': a.get_name()}, **a.get_values()} for a in accounts],
        })

        for acct in accounts:
            # Market returns
            acct.set_value('stocks', acct.get_value('stocks') * (1 + stock_return))
            acct.set_value('bonds', acct.get_value('bonds') * (1 + bond_return))
            # Inflation
            acct.set_value('stocks', acct.get_value('stocks') / (1 + inflation))
            acct.set_value('bonds', acct.get_value('bonds') / (1 + inflation))
            # More logging

        logging.info("------------------------------------------------------------")

    # Save log file
    with open('logs/events-{}.json'.format(iteration), 'w') as fp:
        json.dump(log_events, fp, indent=2)

    # Return the values
    return values_list, inflation_list, stock_return_list, bond_return_list
