from .. import models, schemas
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/master/api/v1/designation',tags=['Designation'])

@router.get('/',response_model=List[schemas.Designation])
def get_all_designations(db: Session = Depends(get_db)):   
    designations = db.query(models.Designation).all()  
    return designations


@router.get('/{id}',response_model=schemas.Designation)
def get_designation(id:int,response:Response,db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE post_id=%s""",(str(id)))
    # post = cursor.fetchone()
    designation = db.query(models.Designation).filter_by(designation_id=id).first()
    if not designation:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return designation


@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.Designation)
def create_designation(designation : schemas.DesignationCreate,db: Session = Depends(get_db)):
    new_designation = models.Designation(**designation.dict())
    db.add(new_designation)
    db.commit()
    db.refresh(new_designation)
    return new_designation

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_designation(id:int,response:Response,db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where post_id = %s RETURNING *""",(int(id),))
    # deleted_post = cursor.fetchone()
    designation = db.query(models.Designation).filter_by(designation_id=id)
    if not designation.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    designation.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
        

@router.put('/{id}',response_model=schemas.Designation)
def update_designation(id:int,designation:schemas.DesignationUpdate,db: Session = Depends(get_db)):
    designation_query = db.query(models.Designation).filter_by(designation_id=id)
    if not designation_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    designation_query.update(designation.dict(),synchronize_session=False)
    db.commit()
    return designation_query.first()
