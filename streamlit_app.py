import streamlit as st
import pandas as pd
import pdfplumber
from supabase import create_client, Client
import io

# Judul Halaman
st.set_page_config(page_title="Robot Rekonsiliasi Tri Wijaya", page_icon="🤖")
st.title("🤖 Asisten Rekonsiliasi Bank - Tri Wijaya")

# --- KONEKSI DATABASE ---
try:
    # Coba baca dari secrets.toml dulu (opsional)
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except:
    # Fallback: Baca dari app_config.js (Biar tidak perlu setting 2x)
    import re
    try:
        with open("app_config.js", "r") as f:
            content = f.read()
            # Regex sederhana untuk ambil URL & KEY dari blok PROD/DEV
            # Asumsi kita ambil yang PROD/Default
            match_url = re.search(r'URL:\s*["\']([^"\']+)["\']', content)
            match_key = re.search(r'KEY:\s*["\']([^"\']+)["\']', content)
            
            if match_url and match_key:
                url = match_url.group(1)
                key = match_key.group(1)
            else:
                st.error("Gagal membaca config dari app_config.js")
                st.stop()
    except FileNotFoundError:
        st.error("File app_config.js tidak ditemukan.")
        st.stop()

# Init Client
try:
    supabase: Client = create_client(url, key)
    # Silent success verify
    # st.sidebar.success("✅ DB Connected") 
except Exception as e:
    st.error(f"Gagal koneksi Supabase: {e}")
    st.stop() 

# --- FUNGSI ---
def baca_pdf(uploaded_file):
    data_list = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table:
                    # Bersihkan data kosong
                    clean_row = [x for x in row if x is not None]
                    if len(clean_row) >= 3: # Asumsi minimal ada Tgl, Ket, Nominal
                        data_list.append(clean_row)
    
    # Ubah ke DataFrame (Sesuaikan nama kolom dengan PDF Bank Anda)
    # Ini contoh generik, nanti bisa disesuaikan lagi setelah lihat PDF asli
    df = pd.DataFrame(data_list)
    return df

def ambil_jurnal_unreconciled():
    # Mengambil data dari tabel 'jurnal' (sesuaikan nama tabel Anda di Supabase)
    # Kita ambil yang statusnya belum 'reconciled'
    if 'supabase' in locals():
        response = supabase.table('jurnal_transaksi').select("*").eq('status', 'draft').execute()
        return pd.DataFrame(response.data)
    return pd.DataFrame()

def update_status_jurnal(id_jurnal):
    if 'supabase' in locals():
        supabase.table('jurnal_transaksi').update({'status': 'reconciled'}).eq('id', id_jurnal).execute()

# --- TAMPILAN UTAMA ---
st.write("Silakan upload Rekening Koran (PDF) di bawah ini:")
uploaded_file = st.file_uploader("Upload File", type="pdf")

if uploaded_file:
    st.info("Sedang membaca file...")
    try:
        df_bank = baca_pdf(uploaded_file)
        st.write("📄 **Preview Data Bank:**")
        st.dataframe(df_bank.head())

        if st.button("🚀 Jalankan Pencocokan Otomatis"):
            st.write("Sedang mengambil data ERP...")
            df_erp = ambil_jurnal_unreconciled()
            
            if df_erp.empty:
                st.warning("Tidak ada data jurnal yang perlu direkonsiliasi di ERP (atau koneksi DB gagal).")
            else:
                progress_bar = st.progress(0)
                jumlah_cocok = 0
                
                # Simulasi Logika Loop (Nanti disesuaikan kolomnya)
                for index, row in df_bank.iterrows():
                    # Update progress bar
                    progress_bar.progress((index + 1) / len(df_bank))
                    
                    # Logika pencocokan (Disini nanti kita fine-tuning)
                    # Misal: Mencari nominal yang sama
                    # ... kode matching ...
                
                st.success(f"Selesai! {jumlah_cocok} transaksi berhasil dicocokkan.")
                
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca PDF: {e}")
