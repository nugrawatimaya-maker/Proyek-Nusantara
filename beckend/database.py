import sqlite3
from typing import List, Optional, Dict, Any

DB_NAME = "database.db"

def init_db():
    """Inisialisasi tabel database jika belum ada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabel Kavling
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kavling (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blok TEXT NOT NULL,
        status TEXT NOT NULL,
        harga INTEGER NOT NULL
    )
    ''')
    
    # Seed data awal jika kosong
    cursor.execute('SELECT count(*) FROM kavling')
    if cursor.fetchone()[0] == 0:
        initial_data = [
            ("A1", "ready", 200000000),
            ("A2", "sold", 210000000),
            ("B1", "booking", 250000000),
        ]
        cursor.executemany('INSERT INTO kavling (blok, status, harga) VALUES (?, ?, ?)', initial_data)
        conn.commit()
        print("Database diinisialisasi dengan data awal.")
        
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Agar hasil query bisa diakses seperti dict
    return conn

# --- CRUD HELPER ---

def get_all_kavling() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    kavlings = conn.execute('SELECT * FROM kavling').fetchall()
    conn.close()
    return [dict(ix) for ix in kavlings]

def get_kavling_by_id(kavling_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    kavling = conn.execute('SELECT * FROM kavling WHERE id = ?', (kavling_id,)).fetchone()
    conn.close()
    if kavling:
        return dict(kavling)
    return None

def create_kavling(blok: str, status: str, harga: int) -> int:
    conn = get_db_connection()
    cursor = conn.execute('INSERT INTO kavling (blok, status, harga) VALUES (?, ?, ?)', (blok, status, harga))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_kavling(kavling_id: int, data: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    
    # Buat query dinamis
    set_clause = []
    values = []
    for key, value in data.items():
        if value is not None:
            set_clause.append(f"{key} = ?")
            values.append(value)
    
    if not set_clause:
        conn.close()
        return False
        
    values.append(kavling_id)
    query = f"UPDATE kavling SET {', '.join(set_clause)} WHERE id = ?"
    
    cursor = conn.execute(query, values)
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def delete_kavling(kavling_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM kavling WHERE id = ?', (kavling_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0
