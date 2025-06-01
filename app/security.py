from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from cryptography.fernet import Fernet
import json

from app.config import settings
from app.database import AsyncSessionDep
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate a key for Fernet encryption (it should be stored securely)
fernet_key = Fernet.generate_key()
fernet = Fernet(fernet_key)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
async def get_current_user(
    session: AsyncSessionDep,
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    
    user = await User.get_by_name(session, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def encrypt_payload(payload: dict) -> str:
    # Convert payload to JSON string and encrypt
    payload_bytes = json.dumps(payload).encode()
    return fernet.encrypt(payload_bytes).decode()

def decrypt_payload(encrypted_payload: str) -> dict:
    # Decrypt and convert back to dict
    decrypted_bytes = fernet.decrypt(encrypted_payload.encode())
    return json.loads(decrypted_bytes.decode())

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard JWT claims
    payload.update({
        "exp": expire.timestamp(),
        "iat": datetime.now(timezone.utc).timestamp()
    })
    
    # Encrypt the payload
    encrypted_payload = encrypt_payload(payload)
    
    # Create the token with encrypted payload
    token_payload = {"encrypted_data": encrypted_payload}
    return jwt.encode(token_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        # Decode the JWT token
        token_data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        # Decrypt the payload
        decrypted_data = decrypt_payload(token_data["encrypted_data"])
        
        # Verify expiration
        exp = datetime.fromtimestamp(decrypted_data["exp"], tz=timezone.utc)
        if datetime.now(timezone.utc) >= exp:
            raise jwt.ExpiredSignatureError("Token has expired")
            
        return decrypted_data
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except Exception as e:
        raise ValueError(f"Error decoding token: {str(e)}")
