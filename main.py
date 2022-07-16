
from degiro.portfolio import StockPortfolio
from degiro.account import Account
from degiro.utils import credentials

if __name__=="__main__":
    account = Account(**credentials())
    portfolio = StockPortfolio(account)
    current_portfolio_df = portfolio.current_values(dataframe=True)

