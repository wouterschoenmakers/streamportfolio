from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import datetime,timedelta,timezone
import logging

from degiro.account import Account
from degiro.utils import datatypes

import degiroapi

now = datetime.now(timezone.utc)
class StockPortfolio:
    def __init__(self,account: Account):
        self.account = account
        self.raw_current_values = None
        self.product_information = None
        self.transactions_subset = None
        self.transactions_complete_df = None

    def _raw_values(self):
        if self.raw_current_values == None:
            self.raw_current_values = self.account.getdata(degiroapi.Data.Type.PORTFOLIO,True)
            return self.raw_current_values
        else:
            return self.raw_current_values
    def _product_info(self):
        if self.product_information is None:
            self.product_information = {stock["id"]: self.account.product_info(stock["id"]) for stock in self._raw_values()}
        else:
            logging.info("Already retrieved")
    def _inverse_mapping(self,mapping : dict) -> dict:
        return {v: k for k, v in mapping.items()}
    def isin_mapper(self,inverse: bool = False) -> dict:
        """Returns a dictonary of Product ID and ISIN code"""
        if self.product_information is None:
            self._product_info()
        mapping =  {stock["id"]: self.product_information[stock["id"]]["isin"] for stock in self._raw_values()}
        if inverse:
            mapping = self._inverse_mapping(mapping)
        return mapping
    def name_mapper(self,inverse : bool = False) -> dict:
        """Returns dictonary of Degiro's Product ID and company name"""
        if self.product_information is None:
            self._product_info()
        mapping = {stock["id"] : self.product_information[stock["id"]]["name"] for stock in self._raw_values()}
        if inverse:
           mapping = self._inverse_mapping(mapping)
        return mapping
    def current_values(self,dataframe=False) -> dict | pd.DataFrame:
        if self.product_information is None:
            self._product_info()
        stock_dict =  {self.product_information[stock["id"]]["name"] : stock for stock in self._raw_values()}
        self.cash = stock_dict["EUR"]["value"]

        if dataframe:
            return (pd.DataFrame(stock_dict)
                    .T
                    .assign(calc_buy_value = lambda df: df["size"]*df["breakEvenPrice"])
                    )
        else:
            return stock_dict
    def transactions(self,
                     from_date: datetime = now - timedelta(days=30),
                     to_date:datetime = now):
        self.transactions_subset =  self.account.transactions(from_date=from_date,
                                  to_date=to_date)
        return self.transactions_subset

    def transactions_df(self,
                        cols : list = ['id', 'productId', 'date', 'buysell', 'price', 'quantity', 'total','fxRate'],
                        from_date: datetime = now - timedelta(days=30),
                        to_date: datetime = now,
                        ) -> pd.DataFrame:

        if cols:
           return pd.DataFrame(self.transactions(from_date=from_date,to_date=to_date)).loc[:,cols]
        else:
           return pd.DataFrame(self.transactions())
    def all_transactions(self) -> dict:
        self.transactions_complete =  self.account.transactions(
                                                    from_date=datetime(1900,1,1),
                                                    to_date=datetime.now()
        )

        return self.transactions_complete
    def all_transactions_df(self,
                            cols: list = ['id', 'productId', 'date', 'buysell', 'price', 'quantity', 'totalInBaseCurrency', 'totalFeesInBaseCurrency'],
                            dtype_converter : dict = datatypes) -> pd.DataFrame:

        if cols:
            if self.transactions_complete_df:
                df =  pd.DataFrame(self.transactions_complete).loc[:,cols]
            else:
                df =  pd.DataFrame(self.all_transactions()).loc[:,cols]
        else:
            df =  pd.DataFrame(self.all_transactions())
        self.transactions_complete_df = True
        self.trans_df = df.assign(date = lambda df: pd.to_datetime(df.date))
        return self.trans_df
    def transaction_value_total(self) -> float:
        transactions = self.all_transactions_df()
        buy_orders = transactions.loc[lambda df: df["buysell"] == "B"]
        sell_orders = transactions.loc[lambda df: df["buysell"] != "B"]
        buy_value = np.sum(buy_orders["totalInBaseCurrency"])
        sell_value = np.sum(sell_orders.loc[:,"totalInBaseCurrency"])

        return np.abs(buy_value + sell_value)
    def transaction_value(self,
                          from_date: datetime = now - timedelta(days=30),
                          to_date:datetime = now
                          ) -> float:
        transactions = self.transactions(from_date=from_date,
                                         to_date=to_date)
        buyorders = [transaction["total"]/transaction["fxRate"] for transaction in transactions if transaction["buysell"] == "B"]
        sellorders = [transaction["total"]*transaction["fxRate"] for transaction in transactions if transaction["buysell"] != "B"]
        print(f"{buyorders=}\n{sellorders=}")
    def transaction_fee_between(self,
                          from_date: datetime = now - timedelta(days=30),
                          to_date : datetime = now) -> float:
        if not self.transactions_complete_df:
            self.trans_df = self.all_transactions_df()
        transaction_fees = self.trans_df.loc[lambda df: (df["date"] > from_date.astimezone()) & (df["date"] <= to_date),"totalFeesInBaseCurrency"]
        return np.sum(transaction_fees)

    def transaction_fee(self):
        if not self.transactions_complete_df:
            self.trans_df = self.all_transactions_df()
        return np.sum(np.abs(self.trans_df["totalFeesInBaseCurrency"]))

    def active(self):
        if not self.transactions_complete_df:
            self.trans_df = self.all_transactions_df()
        return (now - self.trans_df.date.min()).days

    def n_transactions(self)-> int:
        if not self.transactions_complete_df:
            self.trans_df = self.all_transactions_df()
        return len(self.trans_df)
    def nunique(self) -> int:
        if not self.transactions_complete_df:
            self.trans_df = self.all_transactions_df()
        return self.trans_df["productId"].nunique()



