from datetime import date, datetime
from fastapi.exceptions import HTTPException
from starlette import status
from starlette.responses import Response
from .. import models, schemas, oauth2, utils
from fastapi import Depends, APIRouter, BackgroundTasks
from sqlalchemy.orm import Session      
from ..database import get_db
from typing import List
from dateutil import relativedelta
from sqlalchemy import extract
from sqlalchemy.orm import aliased
from fastapi_mail import MessageSchema,ConnectionConfig,FastMail
from sqlalchemy import exc
import datetime

router = APIRouter(tags=['HR'])

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

class CalendarCreate:
    def create_calendar(self,calendar,calendar_status):
    

        if (datetime.date.today() > calendar.objective_set_date):
            raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'objective date must be greater than current date')
        if calendar.objective_set_date > calendar.appraisal_start_date:
           raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'objetive set date cannot be greater than appraisal start date')
        if calendar.closer_date < calendar.self_appraisal_end_date:
            raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'self appraisal end date cannot be larger than closer date')
        if calendar.self_appraisal_end_date > calendar.review_end_date:
            raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'review end date must be greater  than  self appraisal end date')
        if calendar.self_appraisal_end_date > calendar.review_end_date:
            raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'self appraisal end date cannot be larger than review end date')
        new_calendar = models.AppraisalCalendar(**calendar.dict(),status=calendar_status)
        return new_calendar

@router.get('/employee_list_hr',response_model=List[schemas.EmployeeListHR])
def get_all_employees(response:Response,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
#def get_all_employees(response:Response,db: Session = Depends(get_db)):
    qualification_criteria = db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first()
    qualification_criteria = qualification_criteria.qualification_criteria if qualification_criteria else 0
    present_day = date.today()
    employee = aliased(models.Appraisee)
    disqulaified_emp_query = db.query(models.EmployeeAppraisal).filter_by(status=schemas.Status.Disqualified.value).all()
    disqualified_employees = [i.appraisee_id for i in disqulaified_emp_query] if disqulaified_emp_query else []
    employees = db.query(models.Appraisee,models.Appraisee.id,models.Appraisee.appraisee_id,models.Appraisee.first_name,models.Appraisee.last_name,models.Appraisee.status,employee.first_name.label('manager_first_name'),employee.last_name.label('manager_last_name'),models.Department.department_id,models.Department.department_name,models.Designation.designation_id,models.Designation.designation_name).filter((((present_day.year - extract('year', models.Appraisee.joining_date)) * 12) + (present_day.month - extract('month', models.Appraisee.joining_date))) >= qualification_criteria,\
        models.Appraisee.status!=schemas.Status.InActive.value,models.Appraisee.id!=user_id.user_id,models.Appraisee.id.notin_(disqualified_employees)).join(models.Department,models.Appraisee.department_id==models.Department.department_id).join(models.Designation,models.Appraisee.designation_id==models.Designation.designation_id).join(models.EmployeeAppraisers,models.EmployeeAppraisers.appraisee_id == models.Appraisee.id,isouter=True)\
        .join(employee,models.EmployeeAppraisers.appraiser_id == employee.id,isouter=True).all()
    return employees

@router.get('/managers_list', response_model=List[schemas.ManagersList])
def get_all_managers(response:Response, db: Session = Depends(get_db)):
    role = db.query(models.Role).filter_by(role_name = 'Manager').first()
    if not role:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Role Manager Does Not Exist")
    managers = db.query(models.UserRoles,models.Appraisee.id,models.Appraisee.first_name,models.Appraisee.last_name).filter_by(role_id = role.role_id).join(models.Appraisee,models.UserRoles.appraisee_id == models.Appraisee.id).filter(models.Appraisee.status!=schemas.Status.InActive.value).all()
    return managers

@router.get('/discussion_raised_emp',response_model = List[schemas.DiscussionRaisedEmployees])
def discussion_raised_employees_list(db :Session=Depends(get_db)):
    active_calendar_query = db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first()
    if not active_calendar_query:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")
    
    emp = db.query(models.Discussion,models.Appraisee.id,models.Appraisee.first_name,models.Appraisee.last_name,models.Discussion.scheduled_date).filter_by(calendar_id=active_calendar_query.calendar_id).join(models.Appraisee,models.Discussion.appraisee_id==models.Appraisee.id).all()
    return emp

@router.post('/employee')
def create_employee(background_tasks: BackgroundTasks,employee : schemas.EmployeeCreate,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    try: 
        emp_dict = employee.__dict__
        role_id = employee.role_id
        employee.email_id = employee.email_id.lower()
        emp_dict.pop('role_id')
        password = utils.generate_password(8)
        hashed_password = utils.hash(password)
        new_employee = models.Appraisee(**emp_dict,password=hashed_password,created_by=user_id.user_id,modified_by=user_id.user_id,last_access_date=date.today())
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        user_role = models.UserRoles(role_id=role_id,appraisee_id=new_employee.id)
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        
        email = employee.email_id.lower()
        message = MessageSchema(
            subject="Registration Success Mail",
            recipients=[email], 
            subtype="html"
            )
        message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {0},<br>
        <br> Please Use These Credentials To Access Appraisal System Portal.
        <br>
        <br> Email : {1}</br>
        <br> Password : {2} </br>
        <br> Login TO <a href={3}>click here</a></br>
        <br> Thanks,
        <br> Prutech Team.
        </b>""".format(employee.first_name +' '+ employee.last_name, email, password, 'http://192.168.0.140:8000/login')
        background_tasks.add_task(fm.send_message,message)
        return {"Message":"Emmployee Created Successfully"}
    except exc.ProgrammingError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")
    except exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")
    except Exception as e:
        raise  HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")
    finally :
        db.close()

class CalendarUpdate:
    def update_calendar(self,calendar):

        if (datetime.date.today() > calendar.objective_set_date):
            raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'objective date must be greater than current date')
        if calendar.objective_set_date > calendar.appraisal_start_date:
           raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'objetive set date cannot be greater than appraisal start date')
        if calendar.closer_date < calendar.self_appraisal_end_date:
            raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'self appraisal end date cannot be larger than closer date')
        if calendar.closer_date < calendar.review_end_date:
            raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'review end date cannot be larger than closer date')
        if calendar.self_appraisal_end_date > calendar.review_end_date:
            raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'self appraisal end date cannot be larger than review end date')
        return calendar

@router.put('/calendar_update',status_code=status.HTTP_201_CREATED)
def update_calendar(calendar_schema : schemas.CalendarCreate,db: Session = Depends(get_db)):
    
    cals=CalendarUpdate()
    update_calendar =cals.update_calendar(calendar_schema)
    calendar = db.query(models.AppraisalCalendar).filter_by(status=schemas.CalendarStatus.ActiveCalendar.value).first()
    # if calendar.appraisal_start_date >= datetime.datetime.now():
    #    raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'calendar cannot edit after appraisal start date ')
    if calendar:
        calendar.appraisal_term = calendar_schema.appraisal_term
        calendar.objective_set_date = calendar_schema.objective_set_date
        calendar.self_appraisal_end_date = calendar_schema.self_appraisal_end_date
        calendar.appraisal_start_date = calendar_schema.appraisal_start_date
        calendar.review_end_date = calendar_schema.review_end_date
        calendar.closer_date = calendar_schema.closer_date
        calendar.rating_scale = calendar_schema.rating_scale
        calendar.qualification_criteria = calendar_schema.qualification_criteria
        calendar.comments = calendar_schema.comments
        
        db.add(calendar)
        db.commit()
        db.refresh(calendar)
        return {"Message":"Calendar updated Successfully"}


@router.post('/calendar',status_code=status.HTTP_201_CREATED)
def create_calendar(calendar_schema : schemas.CalendarCreate,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    try:
        calendar = db.query(models.AppraisalCalendar).filter_by(status=schemas.CalendarStatus.ActiveCalendar.value).first()
        cal_obj = CalendarCreate()
        calendar_status = 1
        if calendar:
            if calendar.appraisal_term == 12:
                raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'calendar already exists')
            
            elif calendar.appraisal_term ==6:
                future = db.query(models.AppraisalCalendar).filter_by(status=2).all()
                if future:
                    raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'future 6 months calendar already exists')
                else:
                    calendar_status = 2
            else:
                future = db.query(models.AppraisalCalendar).filter_by(status=2).all()
                if (len(future) >= 3):
                   raise HTTPException(status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,f'three future calendar already exists')
                else:
                    calendar_status = 2

        new_calendar = cal_obj.create_calendar(calendar_schema,calendar_status, user_id.user_id)
        db.add(new_calendar)
        db.commit()
        db.refresh(new_calendar)
        return {"Message":"Calendar Created Successfully"}
    except exc.ProgrammingError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")
    except exc.IntegrityError as e:
        db.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")
    except Exception as e:
        raise  HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e}")
    finally :
        db.close()

@router.post('/bulk_upload')
def employee_bulk_upload(background_tasks: BackgroundTasks,employees : List[schemas.EmployeeBulkCreate],db : Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    all_mobile_numbers = []
    all_email_id = []
    all_employee_id =[]
    for employee in employees:
        role_query = db.query(models.Role).filter_by(role_name=employee.role.strip()).first()
        if not role_query:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Role {employee.role} Does Not Exist")
        designation = db.query(models.Designation).filter_by(designation_name=employee.designation_name.strip()).first()
        if not designation:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Designation {employee.designation_name} Does Not Exist")
        department = db.query(models.Department).filter_by(department_name=employee.department_name.strip()).first()
        if not department:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Department {employee.department_name} Does Not Exist") 
        emp_email = db.query(models.Appraisee).filter_by(email_id=employee.email_id).first()
        if emp_email:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Employee already exists with {employee.email_id} email")
        emp_mbl = db.query(models.Appraisee).filter_by(mobile_number=employee.mobile_number).first()
        if emp_mbl:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Mobile number {employee.mobile_number} already exists")  
        emp_id = db.query(models.Appraisee).filter_by(appraisee_id=employee.appraisee_id).first()
        if emp_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Employee Id {employee.appraisee_id} already exists")        
        employee.role = role_query.role_id
        employee.designation_name = designation.designation_id
        employee.department_name = department.department_id
        all_email_id.append(employee.email_id)
        all_mobile_numbers.append(employee.mobile_number)
        all_employee_id.append(employee.appraisee_id)
    if len(all_mobile_numbers) != len(set(all_mobile_numbers)):
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Multiple employees cannot have same mobile number") 
    if len(all_email_id) != len(set(all_email_id)):
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Multiple employees cannot have same email_id") 
    if len(all_employee_id) != len(set(all_employee_id)):
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Multiple employees cannot have same employee_id") 
    for employee in employees:
        try:
            emp_dict = employee.__dict__
            emp_dict['email_id'] = emp_dict['email_id'].lower()
            role_id = emp_dict['role']
            emp_dict['department_id'] = emp_dict['department_name']
            emp_dict['designation_id'] = emp_dict['designation_name']
            emp_dict.pop('department_name')
            emp_dict.pop('designation_name')
            emp_dict.pop('role')
            password = utils.generate_password(8)
            hashed_password = utils.hash(password)
            new_employee = models.Appraisee(**emp_dict,password=hashed_password,created_by=user_id.user_id,modified_by=user_id.user_id,last_access_date=date.today(),status=schemas.Status.NotAssigned.value)
            db.add(new_employee)
            db.commit()
            db.refresh(new_employee)
            user_role = models.UserRoles(role_id=role_id,appraisee_id=new_employee.id)
            db.add(user_role)
            db.commit()
            db.refresh(user_role)
            email = employee.email_id.lower()
            message = MessageSchema(
                subject="Registration Success Mail",
                recipients=[email], 
                subtype="html"
                )
            message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {0},<br>
            <br> Please Use These Credentials To Access Appraisal System Portal.
            <br>
            <br> Email : {1}</br>
            <br> Password : {2} </br>
            <br> Login TO <a href={3}>click here</a></br>
            <br> Thanks,
            <br> Prutech Team.
            </b>""".format(employee.first_name +' '+ employee.last_name, email, password, 'http://192.168.0.140:8000/login')
            background_tasks.add_task(fm.send_message,message)
        except exc.ProgrammingError as e:
            db.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")
        except exc.IntegrityError as e:
            db.rollback()
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")
        except Exception as e:
            print(e)
            raise  HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e}")
        finally :
            db.close()
    return {"Message":"Emmployees Created Successfully"}
	
@router.post('/scheduled_date')  
def scheduled_date(background_tasks : BackgroundTasks , data : schemas.ScheduledDate, db : Session = Depends(get_db)):
    try:
        record = db.query(models.Discussion).filter_by(discussion_id = data.dispute_id,status=schemas.Status.Active.value).first()
        if not record:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Discussion Does Not Exist/not Active")
        employee = db.query(models.Appraisee).filter_by(id = record.appraisee_id).first()
        record.scheduled_date = data.scheduled_date
        record.status=schemas.Status.InActive.value
        db.add(record)
        db.commit()
        db.refresh(record)
        email = employee.email_id.lower()
        message = MessageSchema(
            subject="Scheduled Date Set Mail",
            recipients=[email], 
            subtype="html"
            )
        message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {0},<br>
        <br> Your discussion is scheduled at {1}.
        <br>
        <br> Please try to attend for the discussion.</br>
        <br> Thanks,
        <br> Prutech Team.
        </b>""".format(employee.first_name +' '+ employee.last_name, record.scheduled_date)
        background_tasks.add_task(fm.send_message,message)
        return {"Message": "Scheduled Date is Successfully Set"}
    except Exception as e:
        raise  HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")
    finally :
        db.close()


@router.put('/disqualify')
def create_appraisee_Objective(disqualified_emp : schemas.DisqualifyEmp,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    try:
        active_calendar_query = db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first()
        if not active_calendar_query:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")
        for emp_id in disqualified_emp.emp_list:
            employee = db.query(models.EmployeeAppraisal).filter_by(appraisee_id=emp_id,calendar_id=active_calendar_query.calendar_id).first()
            employee.status = schemas.Status.Disqualified.value
            employee.modified_by = user_id.user_id
            employee.modified_at = datetime.datetime.now() 
            db.add(employee)
            db.commit()
            db.refresh(employee)
        return {"Message":"Employees Successfully Disqualified"}
    except Exception as e:
        raise  HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e}")
    finally :
        db.close()

@router.post('/assign_manager')
def assign_manager(background_tasks : BackgroundTasks ,data : schemas.AssignManger,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
    active_calendar_query = db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first()
    
    if data.manager_id in data.emp_list :
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Manager cannot be assaign to himself")
    if not active_calendar_query:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")
    manager= db.query(models.Appraisee).filter_by(id=data.manager_id).first()
    manager1=db.query(models.UserRoles).filter_by(appraisee_id=data.manager_id,role_id=2).first()
    if  manager1:
        for emp_id in data.emp_list:
            employee = db.query(models.Appraisee).filter_by(id = emp_id).first()
            emp_record = db.query(models.EmployeeAppraisers).filter_by(calendar_id=active_calendar_query.calendar_id,appraisee_id=emp_id).first()
            
            if emp_record:
                emp_record.appraiser_id = data.manager_id 
                emp_record.modified_by = user_id.user_id
                emp_record.modified_at = datetime.datetime.now() 
                db.add(emp_record)
                db.commit()
                db.refresh(emp_record)
                emp_app_record = db.query(models.EmployeeAppraisal).filter_by(calendar_id=active_calendar_query.calendar_id,appraisee_id=emp_id).first()
                emp_app_record.appraiser_id = data.manager_id
                emp_app_record.modified_by = user_id.user_id
                emp_app_record.modified_at = datetime.datetime.now()
                db.add(emp_app_record)
                db.commit()
                db.refresh(emp_app_record)
                email = employee.email_id.lower()
                message = MessageSchema(
                subject="Assigning Manager Mail",
                recipients=[email], 
                subtype="html"
                    )
                message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {0},<br>
                <br> You have assigned to manager {1}
                <br>
                <br> Thanks,
                <br> Prutech Team.
                </b>""".format(employee.first_name +' '+ employee.last_name,manager.first_name +' '+ manager.last_name)
                background_tasks.add_task(fm.send_message,message)

                email = manager.email_id.lower()
                message = MessageSchema(
                subject="Assigning employee to  manager mail",
                recipients=[email], 
                subtype="html"
                    )
                message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {1},<br>
                <br> Employee {0} has assinged to you 
                <br>
                <br> Thanks,
                <br> Prutech Team.
                </b>""".format(employee.first_name +' '+ employee.last_name,manager.first_name +' '+ manager.last_name)
                background_tasks.add_task(fm.send_message,message)

            else:
                record = models.EmployeeAppraisers(calendar_id=active_calendar_query.calendar_id,appraisee_id=emp_id,appraiser_id=data.manager_id,\
                                            created_by=user_id.user_id,modified_by=user_id.user_id)
                db.add(record)
                db.commit()
                db.refresh(record)
                emp_appraisal_record = models.EmployeeAppraisal(calendar_id=active_calendar_query.calendar_id,appraisee_id=emp_id,appraiser_id=data.manager_id,created_by=user_id.user_id,modified_by=user_id.user_id,status=schemas.Status.Assigned.value)
                db.add(emp_appraisal_record)
                db.commit()
                db.refresh(emp_appraisal_record)
                emp_record = db.query(models.Appraisee).filter_by(id=emp_id).first()
                emp_record.status = schemas.Status.Assigned.value
                db.add(emp_record)
                db.commit()
                db.refresh(emp_record)
                email = employee.email_id.lower()
                message = MessageSchema(
                subject="Assigning Manager Mail",
                recipients=[email], 
                subtype="html"
                    )
                message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {0},<br>
                <br> You have assigned to manager {1}
                <br>
                <br> Thanks,
                <br> Prutech Team.
                </b>""".format(employee.first_name +' '+ employee.last_name,manager.first_name +' '+ manager.last_name)
                background_tasks.add_task(fm.send_message,message)

                email = manager.email_id.lower()
                message = MessageSchema(
                subject="Assigning employee to  manager mail",
                recipients=[email], 
                subtype="html"
                    )
                message.html = """<b style = "font-family:calibri,garamond,serif;font-size:16px;"> Hi {1},<br>
                <br> Employee {0} has assinged to you 
                <br>
                <br> Thanks,
                <br> Prutech Team.
                </b>""".format(employee.first_name +' '+ employee.last_name,manager.first_name +' '+ manager.last_name)
                background_tasks.add_task(fm.send_message,message)
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"manager does not exist")
    return {"Message":"Employees successfully assigned to manager"}

    
@router.get('/active_calendar')
def get_active_calendar(db: Session=Depends(get_db)):
    active_calendar = db.query(models.AppraisalCalendar).filter_by(status=schemas.CalendarStatus.ActiveCalendar.value).first()
    if not active_calendar:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")
    return active_calendar


#Get Employees by department
@router.get('/employee_list/{department_id}',response_model=List[schemas.EmployeeListHR])
def get_all_employees(department_id:int,response:Response,db: Session = Depends(get_db),user_id:int=Depends(oauth2.get_current_user)):
#def get_all_employees(response:Response,db: Session = Depends(get_db)):
    try:
        qualification_criteria = db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first()
        qualification_criteria = qualification_criteria.qualification_criteria if qualification_criteria else 0
        present_day = date.today()
        employee = aliased(models.Appraisee)
        disqulaified_emp_query = db.query(models.EmployeeAppraisal).filter_by(status=schemas.Status.Disqualified.value).all()
        disqualified_employees = [i.appraisee_id for i in disqulaified_emp_query] if disqulaified_emp_query else []
        employees = db.query(models.Appraisee,models.Appraisee.id,models.Appraisee.appraisee_id,models.Appraisee.first_name,models.Appraisee.last_name,models.Appraisee.status,employee.first_name.label('manager_first_name'),employee.last_name.label('manager_last_name'),models.Department.department_id,models.Department.department_name,models.Designation.designation_id,models.Designation.designation_name).filter((((present_day.year - extract('year', models.Appraisee.joining_date)) * 12) + (present_day.month - extract('month', models.Appraisee.joining_date))) >= qualification_criteria,\
            models.Appraisee.status!=schemas.Status.InActive.value,models.Appraisee.id!=user_id.user_id,models.Appraisee.id.notin_(disqualified_employees),models.Appraisee.department_id == department_id).join(models.Department,models.Appraisee.department_id==models.Department.department_id).join(models.Designation,models.Appraisee.designation_id==models.Designation.designation_id).join(models.EmployeeAppraisers,models.EmployeeAppraisers.appraisee_id == models.Appraisee.id,isouter=True)\
            .join(employee,models.EmployeeAppraisers.appraiser_id == employee.id,isouter=True).all()
        return employees
    except Exception as e:
        raise  HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,f"{e.orig}")

@router.get('/employee/{employee_id}',response_model =schemas.DiscussionRaisedEmployeeData)
def get_list_of_appraisees(employee_id:int,response:Response,db: Session = Depends(get_db)):

    active_calendar_query = db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first()
    if not active_calendar_query:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Active Calendar Does Not Exist")

    employee = db.query(models.Appraisee).filter_by(id=employee_id).first()
    if not employee:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Employee Does Not Exist")

    discussion = db.query(models.Discussion).filter_by(calendar_id=active_calendar_query.calendar_id,appraisee_id=employee.id).first()   

    appraisal_ratings = db.query(models.EmployeeAppraisal).filter_by(appraisee_id=employee.id,calendar_id=active_calendar_query.calendar_id).first()

    objective = db.query(models.AppraiseeObjectives).filter_by(appraisee_id = employee.id).join(models.Objective,models.AppraiseeObjectives.objective_id==models.Objective.objective_id).add_columns(models.AppraiseeObjectives.appraisee_objective_id,models.Objective.objective_description,models.Objective.objective_name).all()
    
    objectives = db.query(models.AppraiseeObjectives).filter_by(appraisee_id=employee.id,calendar_id=active_calendar_query.calendar_id).join(models.AppraisalRating,models.AppraiseeObjectives.appraisee_objective_id==models.AppraisalRating.appraisal_objective_id)\
        .join(models.Objective,models.AppraiseeObjectives.objective_id==models.Objective.objective_id).\
            add_columns(models.AppraiseeObjectives.weightage,models.AppraisalRating.appraisal_objective_id,models.AppraisalRating.rating,models.AppraisalRating.type\
                ,models.AppraisalRating.appraisal_objective_id,models.AppraisalRating.comments,models.Objective.objective_description,models.Objective.objective_name).all()
    
 
    return {'appraisee':{
    'id' : employee.id,
    'appraisee_id' : employee.appraisee_id,
    'first_name' : employee.first_name,
    'last_name' : employee.last_name,
    'rating_scale' : db.query(models.AppraisalCalendar).filter_by(status=schemas.Status.Active.value).first().rating_scale,
    'designation_name': db.query(models.Designation).filter_by(designation_id=employee.designation_id).first().designation_name,
    'department_name': db.query(models.Department).filter_by(department_id=employee.department_id).first().department_name},
    'dispute' : { 'description':discussion.discussion_description if discussion else 'NA', 'dispute_id': discussion.discussion_id if discussion else None},
    'total_manager_rating': appraisal_ratings.appraiser_total_rating if appraisal_ratings else 0,
    'total_appraisee_rating': appraisal_ratings.appraisee_total_rating if appraisal_ratings else 0,
    'objectives': objective,
    'objectives_details':objectives,
      }    

@router.post('/email_validation',status_code=status.HTTP_201_CREATED)
def create_email_id_validation(appraisee: schemas.EmailValidator, db: Session = Depends(get_db)):
    mail = db.query(models.Appraisee).filter_by(email_id = appraisee.email_id).first()
    if mail:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Appraisee email id is already exist")
    else:
        raise HTTPException(status.HTTP_200_OK,f"success")

@router.post('/mobile_num_validation',status_code=status.HTTP_201_CREATED)
def create_mobile_validation(appraisee: schemas.MobileValidator, db: Session = Depends(get_db)):
    mobile = db.query(models.Appraisee).filter_by(mobile_number = appraisee.mobile_number).first()
    if mobile:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Appraisee mobile number id is already exist")
    else:
        raise HTTPException(status.HTTP_200_OK,f"success")

    
@router.post('/appraiseeid_validation',status_code=status.HTTP_201_CREATED)
def create_appraiseeid_validation(appraisee: schemas.AppraiseeIdValidator, db: Session = Depends(get_db)):
    appraisee_id = db.query(models.Appraisee).filter_by(appraisee_id = appraisee.appraisee_id).first()
    if appraisee_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN,f"Appraisee id is already exist")
    else:
        raise HTTPException(status.HTTP_200_OK,f"success")

@router.get('/dashboard_managers_list')
def get_all_managers(response:Response, db: Session = Depends(get_db)):
    role = db.query(models.Role).filter_by(role_name = 'Manager').first()
    if not role:
        raise HTTPException(status.HTTP_403_FORBIDDEN,f"Role Manager Does Not Exist")
    managers = db.query(models.UserRoles,models.Appraisee.id,models.Appraisee.first_name,models.Appraisee.last_name).filter_by(role_id = role.role_id).join(models.Appraisee,models.UserRoles.appraisee_id == models.Appraisee.id).filter(models.Appraisee.status!=schemas.Status.InActive.value).all()
    
    employees = []
    for i in managers :
        assigned_emp = db.query(models.EmployeeAppraisers).filter_by(appraiser_id = i.id).all()
    
        employees.append({"name":i.first_name +" "+i.last_name, "assignedEmp" : len(assigned_emp)})
    return employees
