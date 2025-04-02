import pandas as pd
import numpy as np
# from mango import Tuner
# from scipy.stats import uniform, randint
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
import os

df = pd.read_excel('data/Brent_final_raw.xlsx')
df['Date'] = pd.to_datetime(df['Date'])
df = df.iloc[8:]
df = df[df['Date'].dt.weekday < 5]
df_Brent_lag = df[['Date', 'Brent_future_price']].copy()
brent_columns = df.columns.tolist()
brent_columns.remove('Date')

lags = [1, 2, 3]
for col in brent_columns:
    for lag in lags:
        df_Brent_lag[f'{col}_Lag_{lag}'] = df[col].shift(lag)

df_Brent_lag['Brent_future_price'] = df_Brent_lag['Brent_future_price'].interpolate(method='linear', limit_direction='both')
df_Brent_lag['Brent_future_price_Lag_1'] = df_Brent_lag['Brent_future_price_Lag_1'].interpolate(method='linear', limit_direction='both')
df_Brent_lag['Brent_future_price_Lag_2'] = df_Brent_lag['Brent_future_price_Lag_2'].interpolate(method='linear', limit_direction='both')
df_Brent_lag['Brent_future_price_Lag_3'] = df_Brent_lag['Brent_future_price_Lag_3'].interpolate(method='linear', limit_direction='both')

X_full = df_Brent_lag[['Brent_future_price_Lag_1', 'Brent_future_price_Lag_2', 'Brent_future_price_Lag_3']]
y_full = df_Brent_lag['Brent_future_price']

best_params = {'max_depth': 7, 'max_features': 0.926255100105888, 'min_samples_leaf': 8, 
               'min_samples_split': 2, 'n_estimators': 1158}

rf_model = RandomForestRegressor(**best_params, random_state=42)
rf_model.fit(X_full, y_full)

df_Brent_lag = df_Brent_lag.reset_index(drop=True)
last_index = df_Brent_lag.index[-1]
current_lag1 = df_Brent_lag.loc[last_index, 'Brent_future_price']
current_lag2 = df_Brent_lag.loc[last_index-1, 'Brent_future_price']
current_lag3 = df_Brent_lag.loc[last_index-2, 'Brent_future_price']
last_date = df_Brent_lag.loc[last_index, 'Date']

future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30, freq='B')

predictions = []
for forecast_date in future_dates:
    # Tạo input với 3 lag
    X_input = pd.DataFrame({
        'Brent_future_price_Lag_1': [current_lag1],
        'Brent_future_price_Lag_2': [current_lag2],
        'Brent_future_price_Lag_3': [current_lag3]
    })
    pred = rf_model.predict(X_input)[0]
    predictions.append({
        'Date': forecast_date,
        'Brent_future_price_Lag_1': current_lag1,
        'Brent_future_price_Lag_2': current_lag2,
        'Brent_future_price_Lag_3': current_lag3,
        'Predicted_Brent_future_price': pred
    })
    current_lag3 = current_lag2
    current_lag2 = current_lag1
    current_lag1 = pred

predictions_df = pd.DataFrame(predictions)
predictions_df

save_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(save_dir, exist_ok=True)

save_path = os.path.join(save_dir, 'forecast_rf.csv')
predictions_df.to_csv(save_path, index=False)
print(f"Forecast saved to {save_path}")