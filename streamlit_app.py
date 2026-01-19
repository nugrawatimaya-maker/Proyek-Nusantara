import streamlit as st
import pandas as pd
import pdfplumber
from supabase import create_client, Client
import cv2
import numpy as np
import easyocr
import re
from PIL import Image

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
                match_url = re.search(r'URL:\s*["\']([^"\']+)["\']', content)
                match_key = re.search(r'KEY:\s*["\']([^"\']+)["\']', content)
                if match_url and match_key:
                    return create_client(match_url.group(1), match_key.group(1))
        except:
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
        # 1. NIK
        if "NIK" in line or len(re.sub(r'[^0-9]', '', line)) >= 15:
            digits = re.sub(r'[^0-9]', '', line)
            if len(digits) >= 15:
                data["nik"] = digits[:16]

        # 2. Nama
        if "NAMA" in line:
            val = line.replace("NAMA", "").replace(":", "").strip()
            if len(val) < 2 and i+1 < len(cleaned_list):
                val = cleaned_list[i+1]
            data["nama"] = re.sub(r'[^A-Z .,\'\-]', '', val)

        # 3. TTL
        if "LAHIR" in line or "TEMPAT" in line:
            val = line.replace("TEMPAT", "").replace("TGL", "").replace("LAHIR", "").replace(":", "").strip()
            if len(val) < 3 and i+1 < len(cleaned_list):
                val = cleaned_list[i+1]
            data["ttl"] = val

        # 4. Alamat
        if "ALAMAT" in line:
            val = line.replace("ALAMAT", "").replace(":", "").strip()
            full_addr = val
            if i+1 < len(cleaned_list) and "RT/RW" not in cleaned_list[i+1]: 
                full_addr += " " + cleaned_list[i+1]
            data["alamat"] = full_addr.strip()

        # 5. Agama
        if "AGAMA" in line:
            val = line.replace("AGAMA", "").replace(":", "").strip()
            if len(val) < 2 and i+1 < len(cleaned_list):
                val = cleaned_list[i+1]
            data["agama"] = val.split(' ')[0]

        # 6. Status Perkawinan
        if "KAWIN" in line:
            if "BELUM" in line: data["status_perkawinan"] = "BELUM KAWIN"
            elif "CERAI" in line: data["status_perkawinan"] = "CERAI HIDUP"
            else: data["status_perkawinan"] = "KAWIN"

        # 7. Pekerjaan
        if "PEKERJAAN" in line:
            val = line.replace("PEKERJAAN", "").replace(":", "").strip()
            if len(val) < 2 and i+1 < len(cleaned_list):
                val = cleaned_list[i+1]
            data["pekerjaan"] = val

        # 8. Kota
        if i < 4 and ("KOTA" in line or "KABUPATEN" in line):
            data["kota_kabupaten"] = line.replace("PROVINSI", "").strip()

    return data

# --- PAGES ---

def page_reconciliation():
    st.header("🤖 Robot Rekonsiliasi Bank")
    st.write("Upload file Rekening Koran PDF untuk dicocokkan dengan data ERP.")
    
    uploaded_file = st.file_uploader("Upload Rekening Koran (PDF)", type="pdf")
    if uploaded_file:
        with pdfplumber.open(uploaded_file) as pdf:
            data_list = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    for row in table:
                        clean_row = [x for x in row if x is not None]
                        if len(clean_row) >= 3:
                            data_list.append(clean_row)
            
            df = pd.DataFrame(data_list)
            st.write("📄 **Preview Data Bank:**")
            st.dataframe(df.head())
            st.info("Fitur rekonsiliasi otomatis siap dihubungkan dengan Supabase Anda.")

def page_ocr_ktp():
    st.header("📸 OCR KTP Scanner (AI)")
    st.write("Upload foto KTP untuk mengekstrak data otomatis menggunakan EasyOCR.")
    
    img_file = st.file_uploader("Upload Foto KTP", type=['png', 'jpg', 'jpeg'])
    
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption='Foto Terupload', use_container_width=True)
        
        if st.button("🔍 Scan KTP Sekarang"):
            with st.spinner("Sedang memproses AI (Mungkin butuh waktu untuk inisialisasi)..."):
                try:
                    # 1. Preprocess
                    cv_img = preprocess_image(img_file)
                    
                    # 2. Load Model & Read
                    reader = load_ocr_reader()
                    result = reader.readtext(cv_img, detail=0)
                    
                    # 3. Parse
                    parsed_data = parse_ktp_output(result)
                    
                    # 4. Display
                    st.success("Scan Selesai!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_input("NIK", parsed_data['nik'])
                        st.text_input("Nama", parsed_data['nama'])
                        st.text_input("Tempat/Tgl Lahir", parsed_data['ttl'])
                        st.text_input("Alamat", parsed_data['alamat'])
                    
                    with col2:
                        st.text_input("Agama", parsed_data['agama'])
                        st.text_input("Status Perkawinan", parsed_data['status_perkawinan'])
                        st.text_input("Pekerjaan", parsed_data['pekerjaan'])
                        st.text_input("Kota/Kabupaten", parsed_data['kota_kabupaten'])
                        
                    st.json(parsed_data)
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

# --- MAIN APP ---
def main():
    st.sidebar.title("Navigasi")
    menu = st.sidebar.radio("Pilih Tools:", ["OCR KTP Scanner", "Rekonsiliasi Bank"])
    
    if menu == "OCR KTP Scanner":
        page_ocr_ktp()
    elif menu == "Rekonsiliasi Bank":
        page_reconciliation()
        
    st.sidebar.markdown("---")
    st.sidebar.info("Proyek Nusantara Tools v2.0")

if __name__ == "__main__":
    main()
