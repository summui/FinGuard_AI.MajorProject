# Contract upload and automated risk analysis endpoints — Sam
# Contract upload, analysis, and retrieval endpoints — Sam (Track B)
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.contract import Contract, ContractRisk
from app.services.document_extract import extract_contract_text
from app.services.gemini_client import analyze_contract
import tempfile
import os

router = APIRouter(prefix="/contracts", tags=["contracts"])

RISK_SCORE_MAP = {"High": 80, "Medium": 50, "Low": 20}


@router.post("/upload")
async def upload_contract(
    file: UploadFile,
    user: User = Depends(get_current_user)
):
    # BR-03 — file type guard
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")

    contents = await file.read()

    # BR-03 — file size guard
    if len(contents) > 15 * 1024 * 1024:
        raise HTTPException(400, "File exceeds 15MB limit.")

    # save to temp file for extraction
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        text = extract_contract_text(tmp_path)
        result = analyze_contract(text)
    except ValueError as e:
        raise HTTPException(422, str(e))
    finally:
        os.unlink(tmp_path)   # purge temp file — SRS privacy requirement
        text = None           # discard raw text immediately

    # build risk list from Gemini result
    risks = [
        ContractRisk(flag_type="red", category=f["category"], clause_text=f["clause_text"])
        for f in result.get("red_flags", [])
    ] + [
        ContractRisk(flag_type="green", category=f["category"], clause_text=f["clause_text"])
        for f in result.get("green_flags", [])
    ]

    contract = Contract(
        user_id=str(user.id),
        filename=file.filename,
        risk_score=RISK_SCORE_MAP.get(result["risk_rating"], 0),
        risk_level=result["risk_rating"],
        summary=result["summary"],
        risks=risks
    )
    await contract.insert()
    return contract


@router.get("")
async def list_contracts(user: User = Depends(get_current_user)):
    """Get all contracts for the current user."""
    return await Contract.find(Contract.user_id == str(user.id)).to_list()


@router.get("/{contract_id}")
async def get_contract(
    contract_id: str,
    user: User = Depends(get_current_user)
):
    """Get a single contract by ID — only if it belongs to the current user."""
    contract = await Contract.get(contract_id)
    if not contract or contract.user_id != str(user.id):
        raise HTTPException(404, "Contract not found.")
    return contract


def get_active_contract_risks(user_id: str):
    """
    Handoff function for Noor's AI Advisor module.
    Returns all contracts with their risk data for a given user.
    """
    return Contract.find(Contract.user_id == user_id).to_list()