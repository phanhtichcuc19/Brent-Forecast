import pandas as pd
from prophet import Prophet
from datetime import datetime
from utilsforecast.preprocessing import fill_gaps
import os

df = pd.read_csv('data/Brent_final_raw.csv')
df = df.iloc[8:]
df['Date'] = pd.to_datetime(df['Date'])

df_brent = pd.DataFrame({
    'ds': df['Date'].values,
    'y': df['Brent_future_price'].values,
})

# Điền đầy dữ liệu bị thiếu
df_brent_fill = df_brent.copy()
df_brent_fill['unique_id'] = 'series_1'
df_brent_fill = fill_gaps(df_brent_fill, freq='D', id_col='unique_id', time_col='ds')
df_brent_fill = df_brent_fill.drop(columns=['unique_id'])
df_brent_fill['y'] = df_brent_fill['y'].interpolate(method='linear', limit_direction='both')

best_params = {'changepoint_prior_scale': 0.05261618703899386, 'changepoint_range': 0.9435355958343157, 'daily_seasonality': True,
                  'growth': 'linear', 'interval_width': 0.702236869891917, 'n_changepoints': 20, 'seasonality_mode': 'multiplicative',
                  'seasonality_prior_scale': 8.660431205115959, 'uncertainty_samples': 2000, 'weekly_seasonality': False,
                  'yearly_seasonality': False}

model_full = Prophet(**best_params)
model_full.fit(df_brent_fill)

future_45 = model_full.make_future_dataframe(periods=30, freq='D')
forecast_45 = model_full.predict(future_45)
predictions_45 = forecast_45.tail(30)
predictions_45 = predictions_45[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
predictions_45

save_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(save_dir, exist_ok=True) 

save_path = os.path.join(save_dir, 'prophet_brent.csv')
predictions_45.to_csv(save_path, index=False)
print(f"Forecast saved to {save_path}")