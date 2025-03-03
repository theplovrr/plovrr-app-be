from pydantic import BaseModel

# Schema for Creating a User
class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str

# Schema for Updating a User
class UserUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    password: str | None = None

# Schema for Returning User Data
class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True
