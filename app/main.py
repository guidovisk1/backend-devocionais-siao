from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, devotionals, categories, comments, users
from . import models
from .config import settings
from . import auth as auth_service

app = FastAPI(title="Devocional SIÃO API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(devotionals.router)
app.include_router(categories.router)
app.include_router(comments.router)
app.include_router(users.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    _create_first_admin()


def _create_first_admin():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == settings.first_admin_email).first()
        if not existing:
            admin = models.User(
                name=settings.first_admin_name,
                email=settings.first_admin_email,
                password_hash=auth_service.hash_password(settings.first_admin_password),
                role=models.UserRole.admin,
            )
            db.add(admin)
            db.commit()
            print(f"Admin criado: {settings.first_admin_email}")
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Devocional SIÃO API", "docs": "/docs"}
