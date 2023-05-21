class Response:
    """
    Will contextually form responses for the entire app
    """

    @staticmethod
    def summary(
        records=None,
        count=0,
        page=0,
        limit=0,
        pages=0,
        error="",
        start_date="",
        end_date="",
        symbol="",
        average_daily_open_price=0.0,
        average_daily_close_price=0.0,
        average_daily_volume=0.0,
        opts="",
    ):
        if records is None:
            records = []

        info = {"info": {"error": error}}

        if opts == "sts":
            response = {
                **{
                    "data": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "symbol": symbol,
                        "average_daily_open_price": average_daily_open_price,
                        "average_daily_close_price": average_daily_close_price,
                        "average_daily_volume": average_daily_volume,
                    },
                },
                **info,
            }

        elif opts == "inf":
            response = info
        else:
            response = {
                **{
                    "data": records,
                    "pagination": {
                        "count": count,
                        "page": page,
                        "limit": limit,
                        "pages": pages,
                    },
                },
                **info,
            }

        return response
