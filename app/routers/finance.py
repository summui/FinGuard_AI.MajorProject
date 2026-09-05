# Financial tracking and budget management endpoints — Noor
from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user
from app.models.user import User, FinancialProfile
from app.models.expense import Expense
from app.schemas.finance import ExpenseCreate, FinancialProfileUpdate

router = APIRouter(prefix="/finance", tags=["finance"])

@router.post("/profile")
async def update_profile(payload: FinancialProfileUpdate, user: User = Depends(get_current_user)):
    user.financial_profile = FinancialProfile(**payload.dict())
    await user.save()
    return user.financial_profile

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return user.financial_profile

@router.post("/expenses")
async def create_expense(payload: ExpenseCreate, user: User = Depends(get_current_user)):
    expense = Expense(user_id=str(user.id), **payload.dict())
    await expense.insert()
    return expense

@router.get("/expenses")
async def list_expenses(user: User = Depends(get_current_user)):
    return await Expense.find(Expense.user_id == str(user.id)).to_list()

@router.get("/budget-status")
async def budget_status(category: str, cap: float, user: User = Depends(get_current_user)):
    expenses = await Expense.find(
        Expense.user_id == str(user.id),
        Expense.category == category
    ).to_list()
    total = sum(e.amount for e in expenses)
    percent_over = ((total - cap) / cap * 100) if cap > 0 else 0
    return {
        "total": total,
        "cap": cap,
        "over_budget": percent_over > 15,
        "percent_over": round(percent_over, 2)
    }