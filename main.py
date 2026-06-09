from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import engine, get_db
import models
import schemas

models.Base.metadata.create_all(bind=engine)  # Membuat tabel di database jika belum ada
# Inisiasi aplikasi FastAPI
app = FastAPI(
    title="API Koperasi Sembako",
    description="Sistem manajemen distribusi sembako",
    version="1.0.0"
)

# Endpoint pertama (mirip Route::get('/') di Laravel)
@app.get("/")
def read_root():
    return {
        "status": "Sukses", 
        "pesan": "Server FastAPI Koperasi Sembako sudah menyala! 🚀"
    }

# enpoint member

@app.post("/api/members/", response_model=schemas.MemberResponse)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    # endpoint untuk membuat member baru
    db_member = db.query(models.Member).filter(models.Member.identity_no == member.identity_no).first()
    if db_member:
        raise HTTPException(status_code=400, detail="Member dengan nomor identitas ini sudah ada")
    # simpan data member baru ke database
    new_member = models.Member(name=member.name, identity_no=member.identity_no)
    # proses eksekusi penyimpanan data member baru ke database
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

# endpoint untuk menambahkan petugas
@app.post("/api/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # endpoint user baru
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    
    new_user = models.User(username=user.username, password_hash=user.password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# endpoint untuk mendapatkan daftar member, dengan fitur pencarian berdasarkan nama atau nomor identitas
@app.get("/api/members/", response_model=List[schemas.MemberResponse])
def get_members(search: str = None, db: Session = Depends(get_db)):
    # endpoint untuk mendapatkan daftar member, dengan fitur pencarian berdasarkan nama atau nomor identitas
    if search:
        members = db.query(models.Member).filter(
            models.Member.name.ilike(f"%{search}%") |
            models.Member.identity_no.ilike(f"%{search}%")
        ).all()
    else:
        members = db.query(models.Member).limit(50).all()
    return members

# endpoint untuk product (katalog barang) - untuk menambahkan item baru ke katalog dan melihat daftar katalog yang tersedia
@app.post("/api/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Menambahkan item katalog baru (Satuan / Paketan)"""
    new_product = models.Product(
        name=product.name,
        category=product.category,
        type=product.type,
        unit=product.unit
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/api/products", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    """Melihat daftar menu/katalog yang bisa dipilih anggota"""
    return db.query(models.Product).all()

# endpoint transaction
@app.post("/api/distributions", response_model=schemas.DistributionResponse)
def create_distribution(order: schemas.DistributionCreate, db: Session = Depends(get_db)):
    """Anggota memilih barang dan mengirim pesanan ke sistem (Status: Pending)"""
    
    # Validasi 1: Pastikan anggota ada dan belum pernah ambil sembako
    member = db.query(models.Member).filter(models.Member.id == order.member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Data anggota tidak ditemukan!")
    if member.status == True:
        raise HTTPException(status_code=400, detail="DITOLAK: Anggota ini SUDAH mengambil paket sembako!")

    try:
        # A. Buat nota induknya dulu
        new_dist = models.Distribution(
            member_id=order.member_id,
            status="pending"
            # user_id sengaja dibiarkan kosong (NULL) karena belum diproses petugas
        )
        db.add(new_dist)
        
        # MAGIC TRICK: db.flush() digunakan agar PostgreSQL meng-generate ID nota (new_dist.id) 
        # tanpa harus melakukan commit (simpan permanen) dulu. Kita butuh ID ini untuk keranjang.
        db.flush() 

        # B. Masukkan isi keranjang (list barang) satu per satu
        for item in order.items:
            new_detail = models.DistributionDetail(
                distribution_id=new_dist.id, # Pake ID nota yang baru aja dibuat
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(new_detail)

        # C. Simpan semuanya secara permanen
        db.commit()
        db.refresh(new_dist)
        return new_dist

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal memproses pesanan: {str(e)}")
    
# 2. PETUGAS MENGONFIRMASI PESANAN (ACC)
@app.put("/api/distributions/{dist_id}/confirm", response_model=schemas.DistributionResponse)
def confirm_distribution(dist_id: str, user_id: str, db: Session = Depends(get_db)):
    """Petugas mengecek keranjang dan klik ACC (Status: Confirmed)"""
    
    dist = db.query(models.Distribution).filter(models.Distribution.id == dist_id).first()
    if not dist:
        raise HTTPException(status_code=404, detail="Nota pesanan tidak ditemukan!")
    if dist.status != "pending":
        raise HTTPException(status_code=400, detail=f"Gagal! Pesanan ini berstatus: {dist.status}")

    # Stamp ID petugas ke nota ini dan ubah status
    dist.user_id = user_id
    dist.status = "confirmed"
    
    db.commit()
    db.refresh(dist)
    return dist

# 3. PETUGAS MENYERAHKAN BARANG FISIK (SELESAI)
@app.put("/api/distributions/{dist_id}/complete", response_model=schemas.DistributionResponse)
def complete_distribution(dist_id: str, db: Session = Depends(get_db)):
    """Petugas menyerahkan fisik sembako dan menutup transaksi (Status: Completed)"""
    
    dist = db.query(models.Distribution).filter(models.Distribution.id == dist_id).first()
    if not dist:
        raise HTTPException(status_code=404, detail="Nota pesanan tidak ditemukan!")
    if dist.status != "confirmed":
        raise HTTPException(status_code=400, detail="Gagal! Pesanan harus di-ACC (Confirmed) terlebih dahulu!")

    # A. Ubah status nota menjadi selesai
    dist.status = "completed"

    # B. Gembok akun anggota agar tidak bisa pesan lagi (status = True)
    member = db.query(models.Member).filter(models.Member.id == dist.member_id).first()
    if member:
        member.status = True

    db.commit()
    db.refresh(dist)
    return dist