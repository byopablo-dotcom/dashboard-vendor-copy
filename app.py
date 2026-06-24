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
    st.title("📊 MONITORING PEMBAYARAN VENDOR")
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
    kolom_A_sampai_Q = df.iloc[:, 0:17]
    df = df.dropna(how='all', subset=kolom_A_sampai_Q.columns)
    return df

df = load_data()

# ========== AMBIL KOLOM ==========
kolom_yang_diambil = [0, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16]
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
    "TOP Internal",
    "Status_Q"
]

# ========== FUNGSI ==========
def clean_rupiah(val):
    if pd.isna(val):
        return 0
    cleaned = re.sub(r'[^0-9]', '', str(val))
    return float(cleaned) if cleaned else 0

def get_status(row):
    try:
        q_val = float(row["Status_Q"])
        if q_val == 0:
            return "Lunas"
        else:
            return "Belum Terbayar"
    except:
        status_str = str(row["Status_Q"]).upper().strip()
        if status_str == "LUNAS":
            return "Lunas"
        else:
            return "Belum Terbayar"

df['Nilai_Invoice_Bersih'] = df["Nilai Invoice"].apply(clean_rupiah)
df['Keterangan'] = df.apply(get_status, axis=1)
df["Tanggal_Parse"] = pd.to_datetime(df["Diterima Kantor Pusat/Kanwil"], errors='coerce')

# ========== FILTER ==========
st.sidebar.header("🎯 Filter Data")

all_customers = df["Pelanggan"].dropna().unique()
filter_customer = st.sidebar.multiselect("Nama Customer", options=all_customers, default=[])

filter_status = st.sidebar.selectbox("Status Pembayaran", options=["Semua", "Lunas", "Belum Terbayar"], index=2)

filter_pembayaran = st.sidebar.selectbox(
    "Pembayaran di",
    options=["Semua", "KANTOR PUSAT", "KANWIL"],
    index=0
)

# ========== TERAPKAN FILTER ==========
df_filter = df.copy()

if filter_customer:
    df_filter = df_filter[df_filter["Pelanggan"].isin(filter_customer)]

if filter_status == "Lunas":
    df_filter = df_filter[df_filter['Keterangan'] == "Lunas"]
elif filter_status == "Belum Terbayar":
    df_filter = df_filter[df_filter['Keterangan'] == "Belum Terbayar"]

if filter_pembayaran != "Semua":
    df_filter = df_filter[df_filter["Pembayaran di"] == filter_pembayaran]

# ========== METRIK ==========
total_nilai = df_filter['Nilai_Invoice_Bersih'].sum()
total_jumlah = len(df_filter)

lunas_df = df_filter[df_filter['Keterangan'] == "Lunas"]
lunas_nilai = lunas_df['Nilai_Invoice_Bersih'].sum()
lunas_jumlah = len(lunas_df)

belum_df = df_filter[df_filter['Keterangan'] == "Belum Terbayar"]
belum_nilai = belum_df['Nilai_Invoice_Bersih'].sum()
belum_jumlah = len(belum_df)

# ========== CSS ==========
st.markdown("""
<style>
/* ===== CARD ===== */
.card-total {
    background: linear-gradient(135deg, #0033a0 0%, #1a5bbf 50%, #4a8ce0 100%);
    padding: 20px;
    border-radius: 12px;
    color: white !important;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin: 10px 0;
}
.card-total * {
    color: white !important;
}
.card-lunas {
    background: linear-gradient(135deg, #e87a00 0%, #f5a623 50%, #f7c948 100%);
    padding: 20px;
    border-radius: 12px;
    color: white !important;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin: 10px 0;
}
.card-lunas * {
    color: white !important;
}
.card-belum {
    background: linear-gradient(135deg, #c0392b 0%, #e74c3c 50%, #f1948a 100%);
    padding: 20px;
    border-radius: 12px;
    color: white !important;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin: 10px 0;
}
.card-belum * {
    color: white !important;
}
.card-label {
    font-size: 14px;
    opacity: 0.9;
    font-weight: 500;
}
.card-value {
    font-size: 28px;
    font-weight: bold;
    margin: 8px 0;
}
.card-sub {
    font-size: 14px;
    opacity: 0.85;
}

/* ===== LIST ITEM ===== */
.list-item {
    background: #f0f2f6;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 8px;
    color: #1a1a1a !important;
    border-left: 4px solid #0033a0;
}
.list-item * {
    color: #1a1a1a !important;
}
.list-item-orange {
    background: #f0f2f6;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 8px;
    color: #1a1a1a !important;
    border-left: 4px solid #e87a00;
}
.list-item-orange * {
    color: #1a1a1a !important;
}

/* ===== TAMPILAN HP ===== */
@media (max-width: 768px) {
    .list-item {
        background: #ffffff;
        border: 1px solid #d0d0d0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #1a1a1a !important;
    }
    .list-item * {
        color: #1a1a1a !important;
    }
    .list-item-orange {
        background: #ffffff;
        border: 1px solid #d0d0d0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #1a1a1a !important;
    }
    .list-item-orange * {
        color: #1a1a1a !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ========== 3 CARD ==========
st.subheader("📊 Ringkasan")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card-total">
        <div class="card-label">💰 TOTAL</div>
        <div class="card-value">Rp {total_nilai:,.0f}</div>
        <div class="card-sub">📄 {total_jumlah:,} invoice</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card-lunas">
        <div class="card-label">✅ LUNAS</div>
        <div class="card-value">Rp {lunas_nilai:,.0f}</div>
        <div class="card-sub">📄 {lunas_jumlah:,} invoice</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card-belum">
        <div class="card-label">⏳ BELUM</div>
        <div class="card-value">Rp {belum_nilai:,.0f}</div>
        <div class="card-sub">📄 {belum_jumlah:,} invoice</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========== LIST ==========
st.subheader("📋 Daftar Tagihan")

col_kiri, col_kanan = st.columns(2)

# ===== KOLOM KIRI: TOP 5 =====
with col_kiri:
    st.markdown("### 🕰️ 5 Vendor dengan Tanggal Terlama (Belum Terbayar)")
    
    df_top5 = df.copy()
    if filter_customer:
        df_top5 = df_top5[df_top5["Pelanggan"].isin(filter_customer)]
    if filter_pembayaran != "Semua":
        df_top5 = df_top5[df_top5["Pembayaran di"] == filter_pembayaran]
    
    df_belum_top5 = df_top5[df_top5['Keterangan'] == "Belum Terbayar"]
    df_valid_tanggal = df_belum_top5.dropna(subset=["Tanggal_Parse"])
    df_sorted = df_valid_tanggal.sort_values(by="Tanggal_Parse", ascending=True)
    top5_terlama = df_sorted.head(5)
    
    if not top5_terlama.empty:
        for idx, row in top5_terlama.iterrows():
            tanggal = row["Diterima Kantor Pusat/Kanwil"] if pd.notna(row["Diterima Kantor Pusat/Kanwil"]) else "-"
            pembayaran_di = row["Pembayaran di"] if pd.notna(row["Pembayaran di"]) else "-"
            top_internal = row["TOP Internal"] if pd.notna(row["TOP Internal"]) else "-"
            st.markdown(f"""
            <div class="list-item">
                <b>{row['Pelanggan']}</b><br>
                📅 {tanggal}<br>
                📍 {pembayaran_di}<br>
                💰 Rp {row['Nilai_Invoice_Bersih']:,.0f}<br>
                📌 {top_internal}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada data Belum Terbayar dengan tanggal yang valid")

# ===== KOLOM KANAN: PEMBAYARAN DI =====
with col_kanan:
    st.markdown("### 📍 Pembayaran di")
    
    if filter_pembayaran == "Semua":
        st.info("Pilih filter KANTOR PUSAT atau KANWIL di sidebar")
        df_tampil = df_filter.head(10)
    else:
        st.success(f"Menampilkan data dengan Pembayaran di: **{filter_pembayaran}**")
        df_tampil = df_filter.head(10)
    
    if not df_tampil.empty:
        for idx, row in df_tampil.iterrows():
            st.markdown(f"""
            <div class="list-item-orange">
                <b>{row['Pelanggan']}</b><br>
                📍 {row['Pembayaran di']}<br>
                💰 Rp {row['Nilai_Invoice_Bersih']:,.0f}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Tidak ada data untuk filter ini")

st.markdown("---")

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
st.info("🔄 Refresh data di sidebar untuk mengambil data terbaru")