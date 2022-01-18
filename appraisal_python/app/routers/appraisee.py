from .. import models, schemas, utils, oauth2
from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException    


router = APIRouter(prefix='/appraisee/api/v1',tags=['Appraisee'])



@router.post('/appraisee',status_code=status.HTTP_201_CREATED,response_model=schemas.Appraisee)
def create_appraisee(appraisee : schemas.AppraiseeCreate,db: Session = Depends(get_db)):
    dept = db.query(models.Department).filter_by(department_id=appraisee.department_id).first()
    desg = db.query(models.Designation).filter_by(designation_id=appraisee.designation_id).first()
    if not dept:
        raise HTTPException(status.HTTP_404_NOT_FOUND,f"Selected Department Does Not Exist")
    if not desg:
        raise HTTPException(status.HTTP_404_NOT_FOUND,f"Selected Desgination Does Not Exist")
    emp = db.query(models.Appraisee).filter_by(appraisee_id=appraisee.appraisee_id).first()
    if emp:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE,f"Appraisee Already Exists With Provided Appraisee Id")
    appraisee.password = utils.hash(appraisee.password)
    new_appraisee = models.Appraisee(**appraisee.dict())
    db.add(new_appraisee)
    db.commit()
    db.refresh(new_appraisee)
    return new_appraisee

@router.get('/{id}',response_model=schemas.Appraisee)
def get_appraisee(id:int,response:Response,db: Session = Depends(get_db)):
    appraisee = db.query(models.Appraisee).filter_by(id=id).first()
    if not appraisee:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return appraisee

@router.get('/{department_id}',response_model=List[schemas.Appraisee])
def get_appraisee(department_id:int,response:Response,db: Session = Depends(get_db)):
    appraisee = db.query(models.Appraisee).filter_by(department_id=department_id).all()
    if not appraisee:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return appraisee

@router.put('/{id}',response_model=schemas.Appraisee)
def update_appraisee(id:int,appraisee:schemas.AppraiseeUpdate,db: Session = Depends(get_db)):
    appraisee_query = db.query(models.Appraisee).filter_by(id=id)

    if not appraisee_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    appraisee_query.update(appraisee.dict(),synchronize_session=False)
    db.commit()
    return appraisee_query.first()

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_appraisee(id:int,response:Response,db: Session = Depends(get_db)):
    appraisee = db.query(models.Appraisee).filter_by(id=id)
    if not appraisee.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    appraisee.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
        
