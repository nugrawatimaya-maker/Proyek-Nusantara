import re
import cv2
import numpy as np
import easyocr
import io
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS so our HTML file can talk to this server
CORS(app)

# Use existing EasyOCR logic (Local Intelligence)
# This removes dependency on Google API entirely
print("🚀 Loading Local OCR Engine (EasyOCR)... This may take a moment first time...")
reader = easyocr.Reader(['id'], gpu=False) 
print("✅ Local OCR Engine Loaded!")

def preprocess_image(image_bytes):
    # Convert upload to OpenCV format
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Resize if too large for speed
    height, width = img.shape[:2]
    if width > 1280:
        scale = 1280 / width
        img = cv2.resize(img, None, fx=scale, fy=scale)
    
    return img

def parse_ktp_output(text_list):
    """
    Mapping OCR text list to strictly formatted JSON for frontend
    """
    data = {
        "nik": "",
        "nama": "",
        "ttl": "",
        "alamat": "",
        "agama": "",
        "status_perkawinan": "",
        "pekerjaan": "",
        "kota_kabupaten": ""
    }
    
    # Helper to clean text
    def clean(vals):
        return [v.upper().strip() for v in vals]
    
    cleaned_list = clean(text_list)
    print("DEBUG OCR:", cleaned_list)

    for i, line in enumerate(cleaned_list):
        # 1. NIK (Priority)
        if "NIK" in line or len(re.sub(r'[^0-9]', '', line)) >= 15:
            digits = re.sub(r'[^0-9]', '', line)
            if len(digits) >= 15:
                data["nik"] = digits[:16]

        # 2. Nama
        if "NAMA" in line:
            # Grab value from this line after : or Name header
            val = line.replace("NAMA", "").replace(":", "").strip()
            # If empty, take next line
            if len(val) < 2 and i+1 < len(cleaned_list):
                val = cleaned_list[i+1]
            data["nama"] = re.sub(r'[^A-Z .,\'\-]', '', val)

        # 3. TTL (Tempat Tgl Lahir)
        if "LAHIR" in line or "TEMPAT" in line:
            val = line.replace("TEMPAT", "").replace("TGL", "").replace("LAHIR", "").replace(":", "").strip()
            if len(val) < 3 and i+1 < len(cleaned_list):
                val = cleaned_list[i+1]
            data["ttl"] = val

        # 4. Alamat
        if "ALAMAT" in line:
            val = line.replace("ALAMAT", "").replace(":", "").strip()
            # Address usually spans multiple lines
            full_addr = val
            if i+1 < len(cleaned_list) and "RT/RW" not in cleaned_list[i+1]: 
                full_addr += " " + cleaned_list[i+1]
            data["alamat"] = full_addr.strip()

        # 5. Agama
        if "AGAMA" in line:
            val = line.replace("AGAMA", "").replace(":", "").strip()
             # Often OCR puts value on next line
            if len(val) < 2 and i+1 < len(cleaned_list):
                val = cleaned_list[i+1]
            # Normalize agama
            val = val.split(' ')[0] # "ISLAM ..." -> "ISLAM"
            data["agama"] = val

        # 6. Status Perkawinan
        if "KAWIN" in line:
            if "BELUM" in line: data["status_perkawinan"] = "BELUM KAWIN"
            elif "CERAI" in line: data["status_perkawinan"] = "CERAI HIDUP" # Default guess
            else: data["status_perkawinan"] = "KAWIN"

        # 7. Pekerjaan
        if "PEKERJAAN" in line:
            val = line.replace("PEKERJAAN", "").replace(":", "").strip()
            if len(val) < 2 and i+1 < len(cleaned_list):
                val = cleaned_list[i+1]
            data["pekerjaan"] = val

        # 8. Kota/Kabupaten (Header detection)
        # Usually at top lines
        if i < 4 and ("KOTA" in line or "KABUPATEN" in line):
            data["kota_kabupaten"] = line.replace("PROVINSI", "").strip()

    return data

@app.route('/ocr-gemini', methods=['POST'])
def ocr_local():
    # Keep endpoint name '/ocr-gemini' so we don't break frontend
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image_bytes = file.read()
        
        # 1. Preprocess
        img = preprocess_image(image_bytes)
        
        # 2. Run EasyOCR
        # detail=0 returns simple list of strings
        text_results = reader.readtext(img, detail=0)
        
        # 3. Parse to JSON
        extracted_data = parse_ktp_output(text_results)
        
        return jsonify({
            'success': True,
            'data': extracted_data
        })

    except Exception as e:
        print("ERROR OCR:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🤖 Local OCR Server (EasyOCR) Running on http://localhost:5000")
    print("   Note: Endpoint remains /ocr-gemini for compatibility.")
    app.run(debug=True, port=5000)
