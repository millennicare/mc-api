# global dependencies

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db

T_Database = Annotated[AsyncSession, Depends(get_db)]
