from datetime import datetime, timedelta, timezone

from dependencies import get_session, verify_token
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from main import (
    ACCESS_TOKEN_EXPIRES_IN,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRES_IN,
    SECRET_KEY,
    bcrypt_context,
)
from models import Users
from schemas import LoginSchema, UserSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def create_token(
    user_id: int, duration=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
) -> str:
    date_expiration = datetime.now(timezone.utc) + duration

    payload = {
        "sub": str(user_id),
        "exp": date_expiration,
    }

    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


def authenticate_user(email, password, session):
    user = session.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    return user


@auth_router.post("/register")
async def register(user_data: UserSchema, session=Depends(get_session)):
    existing_user = session.query(Users).filter(Users.email == user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="user already exist")

    hashed_password = bcrypt_context.hash(user_data.password)

    new_user = Users(
        user_data.name,
        user_data.email,
        hashed_password,
        user_data.active,
        user_data.admin,
    )

    session.add(new_user)
    session.commit()
    return {"message": f"user created successfully {user_data.email}"}


@auth_router.post("/login")
async def login(login_data: LoginSchema, session=Depends(get_session)):
    user = authenticate_user(login_data.email, login_data.password, session)

    if not user:
        raise HTTPException(status_code=400, detail="email or password incorrect")

    access_token = create_token(user.id)
    refresh_token = create_token(
        user.id, duration=timedelta(days=REFRESH_TOKEN_EXPIRES_IN)
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/login_form")
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)
):
    """Only for doc"""
    user = authenticate_user(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(status_code=400, detail="email or password incorrect")

    access_token = create_token(user.id)
    return {"access_token": access_token}


@auth_router.get("/refresh")
async def refresh_token(user: Users = Depends(verify_token)):
    access_token = create_token(user.id)
    return {"access_token": access_token}
