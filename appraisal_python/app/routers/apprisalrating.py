from .. import models, schemas
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/appraisalrating/api/v1',tags=['Appraisalrating'])

# @router.post('/emp_by_dept_and_desg',response_model=List[schemas.AppraiseByDeptDesgOut])
# def get_all_departments(data : schemas.AppraiseByDeptDesg,db: Session = Depends(get_db)):
#     appraisers = db.query(models.Appraisee).filter_by(department_id=data.department_id,designation_id=data.designation_id).all()  
#     return appraisers

@router.get('/',response_model=List[schemas.Appraisalrating])
def get_all_appraisalrating(db: Session = Depends(get_db)):
    apprisalratings = db.query(models.AppraisalRating).all()  
    return apprisalratings


@router.get('/{appraisal_rating_id}',response_model=schemas.Appraisalrating)
def get_apprisalrating(appraisal_rating_id:int,response:Response,db: Session = Depends(get_db)):

    appraisalrating = db.query(models.AppraisalRating).filter_by(appraisal_rating_id=appraisal_rating_id).first()
    if not appraisalrating:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return appraisalrating


@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.Appraisalrating)
def create_apprisalrating(appraisalrating : schemas.Appraisalrating_create,db: Session = Depends(get_db)):
    new_appraisalrating = models.AppraisalRating(**appraisalrating.dict())
    db.add(new_appraisalrating)
    db.commit()
    db.refresh(new_appraisalrating)
    return new_appraisalrating

@router.delete('/{appraisal_rating_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_appraisalrating(appraisal_rating_id:int,response:Response,db: Session = Depends(get_db)):

    appraisalrating = db.query(models.AppraisalRating).filter_by(appraisal_rating_id=appraisal_rating_id)
    if not appraisalrating.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    appraisalrating.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
        

@router.put('/{appraisal_rating_id}',response_model=schemas.Appraisalrating)
def update_appraisalrating(appraisal_rating_id:int,appraisalrating:schemas.AppraisalUpdate,db: Session = Depends(get_db)):
    appraisal_rating_query = db.query(models.AppraisalRating).filter_by(appraisal_rating_id=appraisal_rating_id)
    if not appraisal_rating_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    appraisal_rating_query.update(appraisalrating.dict(),synchronize_session=False)
    db.commit()
    return appraisal_rating_query.first()
