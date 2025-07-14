from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


# ✅ Alias to fix the import error
UserResponse = UserOut
