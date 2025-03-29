import pandas as pd
from nixtla import NixtlaClient
from datetime import datetime
from utilsforecast.preprocessing import fill_gaps
import os

df = pd.read_csv('data/Brent_final_raw.csv')
df = df.iloc[8:]
df['Date'] = pd.to_datetime(df['Date'])

df_brent = pd.DataFrame({
    'timestamp': df['Date'].values,
    'value': df['Brent_future_price'].values,
})

# Điền đầy dữ liệu bị thiếu
df_brent_fill = df_brent.copy()
df_brent_fill['unique_id'] = 'series_1'
df_brent_fill = fill_gaps(df_brent_fill, freq='D', id_col='unique_id', time_col='timestamp')
df_brent_fill = df_brent_fill.drop(columns=['unique_id'])
df_brent_fill['value'] = df_brent_fill['value'].interpolate(method='linear', limit_direction='both')

# Sử dụng TimeGPT để dự báo 30 ngày
nixtla_client = NixtlaClient(api_key='nixak-wFK5lJ8uzPREbB5AtGxWi7NM4bfxbulWEOHjJyO3VoG2ltBSCosFY1NnOycutjiF0kIpm7Z1ROaF2aOz')
fcst_df = nixtla_client.forecast(
    df_brent_fill, 
    h=30, 
    time_col='timestamp', 
    target_col='value',
    level=[80, 90], 
    model='timegpt-1-long-horizon'
)

# Lưu kết quả dự báo vào file CSV
# fcst_df.to_csv('F:\Brent forecast\brent\data\forecast_brent.csv', index=False)
# print("Forecast saved to forecast_brent.csv")

save_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(save_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

save_path = os.path.join(save_dir, 'forecast_brent.csv')
fcst_df.to_csv(save_path, index=False)
print(f"Forecast saved to {save_path}")