import streamlit as st
import numpy as np

import degiroapi

from degiro.portfolio import StockPortfolio
from degiro.account import Account
from degiro.utils import credentials



account = Account(**credentials())
portfolio = StockPortfolio(account)
current_portfolio_df = portfolio.current_values(dataframe=True)
money_spend = portfolio.transaction_value_total()
total_value = np.sum(current_portfolio_df.value)

st.title(f"Welcome👋")
st.caption(f"This dashboard shows you some insights in the stock portfolio of {account.name}")

col1,col2,col3 = st.columns([1,1,1],gap="medium")
col1.metric(label = "Stocks",value = len(current_portfolio_df) - 1)
col2.metric(label = "Value portfolio",value = f"€{total_value : .2f}",delta=f"{money_spend - total_value: .2f}")
col3.metric(label = "Cash",value = f"€{portfolio.cash}")
    #
    # with st.expander(""):
    #     st.write("""
    #              The value of my portfolio is based on the size multiplied by the price
    #              and the amount of cash on the account
    #          """)

# with col3:
#     st.write("The amount of cash on the account")
#     st.write(f"€{portfolio_dict['EUR']['value']}")

