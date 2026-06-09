from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional

# ==========================================
# SKEMA UNTUK PETUGAS (USER)
# ==========================================
class UserCreate(BaseModel):
    username: str
    password: str 
    role: str = "petugas"

class UserResponse(BaseModel):
    id: UUID
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SKEMA UNTUK ANGGOTA (MEMBER)
# ==========================================
class MemberCreate(BaseModel):
    name: str
    identity_no: str

class MemberResponse(BaseModel):
    id: UUID
    name: str
    identity_no: str
    status: bool

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SKEMA UNTUK KATALOG BARANG (PRODUCT)
# ==========================================
class ProductCreate(BaseModel):
    name: str
    category: str  # Contoh: "Bahan Pokok", "Minuman"
    type: str      # Contoh: "satuan", "paketan"
    unit: str      # Contoh: "kg", "liter", "pcs", "paket"

class ProductResponse(BaseModel):
    id: UUID
    name: str
    category: str
    type: str
    unit: str

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SKEMA TRANSAKSI & KERANJANG (DISTRIBUTION)
# ==========================================

# 1. Skema untuk item di dalam keranjang belanja
class DistributionItemCreate(BaseModel):
    product_id: UUID
    quantity: int = 1

class DistributionItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int

    model_config = ConfigDict(from_attributes=True)

# 2. Skema saat Anggota pertama kali membuat pesanan/PO
class DistributionCreate(BaseModel):
    member_id: UUID
    items: List[DistributionItemCreate] # Menerima ARRAY dari barang yang dipilih

# 3. Skema Response Lengkap (Rangkuman Pesanan yang akan dilihat Petugas)
class DistributionResponse(BaseModel):
    id: UUID
    member_id: UUID
    user_id: Optional[UUID] = None # Bisa bernilai null jika status masih pending
    status: str                    # "pending", "confirmed", "completed"
    date: datetime
    details: List[DistributionItemResponse] # Menampilkan list barang yang diambil

    model_config = ConfigDict(from_attributes=True)