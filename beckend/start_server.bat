@echo off
echo Mengaktifkan Virtual Environment...
call venv\Scripts\activate

echo Menjalankan Server Backend Proyek Nusantara...
echo Server akan aktif di http://localhost:8000
echo Tekan Ctrl+C untuk berhenti.
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
