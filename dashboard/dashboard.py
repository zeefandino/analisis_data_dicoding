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
        data_harian = pd.read_csv("data/day.csv")
        data_per_jam = pd.read_csv("data/hour.csv")
        
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
    
    # Cek apakah data kosong
    if data_musim.empty:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih")
        fig = px.bar(labels={'x': 'Musim', 'y': 'Total Penyewaan'})
        fig.update_layout(title="Tidak ada data yang ditampilkan")
    else:
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
    
    # Tampilkan statistik ringkas dalam expander
    with st.expander("📊 Lihat Statistik Ringkas", expanded=False):
        if data_musim.empty:
            st.write("Tidak ada statistik yang tersedia")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Musim Paling Ramai", 
                    f"{data_musim.loc[data_musim['cnt'].idxmax(), 'Musim']}",
                    help="Musim dengan jumlah penyewaan tertinggi"
                )
            
            with col2:
                st.metric(
                    "Total Tertinggi", 
                    f"{data_musim['cnt'].max():,.0f}",
                    help="Jumlah penyewaan di musim paling ramai"
                )
            
            with col3:
                st.metric(
                    "Rata-rata", 
                    f"{data_musim['cnt'].mean():,.0f}",
                    help="Rata-rata penyewaan di semua musim"
                )
    
    # Tampilkan data tabel dengan urutan index asli
    with st.expander("📋 Lihat Data Detail", expanded=False):
        if data_musim.empty:
            st.write("Tidak ada data yang ditampilkan")
        else:
            # Buat dataframe untuk tampilan
            df_tampil = data_musim[['Musim', 'cnt']].rename(columns={'cnt': 'Total Penyewaan'})
            
            # Reset index untuk tampilan rapi
            df_tampil = df_tampil.reset_index(drop=True)
            df_tampil.index = df_tampil.index + 1  # Mulai dari nomor 1
            
            # Tampilkan tabel dengan styling
            st.dataframe(
                df_tampil.style
                    .background_gradient(cmap='YlGnBu', subset=['Total Penyewaan'])
                    .format("{:,.0f}", subset=['Total Penyewaan'])
                    .set_properties(**{'text-align': 'center'}),
                use_container_width=True,
                height=300
            )

with tab2:
    st.header("⏰ Penyewaan per Jam")
    
    # Hitung total per jam
    data_jam = data_per_jam_filter.groupby('hr')['cnt'].sum().reset_index()
    data_jam['Jam'] = data_jam['hr'].apply(lambda x: f"{x:02d}:00")
    
    # Cek apakah data kosong
    if data_jam.empty:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih")
        fig = px.line(labels={'x': 'Jam', 'y': 'Total Penyewaan'})
        fig.update_layout(title="Tidak ada data yang ditampilkan")
    else:
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
    
    # Tampilkan statistik ringkas dalam expander
    with st.expander("📊 Lihat Statistik Ringkas", expanded=False):
        if data_jam.empty:
            st.write("Tidak ada statistik yang tersedia")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Jam Paling Ramai", 
                    f"{data_jam.loc[data_jam['cnt'].idxmax(), 'Jam']}",
                    help="Jam dengan jumlah penyewaan tertinggi"
                )
            
            with col2:
                st.metric(
                    "Total Tertinggi", 
                    f"{data_jam['cnt'].max():,.0f}",
                    help="Jumlah penyewaan pada jam paling ramai"
                )
            
            with col3:
                st.metric(
                    "Rata-rata per Jam", 
                    f"{data_jam['cnt'].mean():,.0f}",
                    help="Rata-rata penyewaan di semua jam"
                )
    
    # Tampilkan data tabel dengan urutan jam
    with st.expander("📋 Lihat Data Detail", expanded=False):
        if data_jam.empty:
            st.write("Tidak ada data yang ditampilkan")
        else:
            # Buat dataframe untuk tampilan
            df_tampil = data_jam[['Jam', 'cnt']].rename(columns={'cnt': 'Total Penyewaan'})
            
            # Reset index untuk tampilan rapi (urut berdasarkan jam)
            df_tampil = df_tampil.sort_values('Jam').reset_index(drop=True)
            df_tampil.index = df_tampil.index + 1  # Mulai dari nomor 1
            
            # Tampilkan tabel dengan styling
            st.dataframe(
                df_tampil.style
                    .background_gradient(cmap='YlGnBu', subset=['Total Penyewaan'])
                    .format("{:,.0f}", subset=['Total Penyewaan'])
                    .set_properties(**{'text-align': 'center'}),
                use_container_width=True,
                height=300
            )
        
# Informasi tambahan
st.sidebar.markdown("---")
st.sidebar.markdown("**ℹ️ Tentang**")
st.sidebar.markdown("Dashboard ini menampilkan pola penyewaan sepeda berdasarkan musim dan jam.")
