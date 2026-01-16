import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import cv2
import numpy as np
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for local testing

# Initialize Reader (Download model only once)
print("Loading OCR Model... Please wait.")
reader = easyocr.Reader(['id'], gpu=False) 
print("OCR Model Ready!")

def extract_ktp_info(text_list):
    """
    Simple heuristic to find NIK and Name from OCR result list.
    """
    nik = None
    nama = None
    
    # regex for NIK: 16 digits
    nik_pattern = re.compile(r'\d{16}')
    
    for i, text in enumerate(text_list):
        text = text.upper()
        
        # Find NIK
        if not nik:
            match = nik_pattern.search(text.replace(" ", "")) # remove spaces for loose matching
            if match:
                nik = match.group(0)
                continue
            # Fallback if "NIK" label is found
            if 'NIK' in text and i+1 < len(text_list):
                 # Check next line or same line parts
                 pass

        # Find Name (Very basic heuristic: usually below NIK or after 'Nama')
        if 'NAMA' in text:
            # Clean "Nama :" prefix
            clean_name = text.replace('NAMA', '').replace(':', '').strip()
            if len(clean_name) > 2:
                nama = clean_name
            elif i+1 < len(text_list):
                # Maybe name is on next line
                nama = text_list[i+1]
    
    return nik, nama

@app.route('/ocr/ktp', methods=['POST'])
def process_ktp():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "No image uploaded"}), 400
    
    file = request.files['image']
    
    # Read image
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    if img is None:
        return jsonify({"success": False, "message": "Invalid image format"}), 400

    try:
        # Run OCR
        results = reader.readtext(img, detail=0)
        print("OCR Results:", results)
        
        nik, nama = extract_ktp_info(results)
        
        return jsonify({
            "success": True,
            "nik": nik,
            "nama": nama,
            "raw_text": results
        })

    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
