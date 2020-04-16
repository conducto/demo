import click
import conducto as co
import json
import math
import numpy


START_PRICE = 100.
START_CASH = 250
NRUNS = 1000 # Do 1K trials
DAYS_PER_YEAR = 250 # There are ~250 trading days in a year
YEARS = 20 # Do 20 years per trial


@click.command()
@click.option("--window", type=int, required=True, help="window of moving average")
@click.option("--mean", type=float, required=True, help="mean annual return of generated data")
@click.option("--volatility", type=float, required=True, help="annual standard deviation of generated data")
@click.option("--data-dir", required=True, help="directory in co.temp_data to store results")
def run(window, mean, volatility, data_dir):
    """
    Monte Carlo test of a simple trading strategy against some randomly generated market
    data. Trading strategy computes a `window` day moving average - whenever the price
    crosses it, trade in the other direction. Randomly generate market data with the
    given mean volatility and mean.
    """
    output = []
    for i in range(NRUNS):
        # Generate sample data. Convert mean & vol from annual to daily; mean scales
        # proportionally to ndays, and volatility proportionally to sqrt(ndays).
        daily_mean = mean / DAYS_PER_YEAR
        daily_vol = volatility / math.sqrt(DAYS_PER_YEAR)
        daily_returns = numpy.random.normal(daily_mean, daily_vol, DAYS_PER_YEAR * YEARS)
        prices = START_PRICE * numpy.cumprod(1+daily_returns)

        # Compute moving average
        avg = moving_average(prices, window)

        # Buy whenever price drops below moving average; sell whenever it goes above it.
        # This could be done vectorized in numpy, but we use a for loop here for
        # clarity.
        pos = 0
        cash = START_CASH
        for curr_price, curr_avg in zip(prices[window-1:], avg):
            if curr_avg < curr_price:
                desired_pos = 1
            else:
                desired_pos = -1

            # Trade at the current price to get to +1 or -1, depending on desired direction.
            qty_to_trade = desired_pos - pos
            cash -= qty_to_trade * curr_price
            pos += qty_to_trade

        # Trade back to zero at the end
        desired_pos = 0
        qty_to_trade = desired_pos - pos
        cash -= qty_to_trade * prices[-1]
        pos += qty_to_trade

        # Record result
        output.append(cash)

        if i % 250 == 0:
            print(f"Run #{i}: Result is ${round(cash, 2)}", flush=True)

    # Save result to Conducto's temp_data store
    path = "{}/mn={:.2f}_vol={:.2f}_win={:03}".format(data_dir, mean, volatility, window)
    data = json.dumps(output).encode()
    co.temp_data.puts(path, data)


def moving_average(a, n=3) :
    ret = numpy.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


if __name__ == "__main__":
    run()
