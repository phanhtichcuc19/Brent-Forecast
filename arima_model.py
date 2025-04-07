import pandas as pd
import numpy as np
from pmdarima.arima import ARIMA
# !pip install statsforecast pmdarima
import os

df = pd.read_excel('data/Brent_final_raw.xlsx', index_col='Date')
# df = df[['Date', 'Brent_future_price']]
# df['Date'] = pd.to_datetime(df['Date'])
# df = df.iloc[8:]
# df = df[df['Date'].dt.weekday < 5]
# df = df.reset_index(drop=True)

df = df[df.index >= '2005-01-01']
df = df.asfreq('B')

arima_model = ARIMA(order=(3,1,2))
arima_model.fit(df['Brent_future_price'])

forecast_values = arima_model.predict(n_periods=30)

last_3_values = df['Brent_future_price'].tail(3)
combined_series = pd.concat([last_3_values, forecast_values])

# Lấy lag 1, lag 2, lag 3
lag_1 = combined_series.shift(1)  # Lag 1
lag_2 = combined_series.shift(2)  # Lag 2
lag_3 = combined_series.shift(3)  # Lag 3

# Tạo DataFrame mới chứa các lag
df_lags = pd.DataFrame({
    'Date': combined_series.index,
    'Brent_future_price_Lag_1': lag_1,
    'Brent_future_price_Lag_2': lag_2,
    'Brent_future_price_Lag_3': lag_3,
    'ARIMA': combined_series
})

df_lags = df_lags.dropna()
df_lags = df_lags.reset_index(drop=True)

save_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(save_dir, exist_ok=True) 

save_path = os.path.join(save_dir, 'forecast_arima.csv')
df_lags.to_csv(save_path, index=False)
print(f"Forecast saved to {save_path}")