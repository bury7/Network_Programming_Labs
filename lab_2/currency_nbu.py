from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from flask import Flask, abort, request
lazy from flask.typing import ResponseReturnValue

from lab_2.currency_static import render_rate

API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"
KYIV_TZ = ZoneInfo("Europe/Kyiv")
REQUEST_TIMEOUT = 10
DAY_OFFSETS = {"today": 0, "yesterday": 1}

app = Flask(__name__)


def fetch_rate(currency: str, day: date) -> float | None:
    params = {"valcode": currency, "date": f"{day:%Y%m%d}", "json": ""}
    response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    rates = response.json()
    return rates[0]["rate"] if rates else None


@app.get("/currency")
def currency() -> ResponseReturnValue:
    days = [day for day in DAY_OFFSETS if request.args.get(day) is not None]
    if len(days) != 1:
        abort(400, "Pass exactly one parameter: today or yesterday")

    day = datetime.now(KYIV_TZ).date() - timedelta(days=DAY_OFFSETS[days[0]])
    try:
        rate = fetch_rate("USD", day)
    except requests.RequestException, LookupError, TypeError:
        abort(502, "NBU API is unavailable")

    if rate is None:
        abort(404, f"No USD rate for {day:%d.%m.%Y}")
    return render_rate("USD", rate)


if __name__ == "__main__":
    app.run(port=8000)
