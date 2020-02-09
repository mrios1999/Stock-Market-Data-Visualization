import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import style
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
import math
import datetime as dt


# Based on: https://www.investopedia.com/terms/v/volatility.asp
def find_standard_deviation(df_at_close):
    avg_close = 0
    for i in df_at_close:
        avg_close += i

    avg_close = avg_close / len(df_at_close)
    deviations = []  # known as the difference between the closing price and the average closing price

    for i in df_at_close:
        deviations.append(i - avg_close)

    sum_of_deviations = 0
    for i in range(len(deviations)):
        deviations[i] = deviations[i] ** 2
        sum_of_deviations += deviations[i]

    standard_deviation = math.sqrt(sum_of_deviations / len(df_at_close))

    return standard_deviation


# Based on: https://www.youtube.com/watch?v=nDcZJcxOwVI
def find_beta_value(df_close, start_date, end_date):
    spy = yf.download("SPY", start_date, end_date)
    df_percent_daily = df_close.pct_change()[1:].values
    spy_percent_daily = spy['Adj Close'].pct_change()[1:].values

    df_avg = 0
    spy_avg = 0
    for i in range(len(df_close)):
        df_avg += df_percent_daily[i-1]
        spy_avg += spy_percent_daily[i-1]

    df_avg /= len(df_percent_daily)
    spy_avg /= len(spy_percent_daily)

    df_deviation = []
    spy_deviation = []
    for i in range(len(df_close)):
        df_deviation.append(df_percent_daily[i-1] - df_avg)
        spy_deviation.append(spy_percent_daily[i-1] - spy_avg)

    product_of_deviations = []
    sum_of_product_of_deviations = 0
    for i in range(len(df_close)):
        product_of_deviations.append((df_deviation[i] / 100) * (spy_deviation[i] / 100))
        sum_of_product_of_deviations += product_of_deviations[i]

    covariance = sum_of_product_of_deviations / (len(df_close)-1)

    squared_spy_deviations = []
    sum_of_squared_spy_deviations = 0
    for i in range(len(spy_deviation)):
        squared_spy_deviations.append((spy_deviation[i] / 100)**2)
        sum_of_squared_spy_deviations += squared_spy_deviations[i]

    variance_of_spy = sum_of_squared_spy_deviations / (len(squared_spy_deviations)-1)

    return covariance / variance_of_spy


style.use('ggplot')

stock = "AAPL"

start = dt.datetime(2010, 1, 1)
end = dt.datetime(2020, 1, 1)

data = yf.download(stock, start, end)
data.to_csv(stock + ".csv")

df = pd.read_csv(stock + '.csv', parse_dates=True, index_col=0)  # data frame

df_ohlc = df['Adj Close'].resample('10D').ohlc()  # Open high, Low close
df_volume = df['Volume'].resample('10D').sum()

df_ohlc.reset_index(inplace=True)
df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)  # mdates required because dates stored in integer values

# Gives the idea how far the price may deviate
print('Standard deviation of', stock, ':', find_standard_deviation(df['Adj Close']))

print('Beta of', stock, ':', find_beta_value(df['Adj Close'], start, end))

ax1 = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=1, colspan=1, sharex=ax1)
ax1.xaxis_date()

candlestick_ohlc(ax1, df_ohlc.values, width=2, colorup='g')
ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)

ax1.title.set_text(stock + ' 10day MeanPrices for 10yrs')
plt.show()
