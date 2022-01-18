from .. import models, schemas
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/discussion/api/v1',tags=['Discussion'])


@router.patch('/close-discussion',response_model=schemas.Discussion)
def update_(id:int,discussion:schemas.DiscussionUpdate,db: Session = Depends(get_db)):
    discussion_query = db.query(models.Discussion).filter_by(id=id)

    if not discussion_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    discussion_query.update(discussion.dict(),synchronize_session=False)
    db.commit()
    return discussion_query.first()
