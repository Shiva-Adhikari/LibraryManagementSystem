# third party module
from pydantic import BaseModel, Field, EmailStr

# built in module
from typing import Optional


class AccountRegisterModel(BaseModel):
    username: str = Field(..., description='username of the account')
    password: str = Field(..., description='password of the account')
    email: Optional[EmailStr] = None
