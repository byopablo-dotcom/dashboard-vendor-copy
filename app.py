import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(page_title="Vendor - Ringkas", page_icon="📊", layout="wide")

# ========== LOGO ==========
LOGO_URL = "https://i.ibb.co.com/jvMsmG76/logo-blii.png"

col_title, col_logo = st.columns([10, 1])
with col_title:
    st.title("📊 MONITORING PEMBAYARAN VENDOR (Ringkas)")
with col_logo:
    try:
        response = requests.get(LOGO_URL)
        logo = Image.open(BytesIO(response.content))
        st.image(logo, width=120)
    except:
        st.image("https://via.placeholder.com/120x120?text=Logo", width=120)

# ========== DATA ==========
SHEET_URL = "https://docs.google.com/spreadsheets/d/1u6GjCRIb-m42zoZtRn24O0uJhT0f_f6QL9YQfkWOjts/export?format=csv&gid=345129766"

@st.cache_data(ttl=0)
def load_data():
    df = pd.read_csv(SHEET_URL, skiprows=2)
    kolom_A_sampai_P = df.iloc[:, 0:16]
    df = df.dropna(how='all', subset=kolom_A_sampai_P.columns)
    return df

df = load_data()

# ========== AMBIL KOLOM ==========
kolom_yang_diambil = [0, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15]
df = df.iloc[:, kolom_yang_diambil]

df.columns = [
    "No IO",
    "Pelanggan",
    "Nama Project",
    "Deskripsi Pekerjaan",
    "Segment ",
    "Nilai Invoice",
    "Pembayaran di",
    "Diterima Kantor Pusat/Kanwil",
    "Total Pembayaran",
    "Sisa Terbayar",
    "Keterangan Posisi",
    "TOP Internal"
]

# ========== FUNGSI ==========
def clean_rupiah(val):
    if pd.isna(val):
        return 0
    cleaned = re.sub(r'[^0-9]', '', str(val))
    return float(cleaned) if cleaned else 0

def get_status(row):
    status_val = str(row["Sisa Terbayar"]).upper().strip()
    if status_val == "LUNAS":
        return "Lunas"
    else:
        return "Belum Terbayar"

df['Nilai_Invoice_Bersih'] = df["Nilai Invoice"].apply(clean_rupiah)
df['Keterangan'] = df.apply(get_status, axis=1)

# ========== FILTER ==========
st.sidebar.header("🎯 Filter Data")

all_customers = df["Pelanggan"].dropna().unique()
filter_customer = st.sidebar.multiselect("Nama Customer", options=all_customers, default=[])

filter_status = st.sidebar.selectbox("Status Pembayaran", options=["Semua", "Lunas", "Belum Terbayar"], index=2)

# ========== TERAPKAN FILTER ==========
df_filter = df.copy()
if filter_customer:
    df_filter = df_filter[df_filter["Pelanggan"].isin(filter_customer)]
if filter_status == "Lunas":
    df_filter = df_filter[df_filter['Keterangan'] == "Lunas"]
elif filter_status == "Belum Terbayar":
    df_filter = df_filter[df_filter['Keterangan'] == "Belum Terbayar"]

# ========== METRIK ==========
total_nilai = df_filter['Nilai_Invoice_Bersih'].sum()
total_jumlah = len(df_filter)

lunas_df = df_filter[df_filter['Keterangan'] == "Lunas"]
lunas_nilai = lunas_df['Nilai_Invoice_Bersih'].sum()
lunas_jumlah = len(lunas_df)

belum_df = df_filter[df_filter['Keterangan'] == "Belum Terbayar"]
belum_nilai = belum_df['Nilai_Invoice_Bersih'].sum()
belum_jumlah = len(belum_df)

# ========== CARD ==========
st.subheader("📊 Ringkasan")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 TOTAL", f"Rp {total_nilai:,.0f}")
    st.caption(f"{total_jumlah} invoice")

with col2:
    st.metric("✅ LUNAS", f"Rp {lunas_nilai:,.0f}")
    st.caption(f"{lunas_jumlah} invoice")

with col3:
    st.metric("⏳ BELUM", f"Rp {belum_nilai:,.0f}")
    st.caption(f"{belum_jumlah} invoice")

st.markdown("---")

# ========== TABEL ==========
st.subheader("📋 Daftar Tagihan")
kolom_tampil = [
    "No IO",
    "Pelanggan",
    "Nama Project",
    "Segment ",
    "Nilai Invoice",
    "Sisa Terbayar",
    "Keterangan"
]
st.dataframe(df_filter[kolom_tampil], use_container_width=True)

# Download CSV
csv = df_filter[kolom_tampil].to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV", csv, "data_tagihan_ringkas.csv", "text/csv")

# ========== GRAFIK PIE ==========
st.subheader("📊 Distribusi Status")
if not df_filter.empty:
    chart_data = df_filter.groupby('Keterangan')['Nilai_Invoice_Bersih'].sum().reset_index()
    fig_pie = px.pie(chart_data, values='Nilai_Invoice_Bersih', names='Keterangan',
                     title='Proporsi Tagihan berdasarkan Status',
                     color='Keterangan',
                     color_discrete_map={'Lunas':'green', 'Belum Terbayar':'red'})
    st.plotly_chart(fig_pie, use_container_width=True)

st.caption(f"🕒 Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")