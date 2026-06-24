# ===== KOLOM KIRI: TOP 5 =====
with col_kiri:
    st.markdown("### 🕰️ 5 Vendor dengan Tanggal Terlama (Belum Terbayar)")
    
    # Ambil dari df (data asli) tapi tetap terpengaruh filter Customer dan Pembayaran di
    df_top5 = df.copy()
    
    if filter_customer:
        df_top5 = df_top5[df_top5["Pelanggan"].isin(filter_customer)]
    
    if filter_pembayaran != "Semua":
        df_top5 = df_top5[df_top5["Pembayaran di"] == filter_pembayaran]
    
    # 1. Ambil data dengan Q > 0 (Belum Terbayar)
    df_belum_top5 = df_top5[df_top5['Keterangan'] == "Belum Terbayar"]
    
    # 2. Ambil data dengan tanggal valid
    df_valid_tanggal = df_belum_top5.dropna(subset=["Tanggal_Parse"])
    
    # 3. Urutkan dari tanggal paling lama (ascending)
    df_sorted = df_valid_tanggal.sort_values(by="Tanggal_Parse", ascending=True)
    
    # 4. Ambil 5 data teratas
    top5_terlama = df_sorted.head(5)
    
    if not top5_terlama.empty:
        for idx, row in top5_terlama.iterrows():
            tanggal = row["Diterima Kantor Pusat/Kanwil"] if pd.notna(row["Diterima Kantor Pusat/Kanwil"]) else "-"
            pembayaran_di = row["Pembayaran di"] if pd.notna(row["Pembayaran di"]) else "-"
            top_internal = row["TOP Internal"] if pd.notna(row["TOP Internal"]) else "-"
            st.markdown(f"""
            <div style="
                background: #f0f2f6;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 8px;
                border-left: 4px solid #0033a0;
            ">
                <b>{row['Pelanggan']}</b><br>
                📅 {tanggal}<br>
                📍 {pembayaran_di}<br>
                💰 Rp {row['Nilai_Invoice_Bersih']:,.0f}<br>
                📌 {top_internal}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada data Belum Terbayar dengan tanggal yang valid")