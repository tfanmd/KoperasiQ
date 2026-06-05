from fastapi import FastAPI
from database import engine
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