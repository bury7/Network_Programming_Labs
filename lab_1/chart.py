import argparse
import sys

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
lazy from matplotlib.figure import Figure

from lab_1.rates import NbuClient, Rate, last_week

SERIES_COLORS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300")
STYLE = {
    "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": "#c3c2b7",
    "axes.labelcolor": "#52514e",
    "axes.titlecolor": "#0b0b0b",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": "#e1e0d9",
    "xtick.color": "#898781",
    "ytick.color": "#898781",
    "lines.linewidth": 2,
    "lines.markersize": 6,
}


def plot_rates(rates: dict[str, list[Rate]]) -> Figure:
    with plt.style.context(STYLE):
        figure, axes = plt.subplots(
            len(rates), sharex=True, squeeze=False, figsize=(8, 1 + 2.5 * len(rates)), layout="constrained"
        )
        for ax, color, (currency, currency_rates) in zip(axes[:, 0], SERIES_COLORS, rates.items(), strict=False):
            days = [rate.day for rate in currency_rates]
            values = [rate.value for rate in currency_rates]
            ax.plot(days, values, color=color, marker="o")
            ax.annotate(
                f"{values[-1]:.4f}",
                (days[-1], values[-1]),
                xytext=(8, 0),
                textcoords="offset points",
                va="center",
                color="#52514e",
            )
            ax.set(title=f"{currency} to UAH", ylabel="UAH")
            ax.margins(x=0.12)
        axes[-1, 0].xaxis.set_major_locator(mdates.DayLocator())
        axes[-1, 0].xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
        figure.suptitle("NBU exchange rates for the last week")
    return figure


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot NBU exchange rates for the last week.")
    parser.add_argument("currencies", nargs="*", default=["USD", "EUR"], help="currency codes, e.g. USD EUR GBP")
    args = parser.parse_args()
    if len(args.currencies) > len(SERIES_COLORS):
        parser.error(f"at most {len(SERIES_COLORS)} currencies can be plotted")
    return args


def main() -> None:
    args = parse_args()
    start, end = last_week()
    try:
        with NbuClient() as nbu:
            rates = {currency.upper(): nbu.fetch_rates(currency, start, end) for currency in args.currencies}
    except requests.RequestException as error:
        sys.exit(f"Failed to fetch exchange rates: {error}")

    if missing := [currency for currency, currency_rates in rates.items() if not currency_rates]:
        sys.exit(f"No data found for: {', '.join(missing)}")

    plot_rates(rates)
    plt.show()


if __name__ == "__main__":
    main()
