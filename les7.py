
'''
predicting time series, data analysis


pandas is a data analysis package, it is the standard for data analysis for python
it puts data into columns and rows, like a sheets, and creates a data structure like that
you can do stuff like ctrl f, row manipulation, etc with pandas

matplotlib is a visualization program
pandas by itself cannot visualize, so matplotlib allows you to visualize

'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from matplotlib.backends.backend_pdf import PdfPages
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
#0 import

df = pd.read_csv("/Users/abrah/pythonless/monthly-milk-production.csv")
df.columns = ["Month", "Milk in pounds per cow"]
print(df.head())

#change from a string to datetime
df["Month"] = pd.to_datetime(df["Month"])
print(df.head())
#1 data print
df.set_index("Month", inplace = True)
print(df.head())

#2 rolling average
timeseries = df["Milk in pounds per cow"]
timeseries.rolling(12).mean().plot(label = "12 Month Rolling Mean")

#3 decomposition print
decomposition = seasonal_decompose(df["Milk in pounds per cow"], period = 12)

#4 model generation and print
#ARIMA - Auto Regressive Integrated Moving Average
amodel = ARIMA(df["Milk in pounds per cow"], order = (12,1,6))
#try 5,1,0
afit = amodel.fit()
aforecast = afit.forecast(steps=12)

#5 model generaiton and print again
#SARMIA - Seasonal Auto Regressive IntegratedMoving Average
smodel = SARIMAX(df["Milk in pounds per cow"], order = (1,1,1), seasonal_order = (1,1,1,12))
sfit = smodel.fit()
sforecast = sfit.get_forecast(steps = 12).predicted_mean



'''
here, matplotlib creates a pdf
pandas works with matplotlib
pandas plots using matplotlib, into a pdf as described

plt.close closes the data collection and plotti8ng
'''
with PdfPages("les7_plots.pdf") as pdf:
    #1
    df.plot()
    plt.title("Monthly milk production data")
    pdf.savefig()
    plt.close()

    #2
    timeseries.plot()
    plt.title("Milk production with seasonality removed")
    pdf.savefig()
    plt.close()

    #3
    decomposition.plot()
    plt.title("Milk production decomposition")
    pdf.savefig()
    plt.close()

    #4
    #ARIMA does not typically give seasonality, you must use SARIMA
    df["Milk in pounds per cow"].plot(label = "Data")
    aforecast.plot(label = "ARIMA Prediction", color = "black")
    plt.legend()
    pdf.savefig()
    plt.close()

    #5
    df["Milk in pounds per cow"].plot (label = "Data")
    sforecast.plot(label = "SARMIA Prediction", color = "red"3)
    plt.legend()
    pdf.savefig()
    plt.close()


'''
SARIMA has seasonal information, you just need to put the periods into them
SARIMA will try to emulate the seasonal period
instead of hand-finding the parameters in ARIMA, you can just use SARIMA


'''