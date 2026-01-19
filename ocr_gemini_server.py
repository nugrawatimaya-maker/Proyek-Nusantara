import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import json

app = Flask(__name__)
# Enable CORS so our HTML file can talk to this server
CORS(app)

# --- CONFIGURATION ---
# In production, use os.getenv('GEMINI_API_KEY')
# For this setup, we configure it directly as requested
GEMINI_API_KEY = "AIzaSyDprUloITMwkS3E-03aF5T1Hw3qSa9Nlc4"

genai.configure(api_key=GEMINI_API_KEY)

# Use the Flash model for speed and cost-efficiency
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_ktp_data(image_bytes):
    """
    Sends image to Gemini 1.5 Flash and asks for JSON extraction
    """
    image_part = Image.open(io.BytesIO(image_bytes))
    
    prompt = """
    Kamu adalah mesin OCR KTP Indonesia yang sangat akurat.
    Ekstrak data dari gambar KTP ini dan kembalikan HANYA dalam format JSON.
    Jangan gunakan markdown code block (```json ... ```). Langsung raw JSON object.
    
    Structure JSON yang diharapkan:
    {
        "nik": "string (hanya angka)",
        "nama": "string (nama lengkap bersih)",
        "ttl": "string (tempat tanggal lahir)",
        "alamat": "string (alamat lengkap, termasuk rt/rw/kelurahan)",
        "agama": "string",
        "status_perkawinan": "string (KAWIN / BELUM KAWIN / CERAI HIDUP / CERAI MATI)",
        "pekerjaan": "string",
        "kota_kabupaten": "string (hanya nama kota/kabupaten)"
    }
    
    Jika ada bagian yang tidak terbaca atau buram, kosongkan stringnya ("").
    Perbaiki typo OCR umum, misal 'N1K' jadi 'NIK', 'L4HIR' jadi 'LAHIR', '1SLAM' jadi 'ISLAM'.
    """
    
    try:
        response = model.generate_content([prompt, image_part])
        text_response = response.text.strip()
        
        # Cleanup if model still includes markdown
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "")
        
        return json.loads(text_response)
    except Exception as e:
        print(f"Error Gemini Generation: {e}")
        return None

@app.route('/ocr-gemini', methods=['POST'])
def ocr_gemini():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Read file into bytes
        image_bytes = file.read()
        
        # Process
        extracted_data = extract_ktp_data(image_bytes)
        
        if extracted_data:
            return jsonify({
                'success': True,
                'data': extracted_data
            })
        else:
            return jsonify({'error': 'Failed to extract data from AI'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🤖 Gemini OCR Server Running on http://localhost:5000")
    app.run(debug=True, port=5000)
