from .. import models, schemas
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from starlette.responses import Response  
from fastapi.exceptions import HTTPException


router = APIRouter(prefix='/posts',tags=['Posts'])

@router.get('/',response_model=List[schemas.Post])
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()  
    return posts


@router.get('/{id}',response_model=schemas.Post)
def get_post(id:int,response:Response,db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE post_id=%s""",(str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter_by(post_id=id).first()
    print(post)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return post


@router.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post : schemas.PostCreate,db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,response:Response,db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where post_id = %s RETURNING *""",(int(id),))
    # deleted_post = cursor.fetchone()
    post = db.query(models.Post).filter_by(post_id=id)
    if not post.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
        

@router.put('/{id}',response_model=schemas.Post)
def update_post(id:int,post:schemas.PostUpdate,db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter_by(post_id=id)

    if not post_query.first():
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    post_query.update(post.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()
