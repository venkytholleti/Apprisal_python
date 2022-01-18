from .. import models, schemas, oauth2
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/master/api/v1/employee_appraisal',tags=['Employee Appraisal'])

@router.get('/',response_model=List[schemas.EmployeeAppraisal])
def get_all_employee_appraisal(db: Session = Depends(get_db)):
    employee_appraisal = db.query(models.EmployeeAppraisal).all()  
    return employee_appraisal


@router.get('/{id}',response_model=schemas.EmployeeAppraisal)
def get_employee_appraisal(id:int,response:Response,db: Session = Depends(get_db)):
    employee_appraisal = db.query(models.EmployeeAppraisal).filter_by(id=id).first()
    if not employee_appraisal:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return employee_appraisal


@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.EmployeeAppraisal)
def create_employee_appraisal(employee_appraisal : schemas.EmployeeAppraisalCreate,db: Session = Depends(get_db)):
    new_employee_appraisal = models.EmployeeAppraisal(**employee_appraisal.dict())
    db.add(new_employee_appraisal)
    db.commit()
    db.refresh(new_employee_appraisal)
    return new_employee_appraisal

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_appraisal(id:int,response:Response,db: Session = Depends(get_db)):
    employee_appraisal = db.query(models.EmployeeAppraisal).filter_by(id=id)
    if not employee_appraisal.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    employee_appraisal.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
     

@router.put('/{id}',response_model=schemas.EmployeeAppraisal)
def update_department(id:int,employee_appraisal:schemas.EmployeeAppraisalUpdate,db: Session = Depends(get_db)):
    employee_appraisal_query = db.query(models.EmployeeAppraisal).filter_by(id=id)

    if not employee_appraisal_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    employee_appraisal_query.update(employee_appraisal.dict(),synchronize_session=False)
    db.commit()
    return employee_appraisal_query.first()
