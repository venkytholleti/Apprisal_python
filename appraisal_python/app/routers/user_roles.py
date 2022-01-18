from .. import models, schemas, oauth2
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/api/v1/user_roles',tags=['User Roles'])

@router.get('/',response_model=List[schemas.UserRoles])
def get_all_user_roles(db: Session = Depends(get_db)):
    user_roles = db.query(models.UserRoles).all()  
    return user_roles


@router.get('/{user_role_id}',response_model=schemas.UserRoles)
def get_user_roles(id:int,response:Response,db: Session = Depends(get_db)):
    user_roles = db.query(models.UserRoles).filter_by(appraisee_id=id).first()
    if not user_roles:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return user_roles


@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.UserRoles)
def create_user_role(user_roles : schemas.UserRolesCreate,db: Session = Depends(get_db)):
    new_user_roles = models.UserRoles(**user_roles.dict())
    db.add(new_user_roles)
    db.commit()
    db.refresh(new_user_roles)
    return new_user_roles

@router.delete('/{user_role_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_user_role(id:int,response:Response,db: Session = Depends(get_db)):
    user_role = db.query(models.UserRoles).filter_by(appraisee_id=id)
    if not user_role.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    user_role.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
     

@router.put('/{id}',response_model=schemas.UserRoles)
def update_User_role(id:int,User_roles:schemas.UserRolesUpdate,db: Session = Depends(get_db)):
    user_role_query = db.query(models.UserRoles).filter_by(appraisee_id=id)

    if not user_role_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    user_role_query.update(user_role_query.dict(),synchronize_session=False)
    db.commit()
    return user_role_query.first()
