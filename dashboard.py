import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import streamlit as st
sns.set(style='dark')


def create_grouped_sales_df(df):
    grouped_sales_df = df.groupby(by=["product_category_name","year"]).agg({
    "order_id": "nunique",
    "order_item_id": "count",
    "price": "sum"
    })
    grouped_sales_df = grouped_sales_df.rename(columns={"order_item_id": "quantity"})
    return grouped_sales_df

def create_sales_grouped_price_df(df):
    sales_grouped_price_df = df.groupby(['product_category_name', 'year'])['price'].sum()
    sales_grouped_price_df = sales_grouped_price_df.unstack()
    return sales_grouped_price_df

def create_sales_grouped_qty_df(df):
    sales_grouped_qty_df = grouped_sales_df.groupby(['product_category_name', 'year'])['quantity'].sum()
    sales_grouped_qty_df = sales_grouped_qty_df.unstack()
    return sales_grouped_qty_df

def create_df_day(df):
    df["Day"] = df["order_purchase_timestamp"].dt.dayofweek.map({
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
    })
    df["Day"] = df["order_purchase_timestamp"].dt.strftime("%d-%m-%Y %H:%M:%S")
    df["Day"] = df["Day"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y %H:%M:%S").strftime("%A"))
    df_day = df.groupby("Day").size().reset_index(name="purchase_amount")
    return df_day

def create_df_hours(df):
    df["hours"] = df["order_purchase_timestamp"].dt.hour
    df_hours = df.groupby("hours").size().reset_index(name="purchase_amount")
    return df_hours

def create_grouped_sales_loc_df(df):
    grouped_sales_loc_df = df.groupby(by=["customer_city"]).agg({
    "order_item_id": "count",
    "price": "sum"
    })
    grouped_sales_loc_df = grouped_sales_loc_df.rename(columns={"order_item_id": "total_unit_sales"})
    grouped_sales_loc_df = grouped_sales_loc_df.rename(columns={"price": "total_revenue"})
    return grouped_sales_loc_df

#judul
st.title("Brazillian E-Commerce Dashboard :sparkles:")

#load data
all_df = pd.read_csv("main_data.csv")

#memastikan kolom datetime
datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values("order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
for column in datetime_columns:
   all_df[column] = pd.to_datetime(all_df[column])

#filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

#membuat sidebar
with st.sidebar:
    # Menambahkan logo
    st.image("https://github.com/cherylaal/Submission_Proyek-Analisis-Data/raw/main/shopping.png")
    
    #membuat rentang waktu
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

#menghubungkan dengan all_df
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                 (all_df["order_purchase_timestamp"] <= str(end_date))]

#menyiapkan berbagai dataframe
df_day = create_df_day(main_df)
df_hours = create_df_hours(main_df)
grouped_sales_df = create_grouped_sales_df(main_df)
sales_grouped_price_df = create_sales_grouped_price_df(main_df)
sales_grouped_qty_df = create_sales_grouped_qty_df(main_df)
grouped_sales_loc_df = create_grouped_sales_loc_df(main_df)

#Jumlah Penjualan dalam hari
st.subheader('Jumlah Penjualan dalam hari')
fig,ax = plt.subplots(figsize=(10, 4))
ax.plot(
  df_day["Day"],
  df_day["purchase_amount"],
  marker='o',
  linewidth=2,
  color="#72BCD4"
)
ax.tick_params(axis='x',labelsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.set_ylim(bottom=8000, top=18000)
st.pyplot(fig)


#Jumlah Penjualan dalam jam
st.subheader('Jumlah Penjualan dalam jam')
#List label jam
hours_labels = list(map(str, range(24)))

fig,ax = plt.subplots(figsize=(10, 4))
ax.plot(
  df_hours["hours"],
  df_hours["purchase_amount"],
  marker='o',
  linewidth=2,
  color="#72BCD4"
)
ax.tick_params(axis='x',labelsize=10)
ax.tick_params(axis='y', labelsize=10)
ax.set_xticks(df_hours["hours"], hours_labels)
# ax.set_xlabel("Jam")
st.pyplot(fig)

#perkembangan Kategori Produk berdasarkan penghasilan (price) dan jumlah unit terjual (quantity)
st.subheader('Rata-rata Perkembangan Kategori Produk tertinggi')
for col in sales_grouped_price_df.columns:
  sales_grouped_price_df[f'{col}_YoY_Growth'] = sales_grouped_price_df[col].diff()
sales_grouped_price_df = sales_grouped_price_df.iloc[:, 4:]
category_growth_price_df = sales_grouped_price_df.mean(axis=1)
highest_growth_price_df = category_growth_price_df.sort_values(ascending=False)
top_10_highest_growth_price_categories = highest_growth_price_df.head(10).index

for col in sales_grouped_qty_df.columns:
  sales_grouped_qty_df[f'{col}_YoY_Growth'] = sales_grouped_qty_df[col].diff()
sales_grouped_qty_df = sales_grouped_qty_df.iloc[:, 4:]
category_growth_qty_df = sales_grouped_qty_df.mean(axis=1)
highest_growth_qty_df = category_growth_qty_df.sort_values(ascending=False)
top_10_highest_growth_qty_categories = highest_growth_qty_df.head(10).index

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(26, 9))
colors = ["#72BCD4", "#D3D3D3" ,"#D3D3D3", "#D3D3D3" ,"#D3D3D3", "#D3D3D3" ,"#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
data_price = {'Category': top_10_highest_growth_price_categories, 'Average Growth': highest_growth_price_df.iloc[list(range(10))]}
df_price = pd.DataFrame(data_price)
data_qty = {'Category': top_10_highest_growth_qty_categories, 'Average Growth': highest_growth_qty_df.iloc[list(range(10))]}
df_qty = pd.DataFrame(data_qty)

sns.barplot(x="Average Growth", y="Category", data=df_price, palette=colors, orient="h", ax=ax[0])
ax[0].set_title("By Income (price)", loc="center", fontsize=15)
ax[0].set_xlabel("Average Growth (Price)", labelpad=10)
ax[0].set_ylabel("")

sns.barplot(x="Average Growth", y="Category", data=df_qty, palette=colors, orient="h", ax=ax[1])
ax[1].set_title("By Units Sold (Quantity)", loc="center", fontsize=15)
ax[1].set_xlabel("Average Growth (Quantity)", labelpad=10)
ax[1].set_ylabel("")

st.pyplot(fig)

#Wilayah dengan Pemasukan Tertinggi
st.subheader('Wilayah dengan Penghasilan Tertinggi')
top_5_cities = grouped_sales_loc_df.sort_values("total_revenue", ascending=False).head(5)
city_names = top_5_cities.index.to_numpy()
total_revenue = top_5_cities["total_revenue"]
colors = ["#72BCD4", "#D3D3D3" ,"#D3D3D3", "#D3D3D3" ,"#D3D3D3"]
explode = (0.1, 0, 0, 0, 0)
fig,ax = plt.subplots(figsize=(6, 6))
ax.pie(total_revenue, explode=explode, labels=city_names,colors=colors, autopct='%1.1f%%',
        shadow=True, startangle=90)

ax.set_aspect('equal')
ax.autoscale()
st.pyplot(fig)
