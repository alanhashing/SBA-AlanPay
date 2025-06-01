from typing import Self, Sequence
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Relationship, SQLModel, Field

from app.database import AsyncSessionDep
from app.models.balance import Balance, MoneyDecimal

class UserBase(SQLModel):
    pass

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    password: str = Field(nullable=False)
    balances: list[Balance] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def total_balance(self) -> MoneyDecimal:
        return sum((balance.amount for balance in self.balances), Decimal('0.00'))

    @classmethod
    async def get_all_users(cls, session: AsyncSessionDep):
        result = await session.execute(select(cls))
        return result.scalars().all()
    
    @classmethod
    async def get_by_name(cls, session: AsyncSessionDep, name: str) -> Self | None:
        statement = select(cls).filter_by(name=name).limit(1)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @classmethod
    async def add(cls, session: AsyncSession, user: Self) -> Self:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @classmethod
    async def update(cls, session: AsyncSession, user: Self) -> Self:
        await session.merge(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    @classmethod
    async def get_user_with_total(
        cls,
        session: AsyncSessionDep,
        user_id: int
    ) -> tuple[Self | None, MoneyDecimal]:
        statement = select(cls).filter_by(id=user_id)
        result = await session.execute(statement)
        user: Self = result.scalar_one()
        return user, user.total_balance
    
    @classmethod
    async def get_balances_by_date(
        cls, 
        session: AsyncSessionDep, 
        user_id: int, 
        from_date: datetime
    ) -> Sequence[Balance]:
        statement = (
            select(Balance)
            .filter_by(user_id=user_id)
            .where(Balance.date >= from_date) # type: ignore
            .order_by(desc(Balance.date)) # type: ignore
        )
        result = await session.execute(statement)
        balances = result.scalars().all()
        return balances
    
class UserPublic(UserBase):
    id: int
    name: str
    balance: str

class UserCreate(UserBase):
    name: str
    password: str

class UserLogin(UserCreate):
    ...

class UserUpdate(UserBase):
    name: str | None = None
    password: str | None = None
