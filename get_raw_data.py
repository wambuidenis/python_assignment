from financial.response import Response
from financial.helpers import get_raw_data

try:
    symbols = ["AAPL", "IBM"]
    [get_raw_data(symbol) for symbol in symbols]
except TypeError as e:
    Response.summary(error=e.__str__(), opts="inf")



