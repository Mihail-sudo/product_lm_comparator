from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import (
    suppliers, categories, contacts, order_conditions,
    certificates, user_notes, comparison
)

app = FastAPI(
    title="Supplier API",
    description="API для работы с поставщиками продуктов питания",
    version="1.0.0"
)

# Настройка CORS (для Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация роутеров
app.include_router(suppliers.router)
app.include_router(categories.router)
app.include_router(contacts.router)
app.include_router(order_conditions.router)
app.include_router(certificates.router)
app.include_router(user_notes.router)
app.include_router(comparison.router)


@app.get("/")
def root():
    return {"message": "Supplier API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
