from fastapi import FastAPI

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