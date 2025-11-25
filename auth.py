from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import models
import schemas
from config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for authentication
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


async def get_tutor_by_username(username: str) -> Optional[models.TutorProfile]:
    """Get a tutor by username."""
    return await models.TutorProfile.get_or_none(username=username)


async def authenticate_tutor(username: str, password: str) -> Optional[models.TutorProfile]:
    """Authenticate a tutor by username and password."""
    tutor = await get_tutor_by_username(username)
    if not tutor or not verify_password(password, tutor.hashed_password):
        return None
    return tutor


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create an access token with expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_tutor(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> models.TutorProfile:
    """Get the current authenticated tutor from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    tutor = await get_tutor_by_username(username=token_data.username)
    if tutor is None:
        raise credentials_exception
    return tutor


async def get_current_active_tutor(current_tutor: models.TutorProfile = Depends(get_current_tutor)) -> models.TutorProfile:
    """Get the current active tutor."""
    # In a real application, you might want to check if the tutor is active
    # For now, we assume all authenticated tutors are active
    return current_tutor


async def get_current_senior_tutor(
    current_tutor: models.TutorProfile = Depends(get_current_tutor)
) -> models.TutorProfile:
    """Get the current senior tutor (for operations requiring senior tutor privileges)."""
    if not current_tutor.is_senior:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires senior tutor privileges"
        )
    return current_tutor
