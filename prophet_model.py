import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime
from utilsforecast.preprocessing import fill_gaps
import os

df = pd.read_excel('data/Brent_final_raw.xlsx')
df = df.iloc[8:]
df['Date'] = pd.to_datetime(df['Date'])

df_brent = pd.DataFrame({
    'ds': df['Date'].values,
    'y': df['Brent_future_price'].values,
})

# # Điền đầy dữ liệu bị thiếu
# df_brent_fill = df_brent.copy()
# df_brent_fill['unique_id'] = 'series_1'
# df_brent_fill = fill_gaps(df_brent_fill, freq='D', id_col='unique_id', time_col='ds')
# df_brent_fill = df_brent_fill.drop(columns=['unique_id'])
# df_brent_fill['y'] = df_brent_fill['y'].interpolate(method='linear', limit_direction='both')

best_params = {'changepoint_prior_scale': np.float64(0.035534441286285204), 'changepoint_range': np.float64(0.8684376461886962),
                  'daily_seasonality': True, 'growth': 'linear', 'interval_width': np.float64(0.39749103968589056),
                  'n_changepoints': 35, 'seasonality_mode': 'additive', 'seasonality_prior_scale': np.float64(10.208855423081015),
                  'uncertainty_samples': 1500, 'weekly_seasonality': False, 'yearly_seasonality': True}

model = Prophet(**best_params)
model.fit(df_brent)

future_45 = model.make_future_dataframe(periods=30, freq='B')
forecast_45 = model.predict(future_45)
predictions_45 = forecast_45.tail(30)
predictions_45 = predictions_45[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
predictions_45

save_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(save_dir, exist_ok=True) 

save_path = os.path.join(save_dir, 'prophet_brent.csv')
predictions_45.to_csv(save_path, index=False)
print(f"Forecast saved to {save_path}")