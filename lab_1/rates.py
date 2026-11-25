import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Self
from zoneinfo import ZoneInfo
lazy from types import TracebackType

import requests

KYIV_TZ = ZoneInfo("Europe/Kyiv")
REQUEST_TIMEOUT = 10


@dataclass(frozen=True, slots=True)
class Rate:
    day: date
    value: float


class NbuClient:
    API_URL = "https://bank.gov.ua/NBU_Exchange/exchange_site"

    def __init__(self, timeout: float = REQUEST_TIMEOUT) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self.session.close()

    def fetch_rates(self, currency: str, start: date, end: date) -> list[Rate]:
        params = {
            "start": f"{start:%Y%m%d}",
            "end": f"{end:%Y%m%d}",
            "valcode": currency,
            "sort": "exchangedate",
            "order": "asc",
            "json": "",
        }
        response = self.session.get(self.API_URL, params=params, timeout=self.timeout)
        response.raise_for_status()
        return [Rate(date.strptime(item["exchangedate"], "%d.%m.%Y"), item["rate"]) for item in response.json()]


def last_week() -> tuple[date, date]:
    today = datetime.now(KYIV_TZ).date()
    return today - timedelta(days=6), today


def print_rates(currency: str, rates: list[Rate]) -> None:
    print(f"\n{currency} to UAH")
    print("-" * 20)
    if not rates:
        print("No data found.")
    for rate in rates:
        print(f"{rate.day:%d.%m.%Y}  {rate.value:>8.4f}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show NBU exchange rates for the last week.")
    parser.add_argument("currencies", nargs="*", default=["USD", "EUR"], help="currency codes, e.g. USD EUR GBP")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start, end = last_week()
    print(f"NBU exchange rates from {start:%d.%m.%Y} to {end:%d.%m.%Y}")
    try:
        with NbuClient() as nbu:
            for currency in args.currencies:
                print_rates(currency.upper(), nbu.fetch_rates(currency, start, end))
    except requests.RequestException as error:
        sys.exit(f"Failed to fetch exchange rates: {error}")


if __name__ == "__main__":
    main()
