from starlette.status import HTTP_404_NOT_FOUND
from .. import models, schemas, oauth2, utils
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException
from typing import Optional


router = APIRouter(tags=['All'])
    

@router.put('/disqualify')
def disqualify_employee(appraisee:schemas.Disqualify,db: Session = Depends(get_db)):
    appraisee = db.query(models.Appraisee).filter_by(id=appraisee.appraisee_id).first()
    appraisee.status = 2
    db.add(appraisee)
    db.commit()
    db.refresh(appraisee)
    return {"message":"Employee Disqualified"}

@router.get('/managers')
def get_all_managers(db: Session = Depends(get_db)):
    managers = db.query(models.Appraisee).filter_by(status=1).all()
    return managers

@router.get('/roles',response_model=List[schemas.RoleOut])
def get_all_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Role).all() 
    return roles

@router.get('/roles/{id}',response_model=schemas.RoleOut)
def get_role(id:int,response:Response,db: Session = Depends(get_db)):
    role = db.query(models.Role).filter_by(role_id=id).first()
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return role

@router.post('/roles',status_code=status.HTTP_201_CREATED,response_model=schemas.RoleOut)
def create_role(role : schemas.RoleCreate,db: Session = Depends(get_db)):
    new_role = models.Role(**role.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@router.delete('/roles/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_role(id:int,response:Response,db: Session = Depends(get_db)):
    role = db.query(models.Role).filter_by(role_id=id)
    if not role.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    role.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/roles/{id}',response_model=schemas.RoleOut)
def update_role(id:int,role:schemas.Role,db: Session = Depends(get_db)):
    role_query = db.query(models.Role).filter_by(role_id=id)

    if not role_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')

    role_query.update(role.dict(),synchronize_session=False)
    db.commit()
    return role_query.first()

@router.get('/authorities',response_model=List[schemas.AuthoritiesOut])
def get_all_authorities(db: Session = Depends(get_db)):
    authorities = db.query(models.Authorities).all() 
    return authorities

@router.get('/authorities/{id}',response_model=schemas.AuthoritiesOut)
def get_authority(id:int,response:Response,db: Session = Depends(get_db)):
    authority = db.query(models.Authorities).filter_by(authority_id=id).first()
    if not authority:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return authority

@router.post('/authorities',status_code=status.HTTP_201_CREATED,response_model=schemas.AuthoritiesOut)
def create_authority(authority : schemas.AuthoritiesCreate,db: Session = Depends(get_db)):
    new_authority = models.Authorities(**authority.dict())
    db.add(new_authority)
    db.commit()
    db.refresh(new_authority)
    return new_authority

@router.delete('/authorities/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_authority(id:int,response:Response,db: Session = Depends(get_db)):
    authority = db.query(models.Authorities).filter_by(authority_id=id)
    if not authority.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    authority.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/authorities/{id}',response_model=schemas.AuthoritiesOut)
def update_authority(id:int,authority:schemas.Authorities,db: Session = Depends(get_db)):
    authority_query = db.query(models.Authorities).filter_by(authority_id=id)

    if not authority_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')

    authority_query.update(authority.dict(),synchronize_session=False)
    db.commit()
    return authority_query.first()



@router.get('/role_authorities',response_model=List[schemas.RoleAuthoritiesOut])
def get_all_role_authorities(db: Session = Depends(get_db)):
    role_authorities = db.query(models.RoleAuthorities).all() 
    return role_authorities

# @router.get('/role_authorities/{role_id}',response_model=List[schemas.RoleAuthoritiesOut])
# def get_authorities_by_role(role_id:int,response:Response,db: Session = Depends(get_db)):
#     authorities = db.query(models.RoleAuthorities).filter_by(role_id=role_id).all()
#     return [db.query(models.Authorities).filter_by(authority_id=i.authority_id).first().authority_name for i in authorities]
        
#     if not authorities:
#         raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
#     return authorities


@router.post('/role_authorities',status_code=status.HTTP_201_CREATED,response_model=schemas.RoleAuthoritiesOut)
def create_role_authority(role_authority : schemas.RoleAuthoritiesCreate,db: Session = Depends(get_db)):
    new_role_authority = models.RoleAuthorities(**role_authority.dict())
    db.add(new_role_authority)
    db.commit()
    db.refresh(new_role_authority)
    return new_role_authority

@router.delete('/role_authorities/{role_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_role_authority(role_id:int,response:Response,db: Session = Depends(get_db)):
    role_authority = db.query(models.RoleAuthorities).filter_by(role_id=role_id)
    if not role_authority.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    role_authority.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put('/role_authorities/{role_id}',response_model=schemas.RoleAuthoritiesOut)
def update_role_authority(id:int,role_authority:schemas.RoleAuthoritiesOut,db: Session = Depends(get_db)):
    role_authority_query = db.query(models.RoleAuthorities).filter_by(authority_id=id)

    if not role_authority_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')

    role_authority_query.update(role_authority.dict(),synchronize_session=False)
    db.commit()
    return role_authority_query.first()