from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

# Crear las tablas en la base de datos al arrancar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leads API - Backend")

# Configuración de CORS para permitir la conexión con el frontend de React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "success", "message": "Servidor FastAPI de Leads funcionando correctamente"}

@app.post("/leads/", response_model=schemas.LeadResponse)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    db_lead = models.Lead(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        raw_message=lead.raw_message,
        budget=lead.budget,
        budget_tier=lead.budget_tier,
        lead_score=lead.lead_score,
        status=lead.status
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@app.get("/leads/", response_model=List[schemas.LeadResponse])
def read_leads(db: Session = Depends(get_db)):
    leads = db.query(models.Lead).order_by(models.Lead.created_at.desc()).all()
    return leads

@app.put("/leads/{lead_id}", response_model=schemas.LeadResponse)
def update_lead(lead_id: int, updated_lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    db_lead.name = updated_lead.name
    db_lead.email = updated_lead.email
    db_lead.phone = updated_lead.phone
    db_lead.raw_message = updated_lead.raw_message
    db_lead.budget = updated_lead.budget
    db_lead.budget_tier = updated_lead.budget_tier
    db_lead.lead_score = updated_lead.lead_score
    db_lead.status = updated_lead.status

    db.commit()
    db.refresh(db_lead)
    return db_lead
