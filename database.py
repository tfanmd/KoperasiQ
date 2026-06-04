import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1. Baca file .env
load_dotenv()

# 2. Ambil URL database, kalau ga ada di .env, pake nilai default (fallback)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Bikin 'Engine' (Ini ibarat jembatan antara Python dan PostgreSQL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 4. Bikin 'Session' (Ini ibarat ruang kerja kita untuk query ke database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Base class untuk semua Model/Tabel kita nanti (mirip class Model di Laravel)
Base = declarative_base()

# 6. Dependency: Fungsi buat buka dan tutup koneksi otomatis setiap kali ada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()