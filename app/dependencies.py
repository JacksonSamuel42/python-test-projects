from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from main import ALGORITHM, SECRET_KEY, oath2_schema
from models import Users, db
from sqlalchemy.orm import Session


def get_session():
    with Session(db) as session:
        yield session


def verify_token(
    token: str = Depends(oath2_schema), session: Session = Depends(get_session)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")

        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = int(sub)
        user = session.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return user
    except JWTError as err:
        print(err)
        raise HTTPException(status_code=401, detail="Invalid token")
