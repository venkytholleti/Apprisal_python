from fastapi.exceptions import HTTPException
from starlette import status
from starlette.responses import Response
from .. import models, schemas, oauth2
from fastapi import Depends, APIRouter,BackgroundTasks
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from fastapi_mail import MessageSchema,ConnectionConfig,FastMail

from sqlalchemy.orm import aliased


router = APIRouter(tags=['Employee'])


conf = ConnectionConfig(
   MAIL_USERNAME="AKIAWAI2B4CYXL2VRYZ6",
   MAIL_FROM = "support.team@prutechindia.com",
   MAIL_PASSWORD="BEaQSN7xzITlDTUdP9vzvbhns1QJnfseErX8HIljIaZW",
   MAIL_PORT=587,
   MAIL_SERVER="email-smtp.ap-south-1.amazonaws.com",
   MAIL_TLS=True,
   MAIL_SSL=False
)

fm = FastMail(conf)

@router.post('/need_discussion',status_code=status.HTTP_201_CREATED)
def create_discussion(background_tasks: BackgroundTasks,discussion : schemas.DiscussionCreate,db: Session = Depends(get_db),user:int=Depends(oauth2.get_current_user)):
    active_calendar_query = db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first()
    record = db.query(models.Role,models.UserRoles).filter(models.Role.role_name.ilike("HR")).join(models.UserRoles).first()
    if not record:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Employee Hr Does Not Exist")
    if not active_calendar_query:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")
    active_discussion = db.query(models.EmployeeAppraisal).filter_by(appraisee_id=user.user_id,calendar_id = active_calendar_query.calendar_id,status=schemas.Status.ManagerRatingPosted.value).first()
    if not active_discussion:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Already Active Discussion Exist")
    new_discussion = models.Discussion(**discussion.dict(), calendar_id = active_calendar_query.calendar_id,appraisee_id=user.user_id,created_by=user.user_id,modified_by=user.user_id,status=schemas.Status.Active.value)
    db.add(new_discussion)
    db.commit()
    db.refresh(new_discussion)
    active_discussion.status = schemas.Status.DiscussionRaised.value
    db.add(active_discussion)
    db.commit()
    db.refresh(active_discussion)

    employee = db.query(models.Appraisee).filter_by(id=user.user_id).first()
    hr = record.UserRoles.appraisee
    email = hr.email_id.lower()
    message = MessageSchema(
        subject="Discussion Raised Mail",
        recipients=[email], 
        subtype="html"
        )
    message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {0},<br>
    <br> This is mail regarding discussion raised by : {1}
    <br>
    <br>  Discussion Description: {2}</br>
    <br>
    <br> Thanks,
    <br> Prutech Team.
    </b>""".format(hr.first_name +' '+ hr.last_name,employee.first_name +' '+ employee.last_name, new_discussion.discussion_description)
    background_tasks.add_task(fm.send_message,message)
    return {"Message":"Discussion Raised Successfully"}




@router.get('/discussion-list',response_model=List[schemas.Discussion])
def get_discussion_employee_list(db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    discussion = db.query(models.Discussion).filter_by(appraisee_id=user_id.user_id).all()  
    return discussion


@router.get('/discussion-list/{id}',response_model=schemas.Discussion)
def get_discussion_info(id:int,response:Response,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    discussion = db.query(models.Discussion).filter_by(appraisee_id=id).first()
    if not discussion:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return discussion
    
@router.get('/get_employee',response_model=schemas.Appraisee)
def get_appraisee(response:Response,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    appraisee = db.query(models.Appraisee).filter_by(id=user_id.user_id).first()
    if not appraisee:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return appraisee

@router.post('/employee_discussions')
def get_employee_discussions(data:schemas.EmployeeDiscussions,db:Session=Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):

    active_calendar_query = db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first()
    if not active_calendar_query:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")

    emp_objs = db.query(models.AppraiseeObjectives,models.AppraisalRating.rating).filter_by(calendar_id=active_calendar_query.calendar_id,appraisee_id=data.employee_id).join(models.AppraisalRating,models.AppraiseeObjectives.appraisee_objective_id==models.AppraisalRating.appraisal_objective_id).all()
    return emp_objs

#Post Self Rating
@router.post('/selfrating',status_code=status.HTTP_201_CREATED)
def create_rating(rating : schemas.Rating,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    appraiseeid = db.query(models.EmployeeAppraisal).filter_by(appraisee_id=user_id.user_id).first()
    if(appraiseeid.status == schemas.Status.ObjectivesAssgined.value):    
        weightage = []
        for i in rating.rating:
            new_rating = models.AppraisalRating(type = "self",rating = i["rating"],appraisal_objective_id = i["objectiveid"],comments = i["notes"],created_by = user_id.user_id,modified_by = user_id.user_id)
            db.add(new_rating)
            db.commit()
            db.refresh(new_rating)
            que = db.query(models.AppraiseeObjectives).filter_by(appraisee_objective_id=i["objectiveid"]).first()
            weightage.append(que.weightage)
        totalrating=0
        c=0
        for i in rating.rating:
            totalrating = totalrating + (i["rating"]*weightage[c])
            c=+1
        totalrating = int(totalrating/10)
        appraiseeid.appraisee_total_rating = int(totalrating)
        appraiseeid.status = schemas.Status.SelfRatingPosted.value
        db.add(appraiseeid)
        db.commit()
        db.refresh(appraiseeid)
        return {'Message':"Rating Created Successfully"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"ratings already posted")