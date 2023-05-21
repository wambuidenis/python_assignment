import logging as log
from datetime import datetime
from typing import Optional, List

import requests
from flask import request
from math import ceil
from sqlalchemy import exc

from financial import db, url, api_key
from model import Symbol, FinancialData, financial_data_schema
from financial.response import Response


def save_symbol(sym: str):
    """
    will save a symbol with error handling and rollbacks
    :param sym: symbol to add to the database (str)
    :return: None
    """
    try:
        symbol = Symbol(symbol=sym)
        db.session.add(symbol)
        db.session.commit()
        log.info("record added successfully")
    except exc.IntegrityError:
        db.session.rollback()
        log.error(f"Symbol Exists `{sym}`: could not be added")
    finally:
        db.session.close()


def get_symbol(name: str) -> Optional[Symbol]:
    """
    Will return a symbol that matches `:param name`
    :param name: symbol name (str)
    :return: symbol record (Optional[Symbol])
    """
    return Symbol.query.filter_by(symbol=name).first()


def save_record(symbol: Symbol, date: str, open_price: float, close_price: float, volume: int) -> Optional[FinancialData]:
    """
    will save the record related to the period
    :param symbol: The symbol of the record. (Symbol)
    :param date: The date of the record in the format 'YYYY-MM-DD'. (str)
    :param open_price: The opening price of the record. (float)
    :param close_price: The closing price of the record. (float)
    :param volume: The volume of the record. (int)

    :return: The saved record object if successful, else None. (Optional[Record])
    """
    try:
        # check if record exists before saving
        if record_exists(symbol.id, date):
            return

        # adding new records
        symbol = symbol.id
        record = FinancialData(symbol, str_to_datetime(date), open_price, close_price, volume)
        db.session.add(record)
        db.session.commit()
        log.info("record added successfully")

    except exc.IntegrityError:
        db.session.rollback()
        log.error(f"Symbol Exists: could not be added")
    finally:
        db.session.close()


def get_financial_all() -> Optional[List[FinancialData]]:
    """
    Get all financial data from the database
    :return:
    """
    records = FinancialData.query.all()
    return records


def get_symbols_all() -> Optional[List[Symbol]]:
    """
    Get all `symbols` from the database
    :return:A list of all symbols retrieved from the database, or None if no symbols are found.
    :rtype: (Optional[List[Symbol]])
    """
    records = Symbol.query(Symbol).all()
    return records


def record_exists(symbol: int, date: str) -> FinancialData:
    """
    Check record exists with exception handling
    :param symbol:
    :param date:
    :return: Single financial record
    :rtype: FinancialData
    """
    try:
        return FinancialData.query.filter_by(symbol=symbol).filter_by(date=str_to_datetime(date)).first()
    except Exception as e:
        msg = f"Error occurred {e}"
        log.error(msg)
        raise TypeError(msg)


def str_to_datetime(date: str):
    """
    Parse date with exception handling
    :param date: datestring to parse (str)
    :return: a date object from the string `date`
    """
    try:
        return datetime.strptime(date, '%Y-%m-%d').date()
    except Exception as e:
        log.error(f"error Parsing date [{e}]")
        raise TypeError("Wrong date format passed.")


def paginator(symbol: str, start_date: str, end_date: str, limit: str, page: str) -> dict:
    """
    Fetch records from the database in a page-based approach
    :param symbol: Symbol or identifier for the records (str)
    :param start_date: Starting date for the records (str)
    :param end_date: Ending date for the records (str)
    :param limit: Maximum number of records per page (int)
    :param page: number of pages (int)
    :return: Fetched records for the given page and filters
    :rtype: dict
    """
    records = list()
    pages = 0
    count = 0

    try:
        symbol_db = get_symbol(symbol)
        limit = int(limit)
        page = int(page)

        if symbol_db is None:
            return Response.summary(records, count, page, limit, pages, error=f"symbol `{symbol}` does not exist.")
        count = FinancialData.query. \
            filter(FinancialData.symbol == symbol_db.id). \
            count()

        # there is a bug
        pages = ceil(count / limit)
        error = f"the page requested `{page}` is above threshold" if page > pages else ""

        start_date = str_to_datetime(start_date)
        end_date = str_to_datetime(end_date)
        # Calculate the offset based on the page and limit
        offset = (page - 1) * limit

        records = FinancialData.query. \
            filter(FinancialData.symbol == symbol_db.id). \
            filter(FinancialData.date >= start_date). \
            filter(FinancialData.date <= end_date). \
            limit(limit). \
            offset(offset).all()
        if len(records) == 0:
            error = "no records in that filter"

        records = financial_data_schema.dump(records)
    except ValueError as e:
        log.error(e)
        error = f"Wrong type in parameter"
    except TypeError as e:
        log.error(e)
        error = e.__str__()
    except Exception as e:
        error = "internal error occurred"
        log.error(e)
    return Response.summary(records, count, page, limit, pages, error)


def calculate(symbol: str, start_date: str, end_date: str) -> dict:
    """
    Fetch records from the database in a page-based approach
    :param symbol: Symbol or identifier for the records (str)
    :param start_date: Starting date for the records (str)
    :param end_date: Ending date for the records (str)
    :return: Fetched records for the given page and filters (dict)
    """
    error = ""
    average_daily_open_price = 0
    average_daily_close_price = 0
    average_daily_volume = 0

    try:

        start_date_parsed = str_to_datetime(start_date)
        end_date_parsed = str_to_datetime(end_date)
        symbol_db = get_symbol(symbol)

        if symbol_db is None:
            return Response.summary(start_date=start_date, end_date=end_date, symbol=symbol,
                                    error=f"symbol `{symbol}` not found", opts="sts")

        records = FinancialData.query. \
            filter(FinancialData.symbol == symbol_db.id). \
            filter(FinancialData.date >= start_date_parsed). \
            filter(FinancialData.date <= end_date_parsed). \
            all()

        total = len(records)

        if total == 0:
            return Response.summary(start_date=start_date, end_date=end_date, symbol=symbol,
                                    error="no records for that time frame", opts="sts")

        open_price_total, close_price_total, volume_total = [
            sum(getattr(record, attr) for record in records)
            for attr in ['open_price', 'close_price', 'volume']
        ]
        average_daily_open_price = round(open_price_total / total, ndigits=2)
        average_daily_close_price = round(close_price_total / total, ndigits=2)
        average_daily_volume = round(volume_total / total, ndigits=2)

    except ValueError as e:
        log.error(e)
        error = f"Wrong type in parameter"
    except TypeError as e:
        log.error(e)
        error = e.__str__()
    except Exception as e:
        error = "internal error occurred"
        log.error(e)
    return Response.summary(start_date=start_date, end_date=end_date, symbol=symbol,
                            average_daily_open_price=average_daily_open_price,
                            average_daily_close_price=average_daily_close_price,
                            average_daily_volume=average_daily_volume, error=error, opts="sts")


def param(name: str, required: bool = True) -> Optional[str]:
    val = request.args.get(name)
    param_length = len(val)
    if required and param_length == 0:
        raise TypeError("required `{}` missing.".format(name))
    return val


def save_finacial_record(date, data, symbol) -> dict:
    """
    will parse data from the response and return the formatted response
    will also add the data parsed to the database
    :param date: week start date (str)
    :param data: data for the filter (dict)
    :param symbol: target fincacial symbol (str)
    :return: data in the parsed format (dict)
    """
    open_price = data['1. open']
    close_price = data['4. close']
    volume = data['6. volume']

    res = {
        "symbol": symbol,
        "date": date,
        "open_price": float(open_price),
        "close_price": float(close_price),
        "volume": int(volume),
    }

    db_symbol = get_symbol(symbol)
    save_record(db_symbol, date, open_price, close_price, volume)
    return res


def make_request(symbol: str) -> list:
    """
    Will make a request to the provider
    :param symbol: the target symbol (str)
    :return: list of symbol data (list)
    """
    symbol = symbol.upper()
    r = requests.get(url.format(symbol, api_key))

    is_status_ok = r.status_code == 200
    if not is_status_ok:
        raise TypeError("Error making request to data provider")

    data = r.json()

    response_is_error = "Error Message" in data
    if response_is_error:
        raise TypeError(data["Error Message"])
    return data


def get_raw_data(symbol):
    """
    Will parse the data returned by the provider.
    :param symbol: the target symbol (str)
    :return: parsed symbol data (dict)
    """
    try:
        data = make_request(symbol)
        weekly_series = data["Time Series (Daily)"]
        dates = list(weekly_series.keys())
        save_symbol(symbol)
        two_weeks = [save_finacial_record(date, weekly_series[date], symbol) for date in dates[:14]]
        return financial_data_schema.dump(two_weeks)
    except TypeError as e:
        log.error(e)
        return Response.summary(error=e.__str__(), opts="inf")
    except Exception as e:
        log.error(e)
        return Response.summary(error="internal error occured. Please try again later.", opts="inf")
