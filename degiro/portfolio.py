from degiro.account import Account

import pandas as pd
import numpy as np

from datetime import datetime,timedelta
import degiroapi

class StockPortfolio:
    def __init__(self,account: Account):
        self.account = account
    def _raw_current_values(self):
        return self.account.getdata(degiroapi.Data.Type.PORTFOLIO,True)
    def current_values(self,dataframe=False):

        stock_dict =  {self.account.product_info(stock["id"])["name"] : stock for stock in self._raw_current_values()}
        self.cash = stock_dict["EUR"]["value"]

        if dataframe:
            return (pd.DataFrame(stock_dict)
                    .T
                    .assign(calc_buy_value = lambda df: df["size"]*df["breakEvenPrice"])
                    )
        else:
            return stock_dict

    def transactions(self,
                     from_date: datetime = datetime.now() - timedelta(days=30),
                     to_date:datetime = datetime.now()):
        return self.account.transactions(from_date=from_date,
                                  to_date=to_date)
    def transactions_df(self,
                        cols : list = ['id', 'productId', 'date', 'buysell', 'price', 'quantity', 'total','fxRate']
                        ) -> pd.DataFrame:
        if cols:
            return pd.DataFrame(self.transactions()).loc[:,cols]
        else:
            return pd.DataFrame(self.transactions())
    def all_transactions(self) -> dict:
        return self.account.transactions(from_date=datetime(1900,1,1),
                                  to_date=datetime.now())
    def all_transactions_df(self,
                            cols: list = ['id', 'productId', 'date', 'buysell', 'price', 'quantity', 'total', 'fxRate'],
                            ) -> pd.DataFrame:
        if cols:
            return pd.DataFrame(self.all_transactions()).loc[:,cols]
        else:
            return pd.DataFrame(self.all_transactions())
    def transaction_value_total(self) -> float:
        transactions = self.all_transactions_df()
        buy_orders = transactions.loc[lambda df: df["buysell"] == "B"]
        sell_orders = transactions.loc[lambda df: df["buysell"] != "B"]
        buy_value = np.sum(np.where(buy_orders["fxRate"] > 0,buy_orders["total"]/buy_orders["fxRate"],buy_orders["total"]))
        pd.set_option("display.max_rows",150)
        pd.set_option("display.max_columns", 10)

        sell_value = np.sum(np.where(sell_orders["fxRate"] > 0,sell_orders["total"]/sell_orders["fxRate"],sell_orders["total"]))


        return np.abs(buy_value + sell_value)

    def transaction_value(self,
                          from_date: datetime = datetime.now() - timedelta(days=30),
                          to_date:datetime = datetime.now()
                          ) -> float:
        transactions = self.transactions(from_date=from_date,
                                         to_date=to_date)
        buyorders = [transaction["total"]/transaction["fxRate"] for transaction in transactions if transaction["buysell"] == "B"]
        sellorders = [transaction["total"]*transaction["fxRate"] for transaction in transactions if transaction["buysell"] != "B"]
        print(f"{buyorders=}\n{sellorders=}")