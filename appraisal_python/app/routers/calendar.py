from .. import models, schemas
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/calendar/api/v1',tags=['Calendar'])

@router.get('/',response_model=List[schemas.Calendar])
def get_all_calender(db: Session = Depends(get_db)):
    calendar = db.query(models.AppraisalCalendar).all()  
    return calendar


@router.get('/{id}',response_model=schemas.Calendar)
def get_calendar(id:int,response:Response,db: Session = Depends(get_db)):

    calendar = db.query(models.AppraisalCalendar).filter_by(calendar_id=id).first()
    if not calendar:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return calendar


@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.Calendar)
def create_calendar(calendar : schemas.CalendarCreate,db: Session = Depends(get_db)):
    new_calendar = models.AppraisalCalendar(**calendar.dict())
    db.add(new_calendar)
    db.commit()
    db.refresh(new_calendar)
    return new_calendar
    
        

@router.put('/{id}',response_model=schemas.Calendar)
def update_calendar(id:int,calendar:schemas.CalendarUpdate,db: Session = Depends(get_db)):
    calendar_query = db.query(models.AppraisalCalendar).filter_by(calendar_id=id)
    if not calendar_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    calendar_query.update(calendar.dict(),synchronize_session=False)
    db.commit()
    return calendar_query.first()

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar(id:int,response:Response,db: Session = Depends(get_db)):
    calendar = db.query(models.AppraisalCalendar).filter_by(calendar_id=id)
    if not calendar.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    calendar.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch('/approve_rejet/{id}',response_model=schemas.Calendar)
def approve_calendar(id:int,calendar:schemas.CalendarUpdate,db: Session = Depends(get_db)):
    calendar_query = db.query(models.AppraisalCalendar).filter_by(calendar_id=id)
    if not calendar_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    calendar_query.update(calendar.dict(),synchronize_session=False)
    db.commit()
    return calendar_query.first()

@router.patch('/differ/{id}',response_model=schemas.Calendar)
def approve_calendar(id:int,calendar:schemas.CalendarUpdate,db: Session = Depends(get_db)):
    calendar_query = db.query(models.AppraisalCalendar).filter_by(calendar_id=id)
    if not calendar_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    calendar_query.update(calendar.dict(),synchronize_session=False)
    db.commit()
    return calendar_query.first()

