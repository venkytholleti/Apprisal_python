from .. import models, schemas, utils
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db    
from starlette.responses import Response
from fastapi.exceptions import HTTPException

router = APIRouter(prefix='/users',tags=['Users'])

@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate,db: Session=Depends(get_db)):
    hashed_pwd = utils.hash(user.password)
    user.password = hashed_pwd
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/{id}',response_model=schemas.UserOut)
def get_user(id:int,response:Response,db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(user_id=id).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'User Data Not Found')
    return user