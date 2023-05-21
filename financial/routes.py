from financial import app
from financial.helpers import paginator, calculate, param
from financial.response import Response


@app.route("/api/financial_data", methods=["GET"])
def get_financial_data():
    # getting the params
    try:
        start_date = param("start_date")
        end_date = param("end_date")
        symbol = param("symbol")
        limit = param("limit")
        page = param("page")
        return paginator(symbol, start_date, end_date, limit, page)
    except TypeError as e:
        return Response.summary(error=e.__str__())


@app.route("/api/statistics", methods=["GET"])
def get_statistics():
    try:
        start_date = param("start_date")
        end_date = param("end_date")
        symbol = param("symbol")

        return calculate(symbol, start_date, end_date)
    except TypeError as e:
        return Response.summary(error=e.__str__(), opts="sts")
