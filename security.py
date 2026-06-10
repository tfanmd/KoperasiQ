import os
import bcrypt # Kita pakai bcrypt langsung tanpa passlib
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ==========================================
# KONFIGURASI KEAMANAN
# ==========================================
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# 1. Fungsi untuk nge-hash password baru
def get_password_hash(password: str):
    # Bcrypt butuh format 'bytes', jadi string-nya kita encode dulu
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    
    # Kembalikan jadi string biar gampang disimpan di database PostgreSQL
    return hashed_password.decode('utf-8')

# 2. Fungsi untuk mengecek password saat login
def verify_password(plain_password: str, hashed_password: str):
    # Keduanya harus diubah ke bytes dulu sebelum diadu
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

# 3. Fungsi untuk mencetak tiket masuk (Token JWT)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt