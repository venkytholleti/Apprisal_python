import uuid
from starlette import status
from .. import models, schemas, oauth2
from fastapi import Depends, APIRouter, BackgroundTasks
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from fastapi.exceptions import HTTPException
import datetime
from fastapi_mail import MessageSchema,ConnectionConfig,FastMail


router = APIRouter(tags=['Manager'])

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


@router.get('/employee_list_manager',response_model=List[schemas.EmployeeListManager1])
#@router.get('/employee_list_manager')
def get_all_employees(db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    active_calendar = db.query(models.AppraisalCalendar).filter(models.AppraisalCalendar.status == schemas.Status.Active.value).first()
    if not active_calendar:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")
    #employees = db.query(models.EmployeeAppraisers,models.Appraisee.id,models.Appraisee.appraisee_id,models.Appraisee.first_name,models.Appraisee.last_name,models.Appraisee.status,models.Designation.designation_name).filter_by(calendar_id=active_calendar.calendar_id,appraiser_id=user_id.user_id).join(models.Appraisee,models.EmployeeAppraisers.appraisee_id==models.Appraisee.id).all()
    employees = db.query(models.EmployeeAppraisers,models.Appraisee).filter_by(calendar_id=active_calendar.calendar_id,appraiser_id=user_id.user_id).join(models.Appraisee,models.EmployeeAppraisers.appraisee_id==models.Appraisee.id).all()

    return employees

@router.get('/objective',response_model=List[schemas.Objective])
def get_all_objectives(db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    objective = db.query(models.Objective).filter_by(status=schemas.Status.Active.value).all()  
    return objective


#Get Objective by Id
@router.get('/objective/{id}',response_model=List[schemas.AppraiseeObjectives])
def get_appraisee_Objectives(id:int,db: Session = Depends(get_db)):
    appraisee_Objective = db.query(models.AppraiseeObjectives).filter_by(appraisee_id=id).all()
    if not appraisee_Objective:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'Data Not Found')
    return appraisee_Objective

@router.post('/objective',status_code=status.HTTP_201_CREATED)
def create_objective(objective : schemas.ObjectiveCreate,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    new_objective = models.Objective(status = 1,objective_id=str(uuid.uuid4()),created_by = user_id.user_id,modified_by = user_id.user_id,**objective.dict())
    db.add(new_objective)
    db.commit()
    db.refresh(new_objective)
    return {'Message':"Objective Created Successfully"}

@router.put('/objective',response_model = schemas.Objective)
def edit_objective(data:schemas.ObjectiveEdit,db:Session=Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    objective_record = db.query(models.Objective).filter_by(objective_id=data.objective_id).first()
    objective_record.objective_name = data.objective_name
    objective_record.objective_description = data.objective_description
    db.add(objective_record)
    db.commit()
    db.refresh(objective_record)
    return objective_record

@router.post('/assign_objectives')
def assign_objectives(background_tasks : BackgroundTasks ,data: schemas.AssignObjectivesSchema,db: Session=Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    active_calendar = db.query(models.AppraisalCalendar).filter(models.AppraisalCalendar.status == schemas.Status.Active.value).first()

    if not active_calendar:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")

    for emp_id in data.employees:
        employee = db.query(models.Appraisee).filter_by(id = emp_id).first()
        appraisal = db.query(models.EmployeeAppraisal).filter_by(appraisee_id = emp_id).first()
        if(appraisal.status == schemas.Status.Assigned.value):
            for obj in data.objectives:
                appraisee_objectives = db.query(models.AppraiseeObjectives).filter_by(appraisee_id=emp_id,objective_id=obj.objective_id,calendar_id=active_calendar.calendar_id).first()
                if not appraisee_objectives:
                    record = models.AppraiseeObjectives(appraisee_id=emp_id,objective_id=obj.objective_id,weightage=obj.weightage,calendar_id=active_calendar.calendar_id) 
                    db.add(record)
                    db.commit()
                    db.refresh(record)
                    appraisal_objectives = db.query(models.EmployeeAppraisal).filter_by(appraisee_id = emp_id).first()
                    appraisal_objectives.status = schemas.Status.ObjectivesAssgined.value
                    db.add(appraisal_objectives)
                    db.commit()
                    db.refresh(appraisal_objectives)

            
            email = employee.email_id.lower()
            message = MessageSchema(
                subject="Objectives Assigned",
                recipients=[email], 
                subtype="html"
                )
            message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {0},<br>
            <br> Objectives have been assigned to you. Please visit the website.
            <br>
            <br> Thanks,
            <br> Prutech Team.
            </b>""".format(employee.first_name +' '+ employee.last_name)
            background_tasks.add_task(fm.send_message,message)
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"objectives are already assigned")   
    return {"Message":"Objectives were assigned to employees"} 

@router.delete('/objective/{id}')
def delete_objective(id:str,db:Session=Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    print(id)
    objective_record = db.query(models.Objective).filter(models.Objective.objective_id == id).first()   
    objective_record.status = schemas.Status.InActive.value
    db.add(objective_record)
    db.commit()
    db.refresh(objective_record)
    return {"Message":"Objective Deleted Successfully"}

@router.post('/manager_rating',status_code=status.HTTP_201_CREATED)
def create_rating(rating : schemas.ManagerRating,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    appraiseeid = db.query(models.EmployeeAppraisal).filter_by(appraisee_id=rating.appraiseeid).first()
    if(appraiseeid.status == schemas.Status.SelfRatingPosted.value):    
        weightage = []
        for i in rating.rating:
            new_rating = models.AppraisalRating(type = "manager",rating = i["rating"],appraisal_objective_id = i["objectiveid"],comments = i["notes"],created_by = user_id.user_id,modified_by = user_id.user_id)
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
        appraiseeid.appraiser_total_rating = int(totalrating)
        appraiseeid.status = schemas.Status.ManagerRatingPosted.value
        db.add(appraiseeid)
        db.commit()
        db.refresh(appraiseeid)
        return {'Message':"Manager Rating posted Successfully"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"manager ratings already posted")

@router.put('/manager_rating',status_code=status.HTTP_201_CREATED)
def create_rating(rating : schemas.ManagerRating,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    appraiseeid = db.query(models.EmployeeAppraisal).filter_by(appraisee_id=rating.appraiseeid).first()
    if(appraiseeid.status == schemas.Status.DiscussionRaised.value):    
        weightage = []
        for i in rating.rating:
            new_rating = models.AppraisalRating(type = "manager",rating = i["rating"],appraisal_objective_id = i["objectiveid "],comments = i["notes"],created_by = user_id.user_id,modified_by = user_id.user_id)
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
        appraiseeid.appraiser_total_rating = int(totalrating)
        appraiseeid.status = schemas.Status.ManagerRatingPosted.value
        db.add(appraiseeid)
        db.commit()
        db.refresh(appraiseeid)
        return {'Message':"Manager Rating posted Successfully"}
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"manager ratings already posted")