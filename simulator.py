import json
import logging
import csv
from rate_generator import RateGenerator

# SPY_MEAN = 0.1151
# SPY_STDDEV = 0.1960
SPY_MEAN = 0.0902  # 9.02% from https://www.lazyportfolioetf.com/etf/spdr-sp-500-spy/
SPY_STDDEV = 0.1649  # 16.49% from https://www.lazyportfolioetf.com/etf/spdr-sp-500-spy/
BND_MEAN = .0451  # 4.51% from https://www.lazyportfolioetf.com/etf/vanguard-total-bond-market-bnd/
BND_STDDEV = .0433
INFLATION_MEAN = 0.03  # 3.0% from https://www.bogleheads.org/forum/viewtopic.php?t=147583
INFLATION_STDDEV = 0.013  # From above


def run_simulation(iteration, years, account_manager, how_much_alg, withdraw_alg, tax_manager):
    prev_withdraw_rate = 0
    values_list = []
    inflation_list = []
    stock_return_list = []
    bond_return_list = []
    log_events = []
    logged = False
    csv_events = [['Year', 'Total Value', 'Withdraw Request', 'Withdraw Actual', 'Percentage',
                  'Tax Paid', 'Inflation', 'Stock Return', 'Bond Return']]

    # Create the rate generator with the right params
    rg = RateGenerator(SPY_MEAN, SPY_STDDEV, BND_MEAN, BND_STDDEV, 0.02, None)

    # Log first year values
    log_events.append({
        'Year': 'Start',
        'Total Value': account_manager.get_total_value(),
        'Account Values': account_manager.get_accounts_values(),
    })
    csv_events.append(['Start', account_manager.get_total_value(), 0, 0, 0, 0, 0, 0, 0])

    logging.info("=================== Iterations {} ====================".format(iteration))
    for year in years:
        inflation = rg.generate_inflation()
        inflation_list.append(inflation)
        stock_return = rg.generate_stock_return()
        stock_return_list.append(stock_return)
        bond_return = rg.generate_bond_return()
        bond_return_list.append(bond_return)

        total_value = account_manager.get_total_value()
        logging.info("Year {}: Total ${:,.2f}. inflation {:.2}% stocks {:.2}% bonds {:.2}%"
                     .format(year, total_value, 100*inflation, 100*stock_return, 100*bond_return))

        values_list.append(total_value)
        num = 5
        if total_value == 0 and not logged:
            logging.warning("!!! Iteration {} hit zero on year {}".format(iteration, year))
            logging.warning("!!! * First {} inflation: {}".format(num, ", ".join([str(x) for x in inflation_list[:num]])))
            logging.warning("!!! * First {} stock returns: {}".format(num, ", ".join([str(x) for x in stock_return_list[:num]])))
            logging.warning("!!! * First {} bond returns: {}".format(num, ", ".join([str(x) for x in bond_return_list[:num]])))
            logged = True

        requested_dollars = how_much_alg.get_how_much_to_withdraw(prev_withdraw_rate, account_manager)

        withdrawal, tax_paid = withdraw_alg.withdraw(account_manager, requested_dollars)
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
            'Account Values': account_manager.get_accounts_values()
        })
        csv_events.append([year, total_value, requested_dollars, withdrawal, round(percentage_of_portfolio, 2),
                           tax_paid, round(inflation, 2), round(stock_return, 2), round(bond_return, 2)])

        account_manager.apply_stock_return(stock_return)
        account_manager.apply_bond_return(bond_return)
        account_manager.apply_inflation(inflation)

        logging.info("------------------------------------------------------------")

    # Save log file
    with open('logs/events-{}.json'.format(iteration), 'w') as fp:
        json.dump(log_events, fp, indent=2)
    with open('logs/events-{}.csv'.format(iteration), 'w', newline='') as fp:
        c = csv.writer(fp, dialect='excel')
        for evt in csv_events:
            c.writerow(evt)

    # Return the values
    return values_list, inflation_list, stock_return_list, bond_return_list
