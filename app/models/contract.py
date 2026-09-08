# Contract document and risk assessment models — Sam
# Contract and embedded risk document models for MongoDB using Beanie ODM
from beanie import Document
from pydantic import BaseModel
from enum import Enum


class FlagType(str, Enum):
    red = "red"
    green = "green"


class ContractRisk(BaseModel):
    """Embedded risk clause — stored inside Contract, not a separate collection."""
    flag_type: FlagType
    category: str
    clause_text: str


class Contract(Document):
    user_id: str          # matches Noor's User ObjectId-as-string
    filename: str
    risk_score: int = 0   # High=80, Medium=50, Low=20
    risk_level: str = ""  # "High" / "Medium" / "Low"
    summary: str = ""     # Gemini plain-English summary
    risks: list[ContractRisk] = []

    class Settings:
        name = "contracts"