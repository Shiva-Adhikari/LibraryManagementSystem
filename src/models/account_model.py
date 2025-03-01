from pydantic import BaseModel, Field
from typing import Optional


class AccountRegisterModel(BaseModel):
    username: str = Field(..., description='username of the account')
    password: str = Field(..., description='password of the account')
    id: int = Field(..., description='unique identifier for the account')
    whoami: str = Field(..., description='Defines whether the account if for "user" or "admin"')
    email: Optional[str] = Field(..., description='email address required for user accounts')
