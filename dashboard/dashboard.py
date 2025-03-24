import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')
from matplotlib.ticker import FuncFormatter  # Impor FuncFormatter


# Judul Dashboard
st.title("Bike Sharing Dataset Analysis Dashboard  :sparkles:")

# Load Data dengan st.cache_data
@st.cache_data  # Ganti st.cache dengan st.cache_data
def load_data():
    day_df = pd.read_csv("../data/day.csv")
    hour_df = pd.read_csv("../data/hour.csv")
    return day_df, hour_df

day_df, hour_df = load_data()

# Konversi kolom `dteday` ke datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Sidebar untuk memilih analisis
st.sidebar.title("Pilih Analisis")
analysis_option = st.sidebar.selectbox(
    "Pilih Jenis Analisis",
    ["Analisis Musim", "Analisis Jam"]
)

# Analisis Musim
if analysis_option == "Analisis Musim":
    st.header("Analisis Penyewaan Sepeda Berdasarkan Musim")
    
    # Hitung total penyewaan per musim
    daySeason_df = day_df.groupby('season')['cnt'].nunique().reset_index()
    daySeason_df.rename(columns={'cnt': 'Jumlah_Rental_Sepeda'}, inplace=True)
    
    # Mapping musim ke nama
    season_names = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    daySeason_df['Season'] = daySeason_df['season'].map(season_names)
    
    # Buat figure dan axes
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Tentukan warna untuk setiap bar
    # Bar dengan jumlah rental terbanyak akan berwarna biru, lainnya abu-abu
    colors = ["#72BCD4" if x == daySeason_df["Jumlah_Rental_Sepeda"].max() else "#D3D3D3" for x in daySeason_df["Jumlah_Rental_Sepeda"]]
    
    # Buat barplot
    sns.barplot(
        x="Season",  # Sumbu x: season
        y="Jumlah_Rental_Sepeda",  # Sumbu y: jumlah rental sepeda
        data=daySeason_df,  # Data yang digunakan
        palette=colors,  # Warna bar
        ax=ax
    )
    
    # Atur label dan judul
    ax.set_ylabel("Jumlah Rental Sepeda", fontsize=12)
    ax.set_xlabel("Musim", fontsize=12)
    ax.set_title("Jumlah Penyewaan Sepeda pada Tiap Musim", loc="center", fontsize=16)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    
    # Nonaktifkan notasi ilmiah pada sumbu y
    ax.ticklabel_format(style='plain', axis='y')
    
    # Format label sumbu y dengan pemisah ribuan
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    
    # Tampilkan plot di Streamlit
    st.pyplot(fig)

# Analisis Jam
elif analysis_option == "Analisis Jam":
    st.header("Analisis Penyewaan Sepeda Berdasarkan Jam")
    
    # Hitung total penyewaan per jam
    hourSeason_df = hour_df.groupby('hr')['cnt'].nunique().reset_index()
    hourSeason_df.rename(columns={'cnt': 'Jumlah_Rental_Sepeda'}, inplace=True)
    
    # Buat figure dan axes
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Tentukan warna untuk setiap bar
    # Bar dengan jumlah rental terbanyak akan berwarna biru, lainnya abu-abu
    colors = ["#72BCD4" if x == hourSeason_df["Jumlah_Rental_Sepeda"].max() else "#D3D3D3" for x in hourSeason_df["Jumlah_Rental_Sepeda"]]
    
    # Buat barplot
    sns.barplot(
        x="hr",  # Sumbu x: hour
        y="Jumlah_Rental_Sepeda",  # Sumbu y: jumlah rental sepeda
        data=hourSeason_df,  # Data yang digunakan
        palette=colors,  # Warna bar
        ax=ax
    )
    
    # Atur label dan judul
    ax.set_ylabel("Jumlah Rental Sepeda", fontsize=12)
    ax.set_xlabel("Jam", fontsize=12)
    ax.set_title("Jumlah Penyewaan Sepeda pada Tiap Jam", loc="center", fontsize=16)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    
    # Nonaktifkan notasi ilmiah pada sumbu y
    ax.ticklabel_format(style='plain', axis='y')
    
    # Format label sumbu y dengan pemisah ribuan
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    
    # Tampilkan plot di Streamlit
    st.pyplot(fig)

# Informasi Tambahan
st.sidebar.markdown("### Tentang Dashboard")
st.sidebar.markdown("Dashboard ini menampilkan analisis penyewaan sepeda terbanyak berdasarkan musim dan jam.")