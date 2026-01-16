
import os
import re
import cv2
import numpy as np
import easyocr
from flask import Flask, request, jsonify
from flask_cors import CORS
from imagekitio import ImageKit

app = Flask(__name__)
CORS(app)  # Enable CORS for local testing

# Initialize ImageKit
imagekit = ImageKit(
    public_key='public_ZzBxgXWQzaOlUvj+11M6G39Si4s=',
    private_key='private_d1MgRwtWJzF4hasu3e0ZhaC+e3Q=',
    url_endpoint='https://ik.imagekit.io/iqdv5umlm'
)

@app.route('/auth', methods=['GET'])
def imagekit_auth():
    try:
        # Generate auth parameters for client-side SDK
        auth_params = imagekit.get_authentication_parameters()
        return jsonify(auth_params)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize EasyOCR Reader (Loads model into memory once)
# 'id' for Indonesian. gpu=False for compatibility on standard laptops.
print("Loading AI Model (EasyOCR)... please wait...")
reader = easyocr.Reader(['id'], gpu=False) 
print("Model Loaded!")

def preprocess_image(file_stream):
    # Convert uploaded file to numpy array
    file_bytes = np.frombuffer(file_stream.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # Optional: Resize if too large to speed up processing
    height, width = image.shape[:2]
    if width > 1024:
        scale = 1024 / width
        image = cv2.resize(image, None, fx=scale, fy=scale)
    
    return image

def parse_ktp_data(text_list):
    """
    Parses raw list of strings from EasyOCR into KTP dictionary
    """
    data = {
        'nik': '',
        'nama': '',
        'ttl': '',
        'alamat': '',
        'agama': '',
        'status': '',
        'pekerjaan': '',
        'kota': ''
    }
    
    # Join all text for easier regex searching
    full_text = ' '.join(text_list).upper()
    
    # Helper for fuzzy cleaning
    def clean(val):
        return val.replace(':', '').replace('.', '').trim()

    for i, line in enumerate(text_list):
        line = line.upper().strip()
        
        # NIK
        if 'NIK' in line or (len(re.sub(r'[^0-9]', '', line)) >= 15):
             nums = re.sub(r'[^0-9]', '', line)
             if len(nums) >= 15:
                 data['nik'] = nums[:16]

        # Nama
        if 'NAMA' in line:
            # Try to grab value from this line or next
            val = line.replace('NAMA', '').replace(':', '').strip()
            if len(val) < 2 and i+1 < len(text_list):
                val = text_list[i+1].strip()
            data['nama'] = re.sub(r'[^A-Z .,]', '', val)

        # TTL
        if 'LAHIR' in line or 'TEMPAT' in line:
            val = line.replace('TEMPAT', '').replace('TGL', '').replace('LAHIR', '').replace(':', '').replace('/', '').strip()
            if len(val) < 3 and i+1 < len(text_list):
                val = text_list[i+1].strip()
            data['ttl'] = val

        # Alamat
        if 'ALAMAT' in line:
            val = line.replace('ALAMAT', '').replace(':', '').strip()
            # If address header is alone, verify next lines
            full_addr = val
            # Grab next 2 lines greedily if they usually contain RT/RW/KEL
            if i+1 < len(text_list): full_addr += " " + text_list[i+1]
            if i+2 < len(text_list): full_addr += " " + text_list[i+2]
            
            data['alamat'] = full_addr.strip()

        # Agama
        if 'AGAMA' in line:
            val = line.replace('AGAMA', '').replace(':', '').strip()
            if len(val) < 2 and i+1 < len(text_list): val = text_list[i+1]
            data['agama'] = val.split(' ')[0] # Usually just first word
        elif line in ['ISLAM', 'KRISTEN', 'KATOLIK', 'HINDU', 'BUDDHA', 'KONGHUCU']:
            data['agama'] = line

        # Status
        if 'KAWIN' in line:
            if 'BELUM' in line: data['status'] = 'BELUM KAWIN'
            elif 'CERAI' in line: data['status'] = 'CERAI HIDUP/MATI'
            else: data['status'] = 'KAWIN'
        
        # Pekerjaan
        if 'PEKERJAAN' in line:
             val = line.replace('PEKERJAAN', '').replace(':', '').strip()
             if len(val) < 2 and i+1 < len(text_list): val = text_list[i+1]
             data['pekerjaan'] = val

        # Kota (Header detection)
        if i < 4 and ('KOTA' in line or 'KABUPATEN' in line):
             data['kota'] = line.replace('PROVINSI', '').strip()

    return data

@app.route('/ocr', methods=['POST'])
def run_ocr():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    try:
        # Preprocess
        img = preprocess_image(file)
        
        # Run EasyOCR
        # detail=0 returns just the strings
        results = reader.readtext(img, detail=0)
        
        print("Raw OCR Output:", results) # Debugging
        
        # Parse Logic
        parsed = parse_ktp_data(results)
        
        return jsonify({
            'success': True,
            'data': parsed,
            'raw': results
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run on port 5000
    app.run(debug=True, port=5000)
