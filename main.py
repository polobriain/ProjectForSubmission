
## This code imports oil price data from the online website Quandl
## Are there near term patterns in the data

## import libraries
import pandas as pd
import requests
import io
import numpy as np


## take date from Quandl using an API
r = requests.get('https://www.quandl.com/api/v3/datasets/FRED/DCOILBRENTEU.csv?api_key=uvNKbWpn_an_BhgACSyE')

## import the CSV data into a pandas dataframe
urldata = r.content
rawdata = pd.read_csv(io.StringIO(urldata.decode('utf-8')))

## examine the shape of the dataframe
print("Data Frame Shape:")
print(rawdata.shape)

## use Date as the index
rawdata = rawdata.set_index(['Date'])

## sort as date ascending, overwrite existing data
rawdata.sort_index(inplace = True, ascending = True)

## check for duplicates in the date column (in the index)
## print the duplicates
duplicate = rawdata[rawdata.index.duplicated()]
print("These are the duplicate dates :" )
print(duplicate)

## drop the duplicates
rawdata.index.drop_duplicates()

## Add the month and day to the data
rawdata['Day'] = pd.DatetimeIndex(rawdata.index).day
rawdata['Month'] = pd.DatetimeIndex(rawdata.index).month

## Add in the rolling moving averages

rawdata['3-Day Moving Ave'] = rawdata.iloc[:,0].rolling(window=3).mean()
rawdata['10-Day Moving Ave'] = rawdata.iloc[:,0].rolling(window=10).mean()
rawdata['20-Day Moving Ave'] = rawdata.iloc[:,0].rolling(window=20).mean()

## Backfill in NaN where there is no data
rawdata = rawdata.fillna(method='bfill')

## Add in a Sentiment column that compares vlues with the available moving averages
rawdata['Sentiment'] = np.where((rawdata['Value'] >= rawdata['3-Day Moving Ave']) & (rawdata['Value']>=rawdata['10-Day Moving Ave']) & (rawdata['Value']>=rawdata['20-Day Moving Ave']), "Bullish", "Bearish")

## print out the data so you can look at it
with pd.option_context('display.max_rows', 10, 'display.max_columns', None, 'display.precision', 2):
    print("This is all the data:")
    print(rawdata)

## Print out the number of bullish and bearish days
print("Number of bullish and bearish days")
print(rawdata["Sentiment"].value_counts())


## Make a subset of the data for the period 2015+
data_2015 = rawdata.loc["2015-01-01":]
print("Shape of data after for the period 2015+")
print(data_2015.shape)

## Import matplotlib and seaborn
import matplotlib.pyplot as plt


## Plot the 2015+ data

fig, ax = plt.subplots()
ax.plot(data_2015.index, data_2015['Value'], color = 'red')

ax.set_title("Plot of oil price vs time from year 2015", color = 'purple')

ax.set_xlabel('Date')
ax.set_ylabel('Oil price (USD$)')

ax.tick_params('x', colors = 'green')
ax.tick_params('y', colors = 'blue')

# find lowest data point in the period and highlight
min_value_date = data_2015['Value'].idxmin()
min_value = data_2015['Value'].min()

ax.annotate("Lowest oil price in period of " + str(min_value) + " on " + str(min_value_date), xy = (min_value_date,min_value), xytext=(-5, 15), arrowprops={'arrowstyle':"->", 'color':"grey"})

## reduce number of x_ticks to 5
ax.xaxis.set_major_locator(plt.MaxNLocator(5))

plt.show()


## set up to use seaborn
import seaborn as sns

sns.set(style="darkgrid") #change style
sns.cubehelix_palette(as_cmap=True)

## Create a list called order which can be used subsequently
order = [1,2,3,4,5,6,7,8,9,10,11,12]

chart = sns.relplot(x = 'Day', y = 'Value', data = data_2015, kind = 'line',ci = 'sd', style = 'Month', col = 'Month', col_wrap=3, col_order = order, height=2)

chart.fig.suptitle("Oil price in each month of the year (year 2015+)", y =0.95)
plt.show()

## Print out stats on the value

print("Statistics on oil price by month")
print(data_2015.groupby('Month')['Value'].agg([min, max, np.mean, np.median]))

##Merge dataframe with itself
##Take current date and put the subsequent date on the same row

merged_data_2015 = data_2015.merge(data_2015, on = data_2015.index, how = 'left')
print(merged_data_2015.head())

print("Shape of merged dataframe:")
print(merged_data_2015.shape)

## Loop through merged dataframe to pick out values over 85 USD
## Create a small function to do this

def my_function(high_price):
    newcount = 0
    for i in range(0, merged_data_2015.shape[0]-2):
        if merged_data_2015.iloc[i, 1]>= high_price:
            newcount += 1

    print("The oil price was above 85 "+str(newcount)+ " times in this period.")

##Call my function
my_function(85)