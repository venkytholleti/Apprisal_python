from .. import models, schemas
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/master/api/v1/department',tags=['Department'])  

@router.get('/',response_model=List[schemas.Department])
def get_all_departments(db: Session = Depends(get_db)):
    departments = db.query(models.Department).all()  
    return departments


@router.get('/{id}',response_model=schemas.Department)
def get_department(id:int,response:Response,db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE post_id=%s""",(str(id)))
    # post = cursor.fetchone()
    department = db.query(models.Department).filter_by(department_id=id).first()
    if not department:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return department


@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.Department)
def create_post(department : schemas.DepartmentCreate,db: Session = Depends(get_db)):
    new_department = models.Department(**department.dict())
    db.add(new_department)
    db.commit()
    db.refresh(new_department)
    return new_department

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_department(id:int,response:Response,db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where post_id = %s RETURNING *""",(int(id),))
    # deleted_post = cursor.fetchone()
    department = db.query(models.Department).filter_by(department_id=id)
    if not department.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    department.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
        

@router.put('/{id}',response_model=schemas.Department)
def update_department(id:int,department:schemas.DepartmentUpdate,db: Session = Depends(get_db)):
    department_query = db.query(models.Department).filter_by(department_id=id)

    if not department_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    department_query.update(department.dict(),synchronize_session=False)
    db.commit()
    return department_query.first()
