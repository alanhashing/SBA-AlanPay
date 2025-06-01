from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING, Annotated
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from pydantic import condecimal

if TYPE_CHECKING:
    from .user import User

MoneyDecimal = Annotated[Decimal, condecimal(max_digits=18, decimal_places=2)]

class BalanceBase(SQLModel):
    amount: MoneyDecimal = Field(default=Decimal('0.00'))
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Balance(BalanceBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    user: "User" = Relationship(back_populates="balances")

class BalancePublic(BalanceBase):
    id: int
    user_id: int
