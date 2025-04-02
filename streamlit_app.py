# Import libraries
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import os

# Page title
st.set_page_config(page_title='Interactive Data Explorer', page_icon='⛽')
st.title('📊 Phân tích và dự đoán giá dầu')

with st.expander('Về ứng dụng này'):
    st.markdown('**Ứng dụng này có thể làm gì?**')
    st.info(
        'Ứng dụng này dự báo giá dầu Brent tương lai bằng cách sử dụng dữ liệu lịch sử và các biến liên quan như giá dầu WTI, giá vàng, chỉ số GPR, sức mạnh USD, và VIX.'
    )
    st.markdown('**Cách sử dụng ứng dụng?**')
    st.warning(
    'Để tương tác với ứng dụng: \n'
    '1. Chọn các biến bạn quan tâm trong hộp lựa chọn thả xuống, sau đó \n'
    '2. Chọn khoảng thời gian từ thanh trượt. \n'
    'Kết quả sẽ hiển thị biểu đồ và bảng dữ liệu tương ứng.'
)

st.subheader('Phân tích biến động thị trường theo từng năm')

# Load data - Read CSV into a Pandas DataFrame
df = pd.read_excel('data/Brent_final_raw.xlsx')
df = df.iloc[8:]
df['Date'] = pd.to_datetime(df['Date']).dt.date

GPR = pd.read_excel("data/data_gpr_daily_recent.xlsx",
                       header = 0)
GPR = GPR.drop(GPR.columns[0], axis=1).drop(GPR.columns[-2:], axis=1)
GPR = GPR[['date', 'GPRD', 'event']]
GPR = GPR[(GPR['date'] >= pd.to_datetime("2005-01-01"))]
GPR['date'] = pd.to_datetime(GPR['date']).dt.date

# Chọn các cột cần thiết
selected_columns = [
    "Date", "Brent_future_price", "WTI_future_price", "Basket_price",
    "Gold_future_price", "nature_gas_price", "heating_oil_price",
    "balti_dry_index_price", "US_index_price", "vix_price", "GPRD"
]
df = df[selected_columns]
df = pd.merge(df, GPR[['date', 'event']], left_on="Date", right_on="date", how="left")
df.drop("date", axis=1, inplace=True)

min_date = df['Date'].min()
max_date = df['Date'].max()

# Hiển thị slider với chỉ ngày tháng năm
date_range = st.slider("Chọn khoảng thời gian", 
                       min_value=min_date, 
                       max_value=max_date, 
                       value=(pd.to_datetime("2014-01-01").date(), max_date))

start_date, end_date = date_range
st.markdown(
    f"Khoảng thời gian đã chọn: <span style='color:green'>{start_date} đến {end_date}</span>",
    unsafe_allow_html=True
)
start_date, end_date = date_range[0], date_range[1]
df_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

st.write("### Dữ liệu được chọn", df_filtered)

df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
# df_filtered = df_filtered[df_filtered['Date'].dt.weekday < 5]

oil_chart_data = df_filtered[["Date", "Brent_future_price", "WTI_future_price", "Basket_price"]].dropna()
oil_chart_data = oil_chart_data.melt('Date', var_name='Oil_Type', value_name='Price')

custom_color_scale = alt.Scale(
    domain=["Brent_future_price", "WTI_future_price", "Basket_price"],
    range=["#0b6ecb", "#85caff", "#0087ff"]  
)

selection = alt.selection_single(fields=['Oil_Type'], bind='legend')

oil_chart = alt.Chart(oil_chart_data).mark_line().encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('Price:Q', title='Giá dầu'),
    color=alt.condition(
        selection, 
        alt.Color('Oil_Type:N', scale=custom_color_scale,
                  legend=alt.Legend(orient='bottom')),
        alt.value('lightgray')
    ),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_selection(
    selection
).properties(
    # title='Biểu đồ Giá dầu',
    height=400
)
st.write("### Biểu đồ Giá dầu")
st.altair_chart(oil_chart, use_container_width=True)


# chart_data_fuel = df_filtered[["Date", "nature_gas_price", "heating_oil_price"]].set_index("Date")
# st.write("### Biểu đồ Giá khí tự nhiên & Dầu hỏa")
# st.line_chart(chart_data_fuel)

chart_data_fuel = df_filtered[["Date", "nature_gas_price", "heating_oil_price"]].dropna()
chart_data_fuel = chart_data_fuel.melt('Date', var_name='Fuel_Type', value_name='Price')

custom_color_scale = alt.Scale(
    domain=["nature_gas_price", "heating_oil_price"],
    range=["#4f970b", "#91be26"]  
)

selection = alt.selection_single(fields=['Fuel_Type'], bind='legend')

fuel_chart = alt.Chart(chart_data_fuel).mark_line().encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('Price:Q', title='Giá nhiên liệu'),
    color=alt.condition(
        selection, 
        alt.Color('Fuel_Type:N', scale=custom_color_scale,
                  legend=alt.Legend(orient='bottom')),
        alt.value('lightgray')
    ),
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
).add_selection(
    selection
).properties(
    # title='Biểu đồ Giá dầu',
    height=400
)
st.write("### Biểu đồ Giá khí tự nhiên & Dầu hỏa")
st.altair_chart(fuel_chart, use_container_width=True)



chart_data_gold = df_filtered[["Date", "Gold_future_price"]].dropna()

gold_chart = alt.Chart(chart_data_gold).mark_line(color="#FFB22C", size=2).encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('Gold_future_price:Q', title='Giá vàng')
).properties(
    # title='Biểu đồ Giá vàng',
    height=400
)
st.write("### Biểu đồ Giá vàng")
st.altair_chart(gold_chart, use_container_width=True)


chart_data_gpr = df_filtered[["Date", "GPRD", 'event']]

gpr_chart = alt.Chart(chart_data_gpr).mark_line(color="#E52020", size=2).encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('GPRD:Q', title='Địa chính trị')
).properties(
    # title='Biểu đồ Giá vàng',
    height=400
)
# Lấy dữ liệu chỉ có event không rỗng để hiển thị chú thích
event_data = chart_data_gpr[(chart_data_gpr["event"].notnull()) & (chart_data_gpr["event"] != "")]
event_text = alt.Chart(event_data).mark_text(align='left', dx=5, dy=-5, color='black').encode(
    x=alt.X('Date:T'),
    y=alt.Y('GPRD:Q'),
    text=alt.Text('event:N')
)

# Kết hợp biểu đồ đường và các chú thích
combined_gpr_chart = gpr_chart + event_text

st.write("### Biểu đồ Địa Chính Trị")
st.altair_chart(combined_gpr_chart, use_container_width=True)



# st.write("## Forecast giá dầu Brent Future bằng Time GPT")

read_path = os.path.join(os.path.dirname(__file__), 'data', 'forecast_brent.csv')
if not os.path.exists(read_path):
    st.error(f"File không tồn tại: {read_path}")
else:
    fcst_df = pd.read_csv(read_path)
    fcst_df['timestamp'] = pd.to_datetime(fcst_df['timestamp'])
    fcst_df = fcst_df[fcst_df['timestamp'].dt.weekday < 5]
    # st.dataframe(fcst_df)

df_hist_2025 = df[df['Date'] >= pd.to_datetime("2023-01-01").date()]
df_hist_2025['Date'] = pd.to_datetime(df_hist_2025['Date'])
df_hist_2025 = df_hist_2025[["Date", "Brent_future_price"]].dropna()
# df_hist_2025 = df_hist_2025[df_hist_2025['Date'].dt.weekday < 5].dropna()

# Biểu đồ lịch sử: Sử dụng cột "Brent_future_price" với màu steelblue, đường liền
hist_chart = alt.Chart(df_hist_2025).mark_line(color="steelblue", size=2).encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('Brent_future_price:Q', title='Giá dầu Brent Future'),
    tooltip=['Date:T', 'Brent_future_price:Q']
).properties(
    height=400
)

# Biểu đồ dự báo: Sử dụng cột "TimeGPT" với màu đỏ, đường gạch
fcst_df.rename(columns={'timestamp': 'Date'}, inplace=True)

forecast_chart = alt.Chart(fcst_df).mark_line(color="red", size=2).encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('TimeGPT:Q', title='Giá dầu Brent Future'),
    tooltip=['Date:T', 'TimeGPT:Q']
).properties(
    height=400
)

# Kết hợp hai biểu đồ lại với nhau
combined_chart = hist_chart + forecast_chart
combined_chart = combined_chart.properties(
    # title="Biểu đồ Giá dầu Brent Future (Lịch sử và Dự báo)"
).interactive()

# st.write("### Forecast giá dầu Brent Future")
# st.altair_chart(combined_chart, use_container_width=True)

# st.write("## Forecast giá dầu Brent Future bằng Prophet")

read_path = os.path.join(os.path.dirname(__file__), 'data', 'prophet_brent.csv')
if not os.path.exists(read_path):
    st.error(f"File không tồn tại: {read_path}")
else:
    prophet_df = pd.read_csv(read_path)
    prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
    prophet_df = prophet_df[prophet_df['ds'].dt.weekday < 5]
    # st.dataframe(prophet_df)

prophet_df.rename(columns={'ds': 'Date', 'yhat': 'Prophet'}, inplace=True)
forecast_prophet_chart = alt.Chart(prophet_df).mark_line(color="red", size=2).encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('Prophet:Q', title='Giá dầu Brent Future'),
    tooltip=['Date:T', 'Prophet:Q']
).properties(
    height=400
)

# Kết hợp hai biểu đồ lại với nhau
combined_chart1 = hist_chart + forecast_prophet_chart
combined_chart1 = combined_chart1.properties(
    # title="Biểu đồ Giá dầu Brent Future (Lịch sử và Dự báo)"
).interactive()

#XG boost
read_path = os.path.join(os.path.dirname(__file__), 'data', 'forecast_xg.csv')
if not os.path.exists(read_path):
    st.error(f"File không tồn tại: {read_path}")
else:
    xg_df = pd.read_csv(read_path)
    xg_df['Date'] = pd.to_datetime(xg_df['Date'])
    xg_df = xg_df[xg_df['Date'].dt.weekday < 5]

xg_df.rename(columns={'Predicted_Brent_future_price': 'XG Boost'}, inplace=True)
forecast_xg_chart = alt.Chart(xg_df).mark_line(color="red", size=2).encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('XG Boost:Q', title='Giá dầu Brent Future'),
    tooltip=['Date:T', 'XG Boost:Q']
).properties(
    height=400
)

# Kết hợp hai biểu đồ lại với nhau
combined_chart2 = hist_chart + forecast_xg_chart
combined_chart2 = combined_chart.properties(
    # title="Biểu đồ Giá dầu Brent Future (Lịch sử và Dự báo)"
).interactive()


#Light GBM
read_path = os.path.join(os.path.dirname(__file__), 'data', 'forecast_lightgbm.csv')
if not os.path.exists(read_path):
    st.error(f"File không tồn tại: {read_path}")
else:
    lightgbm_df = pd.read_csv(read_path)
    lightgbm_df['Date'] = pd.to_datetime(lightgbm_df['Date'])
    lightgbm_df = lightgbm_df[lightgbm_df['Date'].dt.weekday < 5]

lightgbm_df.rename(columns={'Predicted_Brent_future_price': 'Light GBM'}, inplace=True)
forecast_lightgbm_chart = alt.Chart(lightgbm_df).mark_line(color="red", size=2).encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('Light GBM:Q', title='Giá dầu Brent Future'),
    tooltip=['Date:T', 'Light GBM:Q']
).properties(
    height=400
)

# Kết hợp hai biểu đồ lại với nhau
combined_chart3 = hist_chart + forecast_lightgbm_chart
combined_chart3 = combined_chart.properties(
    # title="Biểu đồ Giá dầu Brent Future (Lịch sử và Dự báo)"
).interactive()


#Random Forest
read_path = os.path.join(os.path.dirname(__file__), 'data', 'forecast_rfcsv')
if not os.path.exists(read_path):
    st.error(f"File không tồn tại: {read_path}")
else:
    rf_df = pd.read_csv(read_path)
    rf_df['Date'] = pd.to_datetime(rf_df['Date'])
    rf_df = rf_df[rf_df['Date'].dt.weekday < 5]

rf_df.rename(columns={'Predicted_Brent_future_price': 'Random Forest'}, inplace=True)
forecast_rf_chart = alt.Chart(rf_df).mark_line(color="red", size=2).encode(
    x=alt.X('Date:T', title='Ngày'),
    y=alt.Y('Random Forest:Q', title='Giá dầu Brent Future'),
    tooltip=['Date:T', 'Random Forest:Q']
).properties(
    height=400
)

# Kết hợp hai biểu đồ lại với nhau
combined_chart4 = hist_chart + forecast_rf_chart
combined_chart4 = combined_chart.properties(
    # title="Biểu đồ Giá dầu Brent Future (Lịch sử và Dự báo)"
).interactive()



st.markdown("<h1 style='text-align: center; color: black;'>🫦 Forecast giá dầu Brent Future</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: left; color: black;'>💃 Chọn mô hình dự báo</h2>", unsafe_allow_html=True)
# st.write("##💃 Chọn mô hình dự báo")
model_choice = st.selectbox("", ["Time GPT", "Prophet", "XG Boost", "Light GBM"])

if model_choice == "Time GPT":
    st.dataframe(fcst_df)
    st.write("### Forecast giá dầu Brent Future bằng Time GPT")
    st.altair_chart(combined_chart, use_container_width=True)
elif model_choice == "Prophet":
    st.dataframe(prophet_df)
    st.write("### Forecast giá dầu Brent Future bằng Prophet")
    st.altair_chart(combined_chart1, use_container_width=True)
elif model_choice == "XG Boost":
    st.dataframe(xg_df)
    st.write("### Forecast giá dầu Brent Future bằng XG Boost")
    st.altair_chart(combined_chart2, use_container_width=True)
elif model_choice == "Light GBM":
    st.dataframe(lightgbm_df)
    st.write("### Forecast giá dầu Brent Future bằng Light GBM")
    st.altair_chart(combined_chart3, use_container_width=True)
elif model_choice == "Random Forest":
    st.dataframe(rf_df)
    st.write("### Forecast giá dầu Brent Future bằng Random Forest")
    st.altair_chart(combined_chart4, use_container_width=True)