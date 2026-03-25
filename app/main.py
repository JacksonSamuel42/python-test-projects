import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRES_IN: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 30))  # 30m
REFRESH_TOKEN_EXPIRES_IN: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 7))  # 7days

app = FastAPI()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oath2_schema = OAuth2PasswordBearer(tokenUrl="auth/login_form")

# Routers
from routes.auth_routes import auth_router
from routes.order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)
