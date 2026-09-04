# User model with embedded FinancialProfile
from beanie import Document
from pydantic import BaseModel, EmailStr
from datetime import datetime

class FinancialProfile(BaseModel):
    monthly_salary: float = 0.0
    total_emi: float = 0.0

class User(Document):
    email: EmailStr
    password_hash: str
    created_at: datetime = datetime.utcnow()
    financial_profile: FinancialProfile = FinancialProfile()

    class Settings:
        name = "users"