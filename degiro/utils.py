import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

def credentials(username_key:str = "USER",
                password_key:str = "PASSWORD") -> [str,str]:
    """Retrieve username and password from env file"""
    load_dotenv()
    username, password = os.getenv(username_key), os.getenv(password_key);
    return {"username":username,"password":password}

datatypes = {
    'id':str,
    'productId':str,
    'buysell':str,
    'price':float,
    'quantity':float,
    'totalInBaseCurrency':float,
    'totalFeesInBaseCurrency':float
}