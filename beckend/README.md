# Backend Proyek Nusantara

FastAPI service to serve kavling data for the Nusantara project.

## Menjalankan lokal
1) Buat dan aktifkan virtualenv baru (disarankan):
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
   - Linux/macOS: `python -m venv .venv && source .venv/bin/activate`
2) Install dependensi: `pip install -r requirements.txt`
3) Jalankan server: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## Endpoints
- `GET /` health/message
- `GET /kavling` daftar kavling
- `GET /kavling/{id}` detail kavling
- `POST /kavling` tambah kavling (body: blok, status, harga)
- `PUT /kavling/{id}` ubah kavling (opsional blok/status/harga)
- `DELETE /kavling/{id}` hapus kavling
