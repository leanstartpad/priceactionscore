import matplotlib.pyplot as plt
import json
import pandas as pd
from pandas import json_normalize
import ta
import numpy as np
from ta.momentum import StochasticOscillator
from ta.trend import SMAIndicator
import requests

"""https://technical-analysis-library-in-python.readthedocs.io/en/latest/ (Technical Analysis Library)"""

# Get latest data on S&P500
headers = {
    'Content-Type': 'application/json'
}
requestResponse = requests.get(
    "https://api.tiingo.com/tiingo/daily/spy/prices?startDate=2015-01-01&token=cce97e6bbd22d423b37bbe232d78e9d7caeabd3e",
    headers=headers)  # change the startDate=
data = json.loads(requestResponse.text)
res = json_normalize(data)
df = pd.DataFrame(res)
print(df)

# All the technical indicators with their respective scores

# 50/200 Day SMA
df['SMA50'] = ta.trend.sma_indicator(close=df['close'], n=50, fillna=True)
df['SMA200'] = ta.trend.sma_indicator(close=df['close'], n=200, fillna=True)
df.loc[(df.SMA50 > df.SMA200), "Score1"] = 1
df.loc[(df.SMA50 == df.SMA200), "Score1"] = 0
df.loc[(df.SMA50 < df.SMA200), "Score1"] = -1

# 85-day Stochastics with 5-day smoothing
df['stochastics'] = ta.momentum.stoch(df['high'], df['low'], df['close'], 85, 5, True)
df['stochastics_lag1'] = df['stochastics'].shift(1)
df['stochastics_lag2'] = df['stochastics'].shift(2)
df['stochastics_lag3'] = df['stochastics'].shift(3)
df['stochastics_lag4'] = df['stochastics'].shift(4)
df['stochastics_lag5'] = df['stochastics'].shift(5)
df['stochastics_lag6'] = df['stochastics'].shift(6)
# if indicator crosses above then below 65 (lookback last 6 days), score = -1
df.loc[((df.stochastics_lag6 < 65) | (df.stochastics_lag5 < 65) | (df.stochastics_lag4 < 65)) & (
        df.stochastics_lag3 > 65) & (
               (df.stochastics_lag2 < 65) | (df.stochastics_lag1 < 65) | (df.stochastics < 65)), "Score2"] = -1
# if indicator dips below then rises above 11 (lookback last 10 days), score = +1
df.loc[((df.stochastics_lag6 > 11) | (df.stochastics_lag5 > 11) | (df.stochastics_lag4 > 11)) & (
        df.stochastics_lag3 < 11) & (
               (df.stochastics_lag2 > 11) | (df.stochastics_lag1 > 11) | (df.stochastics > 11)), "Score2"] = 1
# all else, score = 0
df['Score2'] = df['Score2'].fillna(0)

# NYSE Advance/Decline Ratio
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome('C:\\Users\\x\Downloads\chromedriver')
driver.get('https://www.barchart.com/stocks/quotes/$ADRN/technical-chart')
content = driver.page_source
soup = BeautifulSoup(content, 'lxml')
result = float(soup.find('span', {"class": "last-change"}).string)
if result > 1.9:
    Score = 1
else:
    Score = 0
print(Score)

# High-Low Indicator (52-week high/low)
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome('C:\\Users\\x\Downloads\chromedriver')
driver.get('https://www.barchart.com/stocks/highs-lows/summary')
content = driver.page_source
soup = BeautifulSoup(content, 'lxml')
fiftytwo_week_high = float(driver.find_element_by_xpath(
    '//*[@id="main-content-column"]/div/div[3]/div[1]/div/ng-transclude/table/tbody/tr[8]/td[2]/a[1]').text)
print(fiftytwo_week_high)
fiftytwo_week_low = float(driver.find_element_by_xpath(
    '//*[@id="main-content-column"]/div/div[3]/div[1]/div/ng-transclude/table/tbody/tr[9]/td[2]/a[1]').text)
print(fiftytwo_week_low)

highlow_high = (fiftytwo_week_high / (fiftytwo_week_high + fiftytwo_week_low))
highlow_low = (fiftytwo_week_low / (fiftytwo_week_high + fiftytwo_week_low))
if highlow_high < highlow_low:
    x = highlow_high
    print('52 week high={}'.format(x))
else:
    x = highlow_low
    print('52 week low={}'.format(x))
if x > 4.5:
    Score = -1
    print('Score={}'.format(Score))
elif x < 1.5:
    Score = 1
    print('Score={}'.format(Score))
elif 1.5 < x < 4.5:
    Score = 0
    print('Score={}'.format(Score))

# if you want to plot the 50/200-day MA graph
"""
print(df)
plt.plot(df['sp500'], label='SP500')
plt.plot(df['SMA50'], label='SMA50')
plt.plot(df['SMA200'], label='SMA200')
plt.legend(loc='best')
plt.show()
"""

# if you want to plot the stochastics graph
"""
x = df2['date']
y = df2['stochastics']
plt.plot(x,y)
plt.axhline(y=65, color='r', linestyle='-')
plt.axhline(y=11, color='b', linestyle='-')
plt.show()
"""
