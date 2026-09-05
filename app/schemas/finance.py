# Pydantic schemas for expenses, budgets, and financial analytics requests/responses — Noor
from pydantic import BaseModel, Field
from datetime import date
from app.models.expense import Category

class ExpenseCreate(BaseModel):
    category: Category
    amount: float = Field(..., gt=0)
    date: date

class ExpenseOut(BaseModel):
    id: str
    category: Category
    amount: float
    date: date

class FinancialProfileUpdate(BaseModel):
    monthly_salary: float
    total_emi: float

class BudgetCheckResponse(BaseModel):
    total: float
    cap: float
    over_budget: bool
    percent_over: float