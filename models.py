import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="petugas")
    
    distributions = relationship("Distribution", back_populates="user")

class Member(Base):
    __tablename__ = "members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    identity_no = Column(String, unique=True, index=True, nullable=False)
    # Status ini akan berubah jadi True HANYA ketika paket fisik diserahkan
    status = Column(Boolean, default=False) 
    
    distributions = relationship("Distribution", back_populates="member")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False) # Contoh: "Bahan Pokok", "Minuman"
    type = Column(String, nullable=False)     # Contoh: "satuan", "paketan"
    unit = Column(String, nullable=False)     # Contoh: "kg", "liter", "pcs", "paket"
    
    # Kolom 'stock' KITA HAPUS karena ini sistem PO
    
    # Relasi ke detail transaksi
    distribution_details = relationship("DistributionDetail", back_populates="product")

class Distribution(Base):
    __tablename__ = "distributions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id = Column(UUID(as_uuid=True), ForeignKey("members.id"), nullable=False)
    
    # PERUBAHAN PENTING: nullable=True. 
    # Karena saat anggota pesen, belum ada petugas yang nangani. Nanti diisi pas petugas klik "Konfirmasi"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) 
    
    # State Machine Transaksi: "pending" -> "confirmed" -> "completed"
    status = Column(String, default="pending")
    date = Column(DateTime, default=datetime.utcnow)
    
    member = relationship("Member", back_populates="distributions")
    user = relationship("User", back_populates="distributions")
    
    # Relasi untuk nyambungin ke keranjang belanjaan (Cascade = kalau transaksi dihapus, detailnya ikut kehapus)
    details = relationship("DistributionDetail", back_populates="distribution", cascade="all, delete-orphan")

# TABEL BARU: Untuk menyimpan rincian barang apa saja yang dipilih anggota
class DistributionDetail(Base):
    __tablename__ = "distribution_details"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    distribution_id = Column(UUID(as_uuid=True), ForeignKey("distributions.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    
    distribution = relationship("Distribution", back_populates="details")
    product = relationship("Product", back_populates="distribution_details")