# AI Advisor chat and financial/contract recommendation endpoints — Joint
# AI Advisor chat and financial/contract recommendation endpoints — Joint
from fastapi import APIRouter, Depends, HTTPException
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.advisor import generate_advisor_report

router = APIRouter(prefix="/advisor", tags=["advisor"])


@router.get("/report")
async def get_advisor_report(user: User = Depends(get_current_user)):
    """Generate a full financial health report combining finance + contract data."""
    try:
        report = await generate_advisor_report(str(user.id))
        return report
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Advisor generation failed: {str(e)}")