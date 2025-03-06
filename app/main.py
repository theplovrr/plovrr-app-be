import asyncio

from argon2 import PasswordHasher
from fastapi import FastAPI, Response, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud import get_users, create_user, get_user_by_login
from app.database.database import get_db
from config import Config
from app.models.user import User, LoginRequest, RegisterRequest
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

config = Config()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

origins = [
    config.get("Settings.FrontendURL"), "http://127.0.0.1:8000"
]

app.add_middleware(CORSMiddleware,
                   # allow_origins=["*"],
                   allow_origins=origins,  # React frontend
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

ph = PasswordHasher()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/")
def read_root():
    return {"message": "Hello world",
            "debug": config.get("Settings.Debug"),
            "frontendUrl": config.get("Settings.FrontendURL")}


@app.post("/login")
async def login(response: Response, loginRequest: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_login(db, loginRequest.email)
    if user is None:
        raise HTTPException(status_code=401, detail='Email not found')

    try:
        ph.verify(user.password, loginRequest.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail='Incorrect password')

    user_data = {"sub": user.email}  # Payload for JWT
    token = create_access_token(user_data, timedelta(minutes=600))

    # Set token in HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Prevents access from JavaScript
        samesite="none",  # Adjust as needed for cross-domain requests
        secure=True,  # Set to True in production with HTTPS
    )
    return {"email": user.email, "firstname": user.firstname, "lastname": user.lastname}

@app.get("/protected")
async def protected_route(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = await get_user_by_login(db, email)
        return { "email": user.email, "firstname": user.firstname, "lastname": user.lastname }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token",
        httponly=True,
        samesite="none",
        secure=True,
    )
    return {"message": "Logged out"}

@app.get("/listusers")
async def list_users(db: AsyncSession = Depends(get_db)):
    return await get_users(db)

@app.post("/register")
async def register_user(registerRequest: RegisterRequest, db: AsyncSession = Depends(get_db)):
    hashed_password = ph.hash(registerRequest.password)
    try:
        created = await create_user(db,
                                 registerRequest.firstname,
                                 registerRequest.lastname,
                                 registerRequest.email,
                                 hashed_password)
        return created
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'{str(e)}')




import os

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)