import json
import os
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


kavling_data: List[Kavling] = [
    Kavling(id=1, blok="A1", status="ready", harga=200_000_000),
    Kavling(id=2, blok="A2", status="sold", harga=210_000_000),
    Kavling(id=3, blok="B1", status="booking", harga=250_000_000),
]


def _find_kavling(kavling_id: int) -> Kavling:
    for item in kavling_data:
        if item.id == kavling_id:
            return item
    raise HTTPException(status_code=404, detail="Kavling tidak ditemukan")


@app.get("/")
def home():
    return {"message": "Backend Proyek Nusantara aktif"}


@app.get("/kavling", response_model=List[Kavling])
def list_kavling():
    return kavling_data


@app.get("/kavling/{kavling_id}", response_model=Kavling)
def get_kavling(kavling_id: int):
    return _find_kavling(kavling_id)


@app.post("/kavling", response_model=Kavling, status_code=201)
def create_kavling(payload: KavlingCreate):
    new_id = max([item.id for item in kavling_data], default=0) + 1
    kavling = Kavling(id=new_id, **payload.dict())
    kavling_data.append(kavling)
    return kavling


@app.put("/kavling/{kavling_id}", response_model=Kavling)
def update_kavling(kavling_id: int, payload: KavlingUpdate):
    kavling = _find_kavling(kavling_id)
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(kavling, key, value)
    return kavling


@app.delete("/kavling/{kavling_id}", status_code=204)
def delete_kavling(kavling_id: int):
    kavling = _find_kavling(kavling_id)
    kavling_data.remove(kavling)


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
