from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, Form, Response

from app.database import AsyncSessionDep
from app.models.user import User
from app.models.balance import Balance
from app.models.balance import MoneyDecimal
from app.security import get_current_user
from app.qr_gen import create_qr_codeas_svg, create_qr_codeas_png


router = APIRouter(
    prefix="/api/pay",
    tags=["pay"]
)

@router.post("/topup")
async def topup(session: AsyncSessionDep, current_user: User = Depends(get_current_user), amount: MoneyDecimal = Form(...)):
    if amount <= Decimal('0.00'):
        return {"message": "Top-up amount must be greater than zero."}
    current_user.balances.append(Balance(user_id=current_user.id, amount=amount))
    await session.commit()
    # await session.refresh(current_user)
    return {"message": "Top-up payment processed successfully."}

@router.post("/withdraw")
async def withdraw(session: AsyncSessionDep, current_user: User = Depends(get_current_user), amount: MoneyDecimal = Form(...)):
    total_balance = current_user.total_balance
    if total_balance <= Decimal('0.00'):
        return {"message": "Insufficient balance for withdrawal."}
    if amount > total_balance:
        return {"message": "Withdrawal amount exceeds total balance."}
    current_user.balances.append(Balance(user_id=current_user.id, amount=-amount))
    await session.commit()
    # await session.refresh(current_user)

    return {"message": "Withdrawal payment processed successfully."}

@router.post("/transfer")
async def transfer(session: AsyncSessionDep, current_user: User = Depends(get_current_user)):
    return {"message": "Transfer payment processed successfully."}

@router.get("/history")
async def get_history(
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user),
    history_months: int = 6
):
    cutoff_date = datetime.now() - timedelta(days=30 * history_months)
    
    filtered_balances = await User.get_balances_by_date(
        session=session,
        user_id=current_user.id,
        from_date=cutoff_date
    )

    return {
        "name": current_user.name,
        "total_balance": f"{current_user.total_balance:.2f}",
        "history_months": history_months,
        "balances": [
            {
                "id": balance.id,
                "amount": f"{balance.amount:.2f}",
                "created_at": balance.date.isoformat(),
            } for balance in filtered_balances
        ]
    }

@router.get("/qrcode")
async def get_qrcode(
    session: AsyncSessionDep,
    current_user: User = Depends(get_current_user)
) -> Response:
    # Generate a QR code for the user's payment information
    qr_code_data = f"User: {current_user.name}, Balance: {current_user.total_balance:.2f}"
    # qr_code = create_qr_codeas_svg(qr_code_data)
    # return {"qr_svg": qr_code.getvalue().decode('utf-8')}
    qr_code = create_qr_codeas_png(qr_code_data)
    return Response(
        content=qr_code.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": "inline; filename=qrcode.png"}
    )
