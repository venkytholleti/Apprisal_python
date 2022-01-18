from .. import models, schemas
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException
import uuid


router = APIRouter(prefix='/objective',tags=['Objectives'])




@router.get('/{id}',response_model=schemas.Objective)
def get_objective(id:str,response:Response,db: Session = Depends(get_db)):
    objective= db.query(models.Objective).filter_by(objective_id=id).first()
    if not objective:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return objective

# @router.get('bycalendarid/{id}',response_model=schemas.Objective)
# def get_objective(id:str,response:Response,db: Session = Depends(get_db)):
#     objective= db.query(models.Objective).filter_by(calendar_id=id).first()
#     if not objective:
#         raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
#     return objective




@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_objective(id:str,response:Response,db: Session = Depends(get_db)):
    
    objective = db.query(models.Objective).filter_by(objective_id=id)
    if not objective.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    objective.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
        

@router.put('/{id}',response_model=schemas.Objective)
def update_objective(id:str,objective:schemas.ObjectiveUpdate,db: Session = Depends(get_db)):
    objective_query = db.query(models.Objective).filter_by(objective_id=id)
    if not objective_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    objective_query.update(objective.dict(),synchronize_session=False)
    db.commit()
    return objective_query.first()