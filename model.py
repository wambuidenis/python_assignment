import logging as log
from datetime import datetime

import sqlalchemy
from sqlalchemy import exc

from financial import db, ma


class FinancialData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.Integer, db.ForeignKey("symbol.id"))
    open_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(
        self,
        symbol: int,
        date: datetime.date,
        open_price: float,
        close_price: float,
        volume: int,
    ):
        self.symbol = symbol
        self.date = date
        self.open_price = open_price
        self.close_price = close_price
        self.volume = volume

    def __repr__(self) -> str:
        return f"<FinancialData id={id},symbol={self.symbol}, open_price={self.open_price}, date={self.date}, \
        close_price={self.close_price},volume={self.volume}>"


class FinancialDataSchema(ma.Schema):
    class Meta:
        fields = ("symbol", "date", "open_price", "close_price", "volume")


class Symbol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, symbol: str):
        self.symbol = symbol

    def __repr__(self) -> str:
        return f"<Symbol id={self.id}, symbol={self.symbol}>"


# initialize the schemas and tables
financial_data_schema = FinancialDataSchema(many=True)
try:
    db.create_all()
except sqlalchemy.exc.ProgrammingError as e:
    log.error(f"Error:`{e}`")
