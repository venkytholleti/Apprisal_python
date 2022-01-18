from fastapi.encoders import jsonable_encoder
from .. import models, schemas
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import JSONResponse, Response  
from fastapi.exceptions import HTTPException


router = APIRouter(tags=['Static'])

@router.get('/designations',response_model=List[schemas.Designation])
def get_all_designations(db: Session = Depends(get_db)):
    designations = db.query(models.Designation).all()  
    return designations


@router.get('/departments',response_model=List[schemas.Department])
def get_all_departments(db: Session = Depends(get_db)):
    departments = db.query(models.Department).all()  
    return departments


@router.get('/roles',response_model=List[schemas.RoleOut])
def get_all_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Role).all() 
    return roles


@router.get('/authorities',response_model=List[schemas.AuthoritiesOut])
def get_all_authorities(db: Session = Depends(get_db)):
    authorities = db.query(models.Authorities).all() 
    return authorities


@router.get('/role_authorities/{role_id}',response_model=List[schemas.NewOut])  
def get_authorities_by_role(role_id:int,response:Response,db: Session = Depends(get_db)):
    authorities = db.query(models.RoleAuthorities,models.RoleAuthorities.role_id,models.Authorities.authority_name).join(models.Authorities,models.RoleAuthorities.authority_id == models.Authorities.authority_id).filter(models.RoleAuthorities.role_id==role_id).all()
    return authorities


