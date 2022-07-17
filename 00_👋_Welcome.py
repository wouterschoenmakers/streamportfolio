import streamlit as st
import numpy as np

from degiro.portfolio import StockPortfolio
from degiro.account import Account
from degiro.utils import credentials

from page_utils.pages_conf import gap
from page_utils.metrics_info import metrics_info0

account = Account(**credentials())
portfolio = StockPortfolio(account)
current_portfolio_df = portfolio.current_values(dataframe=True)
money_spend = portfolio.transaction_value_total()
print(current_portfolio_df)
total_value = np.sum(current_portfolio_df.value)


st.title(f"Welcome👋")
st.caption(f"This dashboard shows you some insights in the stock portfolio of {account.name} "
           f"after the first transaction which was {portfolio.active()} days ago.")
# col21.metric(label = "Already active", value = f"{portfolio.active()} days", help=metrics_info0["active"])

metrics_info0 = {
    "stocks":" The number of stocks is based on the number of products, cash is **not** included",
    "portfolio_value":"The portfolio value is calculated by taking the sum of the multiplication of the size and the current price of the stocks and the amount of cash on the account.",
    "cash":"The cash is the amount of euro's that is **not** invested",
    "invested":"The amount of invested euro's is based on the difference between the value of the buy and sell transactions",
    "active":"The active days is based on the timedelta between the first transaction and now",
    "transaction_fee":"Sum of all the transactions fee expressed in Euro's",
    "total":"Sum of portfolio value and cash on the account"
    }


col1,col2, = st.columns([1,1],gap=gap)
col1.metric(label="Total on account:", value = f"€{total_value:.2f}", delta=f"{total_value - money_spend : .2f}", help=metrics_info0["total"])
col2.metric(label = "Portfolio value", value = f"€{total_value - portfolio.cash : .2f}", help=metrics_info0["portfolio_value"])

col1,col2, = st.columns([1,1],gap=gap)
col1.metric(label = "Euro's invested", value = f"€{money_spend : .2f}", help = metrics_info0["invested"])#delta=f"{money_spend - (total_value + portfolio.transaction_fee): .2f}")
col2.metric(label = "Cash on account", value = f"€{portfolio.cash:.2f}", help=metrics_info0["cash"])

col1,col2= st.columns([1,1],gap=gap)
col1.metric(label = "Stocks", value = len(current_portfolio_df) - 1, help=metrics_info0["stocks"])
col2.metric(label="Unique stocks",value=portfolio.nunique(),help = metrics_info0["nunique_stocks"])

col1, col2= st.columns([1,1],gap=gap)
col1.metric(label="Number of Transactions",value = f"{portfolio.n_transactions()}")
col2.metric(label="Transaction fee", value = f"€{portfolio.transaction_fee():.2f}", help=metrics_info0["transaction_fee"])








