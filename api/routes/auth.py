# api/routes/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.security import authenticate_user, create_access_token

router = APIRouter(tags=["Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(body: LoginRequest):
    user = authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=body.email, role=user["role"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "role": user["role"]
        }
    }


