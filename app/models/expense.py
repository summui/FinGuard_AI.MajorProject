# Expense and transaction models for personal finance tracking — Noor
from beanie import Document
from pydantic import Field
from datetime import date
from enum import Enum

class Category(str, Enum):
    Food = "Food"
    Shopping = "Shopping"
    Travel = "Travel"
    Bills = "Bills"
    Healthcare = "Healthcare"
    Education = "Education"
    Others = "Others"

class Expense(Document):
    user_id: str
    category: Category
    amount: float = Field(..., gt=0)
    date: date

    class Settings:
        name = "expenses"