from .. import models, schemas, oauth2
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/master/api/v1/appraisee_objective',tags=['Appraisee Objectives'])

@router.get('/',response_model=List[schemas.AppraiseeObjectives])
def get_all_appraisee_Objectives(db: Session = Depends(get_db)):
    appraisee_objectives = db.query(models.AppraiseeObjectives).all()  
    return appraisee_objectives


@router.get('/{id}',response_model=schemas.AppraiseeObjectives)
def get_appraisee_Objectives(id:int,response:Response,db: Session = Depends(get_db)):
    appraisee_Objective = db.query(models.AppraiseeObjectives).filter_by(appraisee_objective_id=id).first()
    if not appraisee_Objective:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return appraisee_Objective


@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.AppraiseeObjectives)
def create_appraisee_Objective(appraisee_Objective : schemas.AppraiseeObjectivesCreate,db: Session = Depends(get_db)):
    new_appraisee_Objective = models.AppraiseeObjectives(**appraisee_Objective.dict())
    db.add(new_appraisee_Objective)
    db.commit()
    db.refresh(new_appraisee_Objective)
    return new_appraisee_Objective

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_appraisee_Objective(id:int,response:Response,db: Session = Depends(get_db)):
    appraisee_Objective = db.query(models.AppraiseeObjectives).filter_by(appraisee_objective_id=id)
    if not appraisee_Objective.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    appraisee_Objective.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
        

@router.put('/{id}',response_model=schemas.AppraiseeObjectives)
def update_appraisee_Objective(id:int,appraisee_Objective:schemas.AppraiseeObjectivesUpdate,db: Session = Depends(get_db)):
    appraisee_Objective_query = db.query(models.AppraiseeObjectives).filter_by(appraisee_objective_id=id)
    if not appraisee_Objective_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    appraisee_Objective_query.update(appraisee_Objective.dict(),synchronize_session=False)
    db.commit()
    return appraisee_Objective_query.first()
