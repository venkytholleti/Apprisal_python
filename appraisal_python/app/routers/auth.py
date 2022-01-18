from .. import models, schemas, utils, oauth2
from fastapi import FastAPI, status, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db    
from starlette.responses import Response
from fastapi.exceptions import HTTPException
from fastapi_mail import MessageSchema,ConnectionConfig,FastMail


router = APIRouter(tags=['Auth'])

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


@router.post('/login')
def login(user_cred:schemas.UserLogin,db: Session = Depends(get_db)):
    employee = db.query(models.Appraisee).filter_by(email_id=user_cred.email).first()
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND,'User Not Found')
    if not utils.verify(user_cred.password,employee.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f'Invalid Credentials')
    access_token = oauth2.create_access_token(data={"user_id":employee.id})
    active_calendar_query = db.query(models.AppraisalCalendar).filter_by(status=schemas.CalendarStatus.ActiveCalendar.value).first()
    role = db.query(models.UserRoles,models.Role.role_name).join(models.Role,models.UserRoles.role_id==models.Role.role_id).filter(models.UserRoles.appraisee_id==employee.id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Role Does Not Exist')

    department = db.query(models.Department).filter_by(department_id=employee.department_id).first().department_name
    designation = db.query(models.Designation).filter_by(designation_id=employee.designation_id).first().designation_name
    if not active_calendar_query:
        manager_first_name = ''
        manager_last_name = ''
        manager_ratings = '-'
        appraisee_ratings = '-'
    else:
        manager = db.query(models.EmployeeAppraisers,models.Appraisee.first_name,models.Appraisee.last_name).filter(models.EmployeeAppraisers.calendar_id==active_calendar_query.calendar_id,models.EmployeeAppraisers.appraisee_id==employee.id).join(models.Appraisee,models.EmployeeAppraisers.appraiser_id==models.Appraisee.id).first()
        if manager:
            manager_first_name = manager.first_name
            manager_last_name = manager.last_name
            appraisal_ratings = db.query(models.EmployeeAppraisal).filter_by(calendar_id=active_calendar_query.calendar_id,).first()
            manager_ratings = appraisal_ratings.appraiser_total_rating
            appraisee_ratings = appraisal_ratings.appraisee_total_rating

        else:
            manager_first_name = ''
            manager_last_name = ''
            manager_ratings = '-'
            appraisee_ratings = '-'

    return {"access_token":access_token, "token_type":"bearer","username":employee.email_id,"name":employee.first_name+' '+employee.last_name,"role":role.role_name,\
            "employee_first_name":employee.first_name,"employee_last_name":employee.last_name,"employee_id":employee.appraisee_id,"manager_name":manager_first_name+' '+manager_last_name,"manager_first_name":manager_first_name,\
             "manager_last_name":manager_last_name,'employee_rating':appraisee_ratings,'manager_ratings':manager_ratings,'department':department,'designation':designation,'id':employee.id}

@router.post('/reset_password')
async def forgot_password(reset_pass_data:schemas.ResetPassword,db: Session = Depends(get_db)):
    email = reset_pass_data.email.lower()
    record = db.query(models.Appraisee).filter_by(email_id=email).first()
    if record :
        name = email.split('@')[0] 
        token = oauth2.create_access_token(data={"user_id":record.id})
        reset_url = reset_pass_data.base_url + '?token=' + token
        #reset_url = reset_pass_data.base_url
        message = MessageSchema(
            subject="Reset Password Mail",
            recipients=[email],  # List of recipients, as many as you can pass  
            subtype="html"
            )
        message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {0},<br>
        <br> You received Password reset link from PRUTECH to Appraisal System Portal.
        <br>
        <br> To reset <a href={1}>click here</a></br>
        <br> Thanks,
        <br> PRUTECH Team.
        </b>""".format(name, reset_url)
        await fm.send_message(message)
        mail_validation_obj = models.PasswordMailStatus(token=token,token_status=1)
        db.add(mail_validation_obj)
        db.commit()
        db.refresh(mail_validation_obj)
        return {"message": "Password Reset Mail Sent Successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"{email} Is Not A Valid User")


@router.post('/passmailvalidation')
def PasswordMailValidation(pass_validation_data:schemas.PasswordValidation):
    if not db.query(models.PasswordMailStatus).filter_by(token=pass_validation_data.token,token_status=1).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Your Link Was Invalid/Expired")
    return {"message":"success"}
        


@router.post('/changePassword')
def change_password(password_details:schemas.PasswordChange,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    employee = db.query(models.Appraisee).filter_by(id=user_id.user_id).first()
    if not employee:
        raise HTTPException(status.HTTP_403_FORBIDDEN,'User Not Found')
    if utils.verify(password_details.new_password,employee.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f'Invalid Credentials')
    if not utils.verify(password_details.current_password, employee.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')
    employee.password = utils.hash(password_details.new_password)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return {"message":"Password Changed Successfully"}

@router.post('/change_password')
def ResetPassword(password_details:schemas.ResetPassword,user_id:int=Depends(oauth2.get_current_user)):
    employee = db.query(models.Appraisee).filter_by(id=user_id.user_id).first()
    if not employee:
        raise HTTPException(status.HTTP_403_FORBIDDEN,'User Not Found')
    employee.password = utils.hash(password_details.password)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return {"message": "Password Has Been Reset Successfully"}

