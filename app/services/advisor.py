# Multi-modal AI advisor engine combining financial summaries and contract insights — Joint
# Multi-modal AI advisor engine combining financial summaries and contract insights — Joint
import json
from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

ADVISOR_PROMPT = """You are FinGuard AI's financial health advisor. 
Analyze the following user financial data and contract risks, then return STRICT JSON only, 
no markdown, matching this exact schema:

{{
  "health_score": <integer 0-100>,
  "diagnosis": [
    {{
      "severity": "critical" | "warning" | "good",
      "title": "short title",
      "detail": "one sentence explanation"
    }}
  ],
  "prescription": [
    "actionable advice string 1",
    "actionable advice string 2",
    "actionable advice string 3"
  ],
  "summary": "2-3 sentence overall financial health narrative"
}}

Health score calculation guide:
- Start at 100
- Deduct 20 if expenses > 80% of salary
- Deduct 15 if EMI > 30% of salary  
- Deduct 10 if savings rate < 20%
- Deduct 10 per High risk contract
- Deduct 5 per Medium risk contract
- Add 5 if savings rate > 30%

User Financial Data:
- Monthly Salary: ₹{salary}
- Total Monthly EMI: ₹{emi}
- Total Expenses This Month: ₹{total_expenses}
- Savings This Month: ₹{savings}
- Savings Rate: {savings_rate}%
- EMI to Income Ratio: {emi_ratio}%
- Top Spending Categories: {top_categories}

Contract Risks:
{contract_summary}

Return ONLY the JSON object. No explanation, no markdown, no extra text.
"""


def calculate_health_score(salary: float, emi: float, total_expenses: float, 
                             high_risk: int, medium_risk: int) -> int:
    score = 100
    if salary > 0:
        expense_ratio = total_expenses / salary
        savings_rate = (salary - total_expenses - emi) / salary * 100
        emi_ratio = emi / salary * 100

        if expense_ratio > 0.8:
            score -= 20
        if emi_ratio > 30:
            score -= 15
        if savings_rate < 20:
            score -= 10
        elif savings_rate > 30:
            score += 5

    score -= high_risk * 10
    score -= medium_risk * 5
    return max(0, min(100, score))


async def generate_advisor_report(user_id: str) -> dict:
    """
    Main advisor function.
    Pulls finance + contract data for a user and generates AI diagnosis.
    """
    from app.models.user import User
    from app.models.expense import Expense
    from app.models.contract import Contract

    # fetch user financial profile
    user = await User.get(user_id)
    if not user:
        raise ValueError("User not found")

    salary = user.financial_profile.monthly_salary
    emi = user.financial_profile.total_emi

    # fetch expenses
    expenses = await Expense.find(Expense.user_id == user_id).to_list()
    total_expenses = sum(e.amount for e in expenses)

    # top spending categories
    category_totals = {}
    for e in expenses:
        category_totals[e.category] = category_totals.get(e.category, 0) + e.amount
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]
    top_categories_str = ", ".join([f"{cat}: ₹{amt:.0f}" for cat, amt in top_categories])

    # savings
    savings = max(0, salary - total_expenses - emi)
    savings_rate = round((savings / salary * 100) if salary > 0 else 0, 1)
    emi_ratio = round((emi / salary * 100) if salary > 0 else 0, 1)

    # fetch contracts
    contracts = await Contract.find(Contract.user_id == user_id).to_list()
    high_risk = sum(1 for c in contracts if c.risk_level == "High")
    medium_risk = sum(1 for c in contracts if c.risk_level == "Medium")

    contract_summary = "No contracts analyzed yet."
    if contracts:
        contract_summary = "\n".join([
            f"- {c.filename}: {c.risk_level} risk (score {c.risk_score}/100)"
            for c in contracts
        ])

    # build prompt
    prompt = ADVISOR_PROMPT.format(
        salary=salary,
        emi=emi,
        total_expenses=total_expenses,
        savings=savings,
        savings_rate=savings_rate,
        emi_ratio=emi_ratio,
        top_categories=top_categories_str or "No expenses recorded",
        contract_summary=contract_summary
    )

    # call Gemini
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            cleaned = (
                response.text
                .strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            result = json.loads(cleaned)
            result["health_score"] = calculate_health_score(
                salary, emi, total_expenses, high_risk, medium_risk
            )
            return result
        except (json.JSONDecodeError, Exception):
            if attempt == 2:
                raise
            continue