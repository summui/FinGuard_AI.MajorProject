# Authentication endpoints for user registration, login, and token management
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.schemas.user import UserRegister, UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister):
    existing = await User.find_one(User.email == payload.email)
    if existing:
        raise HTTPException(400, "Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    await user.insert()
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    user = await User.find_one(User.email == payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user