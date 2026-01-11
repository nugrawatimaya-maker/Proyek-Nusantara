import json
import os
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

from datetime import date
from functools import lru_cache
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel, validator

app = FastAPI(title="Backend Proyek Nusantara")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Kavling(BaseModel):
    id: int
    blok: str
    status: str
    harga: int


class KavlingCreate(BaseModel):
    blok: str
    status: str
    harga: int


class KavlingUpdate(BaseModel):
    blok: Optional[str] = None
    status: Optional[str] = None
    harga: Optional[int] = None


from database import init_db, get_all_kavling, get_kavling_by_id, create_kavling as db_create, update_kavling as db_update, delete_kavling as db_delete

# Inisialisasi DB saat startup (akan dipanggil manual atau bisa pakai lifespan event di FastAPI nnti, 
# tapi untuk simplifikasi kita taruh di main scope atau startup event)
@app.on_event("startup")
def startup_db():
    init_db()


class Kavling(BaseModel):
    id: int
    blok: str
    status: str
    harga: int


class KavlingCreate(BaseModel):
    blok: str
    status: str
    harga: int


class KavlingUpdate(BaseModel):
    blok: Optional[str] = None
    status: Optional[str] = None
    harga: Optional[int] = None


@app.get("/")
def home():
    return {"message": "Backend Proyek Nusantara aktif (SQLite Connected)"}


@app.get("/kavling", response_model=List[Kavling])
def list_kavling():
    return get_all_kavling()


@app.get("/kavling/{kavling_id}", response_model=Kavling)
def get_kavling(kavling_id: int):
    item = get_kavling_by_id(kavling_id)
    if not item:
        raise HTTPException(status_code=404, detail="Kavling tidak ditemukan")
    return item


@app.post("/kavling", response_model=Kavling, status_code=201)
def create_kavling(payload: KavlingCreate):
    new_id = db_create(payload.blok, payload.status, payload.harga)
    # Return data yang baru dibuat
    return {
        "id": new_id,
        "blok": payload.blok,
        "status": payload.status,
        "harga": payload.harga
    }


@app.put("/kavling/{kavling_id}", response_model=Kavling)
def update_kavling(kavling_id: int, payload: KavlingUpdate):
    # Cek exist
    if not get_kavling_by_id(kavling_id):
        raise HTTPException(status_code=404, detail="Kavling tidak ditemukan")
    
    success = db_update(kavling_id, payload.dict(exclude_unset=True))
    if not success:
         raise HTTPException(status_code=500, detail="Gagal update")
         
    return get_kavling_by_id(kavling_id)


@app.delete("/kavling/{kavling_id}", status_code=204)
def delete_kavling(kavling_id: int):
    # Cek exist
    if not get_kavling_by_id(kavling_id):
        raise HTTPException(status_code=404, detail="Kavling tidak ditemukan")
        
    db_delete(kavling_id)


class Transaksi(BaseModel):
    tanggal: date
    jenis: str
    akun: str
    jumlah: int
    bank: Optional[str] = None
    keterangan: Optional[str] = None
    bukti: Optional[str] = None

    @validator("jenis")
    def validate_jenis(cls, value: str) -> str:
        if value not in {"kas-masuk", "kas-keluar"}:
            raise ValueError("Jenis transaksi harus kas-masuk atau kas-keluar")
        return value

    @validator("jumlah")
    def validate_jumlah(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Jumlah harus lebih besar dari 0")
        return value


SHEETS_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID") or os.getenv("GOOGLE_SPREADSHEET_ID")
SHEET_RANGE = os.getenv("GOOGLE_SHEET_RANGE", "Transaksi!A1")


@lru_cache
def _get_sheets_client():
    cred_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    cred_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if cred_file:
        creds = Credentials.from_service_account_file(cred_file, scopes=SHEETS_SCOPE)
    elif cred_json:
        creds = Credentials.from_service_account_info(json.loads(cred_json), scopes=SHEETS_SCOPE)
    else:
        raise RuntimeError("Kredensial Google Service Account belum dikonfigurasi.")

    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    return service.spreadsheets()


@app.post("/transaksi", status_code=201)
def submit_transaksi(payload: Transaksi):
    if not SPREADSHEET_ID:
        raise HTTPException(status_code=500, detail="GOOGLE_SHEET_ID belum diset.")

    try:
        sheets = _get_sheets_client()
    except Exception as exc:  # pragma: no cover - passtrough pesan ke klien
        raise HTTPException(status_code=500, detail=f"Gagal inisialisasi Sheets: {exc}") from exc

    values = [
        [
            payload.tanggal.isoformat(),
            payload.jenis,
            payload.akun,
            payload.jumlah,
            payload.bank or "-",
            payload.keterangan or "-",
            payload.bukti or "-",
        ]
    ]

    try:
        sheets.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE,
            valueInputOption="USER_ENTERED",
            body={"values": values},
        ).execute()
    except Exception as exc:  # pragma: no cover - passtrough pesan ke klien
        raise HTTPException(status_code=500, detail=f"Gagal menulis ke spreadsheet: {exc}") from exc

    return {"status": "ok"}


# --- LOCAL STORAGE INTEGRATION (FALLBACK) ---
from fastapi import UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
import shutil
import uuid
import os

# Mount folder uploads agar bisa diakses via URL
# Pastikan folder 'uploads' ada (sudah dibuat manual via command)
if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.post("/upload-drive")
async def upload_drive(file: UploadFile = File(...)):
    """
    Mengupload file ke penyimpanan LOKAL server (Folder 'uploads').
    Nama endpoint tetap '/upload-drive' agar tidak perlu ubah frontend.
    """
    try:
        # 1. Generate nama file unik agar tidak bentrok
        # Ambil ekstensi asli
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".png" # Default fallback
            
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = f"uploads/{unique_filename}"
        
        # 2. Simpan File ke Disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. Generate Link Akses
        # URL Lokal: http://localhost:8000/uploads/namafile.jpg
        # Kita pakai hardcode base URL atau ambil dari request jika perlu, 
        # tapi untuk simpel kita return relative atau absolute path
        
        # IP 0.0.0.0 berarti listener, untuk akses dari luar pakai IP LAN komputer ini
        # Untuk localhost user (browser di laptop yang sama), localhost aman.
        web_view_link = f"http://localhost:8000/{file_path}"
        
        return {
            "file_id": unique_filename,
            "web_view_link": web_view_link,
            "download_link": web_view_link
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gagal upload file: {exc}") from exc
