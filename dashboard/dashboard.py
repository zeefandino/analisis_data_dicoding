import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Analisis Penyewaan Sepeda",
    page_icon="🚲",
    layout="wide"
)

# Judul dashboard
st.title("🚴‍♂️ Analisis Penyewaan Sepeda")

# Fungsi untuk memuat data
@st.cache_data
def muat_data():
    try:
        data_harian = pd.read_csv("../data/day.csv")
        data_per_jam = pd.read_csv("../data/hour.csv")
        
        data_harian['dteday'] = pd.to_datetime(data_harian['dteday'])
        data_per_jam['dteday'] = pd.to_datetime(data_per_jam['dteday'])
        
        return data_harian, data_per_jam
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Memuat data
data_harian, data_per_jam = muat_data()


#  SIDEBAR FILTER
with st.sidebar:
    st.header("🔧 Filter Data")
    
    # Filter tanggal
    tanggal_min = data_harian['dteday'].min().date()
    tanggal_max = data_harian['dteday'].max().date()
    rentang_tanggal = st.date_input(
        "Rentang Tanggal",
        value=(tanggal_min, tanggal_max),
        min_value=tanggal_min,
        max_value=tanggal_max
    )
    
    # Filter musim
    musim_mapping = {1: 'Semi', 2: 'Panas', 3: 'Gugur', 4: 'Dingin'}
    musim_terpilih = st.multiselect(
        "Pilih Musim",
        options=list(musim_mapping.values()),
        default=list(musim_mapping.values())
    )

# =============================================
# 🛠 APLIKASI FILTER
# =============================================
def filter_data(df):
    # Filter tanggal
    if len(rentang_tanggal) == 2:
        start = pd.to_datetime(rentang_tanggal[0])
        end = pd.to_datetime(rentang_tanggal[1])
        df = df[(df['dteday'] >= start) & (df['dteday'] <= end)]
    
    # Filter musim
    if musim_terpilih:
        musim_numbers = [k for k, v in musim_mapping.items() if v in musim_terpilih]
        df = df[df['season'].isin(musim_numbers)]
    
    return df

data_harian_filter = filter_data(data_harian)
data_per_jam_filter = filter_data(data_per_jam)

# =============================================
# 📊 VISUALISASI UTAMA
# =============================================

# Tab untuk memilih analisis
tab1, tab2 = st.tabs(["Analisis Musim", "Analisis Per Jam"])

with tab1:
    st.header("🌦 Penyewaan per Musim")
    
    # Hitung total per musim
    data_musim = data_harian_filter.groupby('season')['cnt'].sum().reset_index()
    data_musim['Musim'] = data_musim['season'].map(musim_mapping)
    
    # Grafik batang interaktif
    fig = px.bar(
        data_musim,
        x='Musim',
        y='cnt',
        color='Musim',
        text='cnt',
        labels={'cnt': 'Total Penyewaan'},
        height=500
    )
    fig.update_traces(texttemplate='%{text:,}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    # Tampilkan data tabel
    with st.expander("🔍 Lihat Data Detail"):
        st.dataframe(data_musim[['Musim', 'cnt']].rename(columns={'cnt': 'Total Penyewaan'}))

with tab2:
    st.header("⏰ Penyewaan per Jam")
    
    # Hitung total per jam
    data_jam = data_per_jam_filter.groupby('hr')['cnt'].sum().reset_index()
    data_jam['Jam'] = data_jam['hr'].astype(str) + ':00'
    
    # Grafik garis interaktif
    fig = px.line(
        data_jam,
        x='Jam',
        y='cnt',
        markers=True,
        labels={'cnt': 'Total Penyewaan'},
        height=500
    )
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap per jam dan hari
    st.subheader("Pola per Jam dan Hari")
    heatmap_data = data_per_jam_filter.groupby(['hr', 'weekday'])['cnt'].sum().unstack()
    fig2 = px.imshow(
        heatmap_data,
        labels=dict(x="Hari", y="Jam", color="Penyewaan"),
        x=['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'],
        y=[f"{h}:00" for h in range(24)],
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig2, use_container_width=True)

# Informasi tambahan
st.sidebar.markdown("---")
st.sidebar.markdown("**ℹ️ Tentang**")
st.sidebar.markdown("Dashboard ini menampilkan pola penyewaan sepeda berdasarkan musim dan jam.")
