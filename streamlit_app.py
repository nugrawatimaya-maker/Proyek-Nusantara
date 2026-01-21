import streamlit as st
import pandas as pd
import pdfplumber
from supabase import create_client, Client
import cv2
import numpy as np
import easyocr
import re
from PIL import Image
from datetime import datetime

# --- CONFIG & AUTH ---
st.set_page_config(page_title="Tools Proyek Nusantara", page_icon="🤖", layout="wide")

# Init Supabase
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except:
        # Fallback local config
        try:
            with open("app_config.js", "r") as f:
                content = f.read()
                # Find the PROD block manually or just regex the first occurrence of key-value
                # Match URL: "..."
                url_match = re.search(r'URL:\s*"([^"]+)"', content)
                # Match KEY: "..." (look for sb_publishable...)
                key_match = re.search(r'KEY:\s*"(sb_publishable_[^"]+)"', content)
                
                if url_match and key_match:
                    st.toast("Connected to Supabase via app_config.js", icon="🔌")
                    return create_client(url_match.group(1), key_match.group(1))
                else:
                    st.error("Gagal membaca config dari app_config.js. Pastikan format URL/KEY benar.")
                    return None
        except Exception as e:
            st.error(f"Config Error: {e}")
            return None

supabase = init_supabase()

# --- CACHED RESOURCES ---
@st.cache_resource
def load_ocr_reader():
    # Load EasyOCR model (cached so it doesn't reload heavily)
    return easyocr.Reader(['id'], gpu=False)

# --- FUNGSI OCR HELPER ---
def preprocess_image(image_bytes):
    # Convert PIL/Bytes to OpenCV
    file_bytes = np.asarray(bytearray(image_bytes.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # Resize Logic (keep aspect ratio, max width 1000px for speed)
    height, width = img.shape[:2]
    if width > 1280:
        scale = 1280 / width
        img = cv2.resize(img, None, fx=scale, fy=scale)
    return img

def parse_ktp_output(text_list):
    data = {
        "nik": "", "nama": "", "ttl": "", "alamat": "", 
        "agama": "", "status_perkawinan": "", "pekerjaan": "", "kota_kabupaten": ""
    }
    
    cleaned_list = [v.upper().strip() for v in text_list]
    
    for i, line in enumerate(cleaned_list):
        if "NIK" in line or len(re.sub(r'[^0-9]', '', line)) >= 15:
            digits = re.sub(r'[^0-9]', '', line)
            if len(digits) >= 15: data["nik"] = digits[:16]

        if "NAMA" in line:
            val = line.replace("NAMA", "").replace(":", "").strip()
            if len(val) < 2 and i+1 < len(cleaned_list): val = cleaned_list[i+1]
            data["nama"] = re.sub(r'[^A-Z .,\'\-]', '', val)

        if "LAHIR" in line or "TEMPAT" in line:
            val = line.replace("TEMPAT", "").replace("TGL", "").replace("LAHIR", "").replace(":", "").strip()
            if len(val) < 3 and i+1 < len(cleaned_list): val = cleaned_list[i+1]
            data["ttl"] = val

        if "ALAMAT" in line:
            val = line.replace("ALAMAT", "").replace(":", "").strip()
            full_addr = val
            if i+1 < len(cleaned_list) and "RT/RW" not in cleaned_list[i+1]: 
                full_addr += " " + cleaned_list[i+1]
            data["alamat"] = full_addr.strip()

        if "AGAMA" in line:
            val = line.replace("AGAMA", "").replace(":", "").strip()
            if len(val) < 2 and i+1 < len(cleaned_list): val = cleaned_list[i+1]
            data["agama"] = val.split(' ')[0]

        if "KAWIN" in line:
            if "BELUM" in line: data["status_perkawinan"] = "BELUM KAWIN"
            elif "CERAI" in line: data["status_perkawinan"] = "CERAI HIDUP"
            else: data["status_perkawinan"] = "KAWIN"

        if "PEKERJAAN" in line:
            val = line.replace("PEKERJAAN", "").replace(":", "").strip()
            if len(val) < 2 and i+1 < len(cleaned_list): val = cleaned_list[i+1]
            data["pekerjaan"] = val

        if i < 4 and ("KOTA" in line or "KABUPATEN" in line):
            data["kota_kabupaten"] = line.replace("PROVINSI", "").strip()

    return data

# --- FUNGSI REKONSILIASI ---
def extract_mutations_from_pdf(uploaded_file):
    mutations = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                clean = line.strip()
                # Helper Regex for Indo Bank Format (DD/MM and Amount with dots)
                date_match = re.search(r'(\d{2})[\/-](\d{2})', clean)
                amount_match = re.search(r'[\d\.]+,(\d{2})', clean) # 1.500.000,00
                
                if date_match and amount_match:
                    amount_str = amount_match.group(0).replace('.', '').replace(',', '.')
                    try:
                        amount = float(amount_str)
                        is_credit = 'CR' in clean.upper()
                        is_debit = 'DB' in clean.upper() # Or assume default
                        
                        # Simplistic DB/CR detection logic, adjust as needed per Bank format
                        mutations.append({
                            "date": date_match.group(0),
                            "amount": amount,
                            "desc": clean,
                            "raw": clean
                        })
                    except: pass
    return pd.DataFrame(mutations)

def get_unreconciled_transactions():
    if not supabase: return pd.DataFrame()
    response = supabase.table('transaksi').select("*").eq('is_reconciled', False).execute()
    return pd.DataFrame(response.data)

def perform_matching(df_bank, df_sys):
    matched_ids = []
    results = []
    
    # Simple Exact Amount Match Logic
    for idx, row in df_bank.iterrows():
        bank_amt = row['amount']
        
        # Find candidate in System (Tolerance 1.0)
        candidates = df_sys[
            (df_sys['jumlah'] >= bank_amt - 1) & 
            (df_sys['jumlah'] <= bank_amt + 1) &
            (~df_sys['id'].isin(matched_ids))
        ]
        
        match_status = "Unmatched"
        sys_id = None
        
        if not candidates.empty:
            # Pick first available (Idea: Check Date proximity later)
            best_match = candidates.iloc[0]
            sys_id = best_match['id']
            matched_ids.append(sys_id)
            match_status = "Matched"
            
        results.append({
            "Bank Date": row['date'],
            "Bank Desc": row['desc'],
            "Bank Amount": bank_amt,
            "Status": match_status,
            "System ID": sys_id
        })
        
    return pd.DataFrame(results), matched_ids

# --- PAGES ---

def page_reconciliation():
    st.header("🤖 Robot Rekonsiliasi Bank")
    st.info("Fitur ini akan mencocokkan Upload PDF dengan Database Transaksi (Supabase) secara otomatis.")
    
    uploaded_file = st.file_uploader("Upload Rekening Koran (PDF)", type="pdf")
    
    if uploaded_file and supabase:
        st.write("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📂 **1. Membaca PDF...**")
            df_bank = extract_mutations_from_pdf(uploaded_file)
            st.success(f"Ditemukan {len(df_bank)} baris mutasi di PDF.")
            st.dataframe(df_bank.head(), use_container_width=True)

        with col2:
            st.write("🗄️ **2. Mengambil Data Sistem (Supabase)...**")
            df_sys = get_unreconciled_transactions()
            if df_sys.empty:
                st.warning("Tidak ada transaksi Unreconciled di database.")
            else:
                st.success(f"Ditemukan {len(df_sys)} transaksi outstanding di sistem.")
                st.dataframe(df_sys[['tanggal', 'keterangan', 'jumlah', 'jenis_transaksi']].head(), use_container_width=True)
        
        if not df_bank.empty and not df_sys.empty:
            st.write("---")
            if st.button("🚀 Jalankan Pencocokan & Update Database", type="primary"):
                progress_bar = st.progress(0)
                st.write("🔄 Sedang mencocokkan...")
                
                df_results, matched_ids = perform_matching(df_bank, df_sys)
                progress_bar.progress(50)
                
                st.write("📊 **Hasil Pencocokan:**")
                st.dataframe(df_results, use_container_width=True)
                
                # Update Database
                if matched_ids:
                    st.write(f"💾 Menyimpan {len(matched_ids)} transaksi cocok ke Database...")
                    tgl_rekon = datetime.now().strftime("%Y-%m-%d")
                    
                    try:
                        response = supabase.table('transaksi').update({
                            'is_reconciled': True,
                            'tgl_rekon': tgl_rekon
                        }).in_('id', matched_ids).execute()
                        
                        progress_bar.progress(100)
                        st.success(f"✅ SUKSES! {len(matched_ids)} transaksi telah direkonsiliasi di Database.")
                        st.balloons()
                        st.info("Silakan refresh halaman Dashboard HTML Anda untuk melihat perubahannya.")
                    except Exception as e:
                        st.error(f"Gagal update database: {e}")
                else:
                    st.warning("Tidak ada transaksi yang cocok ditemukan.")
                    progress_bar.progress(100)

def page_ocr_ktp():
    st.header("📸 OCR KTP Scanner (AI)")
    st.write("Upload foto KTP untuk mengekstrak data otomatis menggunakan EasyOCR.")
    
    img_file = st.file_uploader("Upload Foto KTP", type=['png', 'jpg', 'jpeg'])
    
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption='Foto Terupload', use_container_width=True)
        
        if st.button("🔍 Scan KTP Sekarang"):
            with st.spinner("Sedang memproses AI..."):
                try:
                    cv_img = preprocess_image(img_file)
                    reader = load_ocr_reader()
                    result = reader.readtext(cv_img, detail=0)
                    parsed_data = parse_ktp_output(result)
                    
                    st.success("Scan Selesai!")
                    st.json(parsed_data)
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# --- MAIN APP ---
def main():
    st.sidebar.image("logo.png", width=100) if "logo.png" in ["logo.png"] else None # Optional Logo
    st.sidebar.title("Navigasi")
    menu = st.sidebar.radio("Pilih Tools:", ["OCR KTP Scanner", "Rekonsiliasi Bank"])
    
    if menu == "OCR KTP Scanner":
        page_ocr_ktp()
    elif menu == "Rekonsiliasi Bank":
        page_reconciliation()
        
    st.sidebar.markdown("---")
    if supabase:
        st.sidebar.success("🟢 Database Terhubung")
    else:
        st.sidebar.error("🔴 Database Gagal")

if __name__ == "__main__":
    main()
