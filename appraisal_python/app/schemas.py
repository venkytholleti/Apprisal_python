from pydantic import BaseModel, EmailStr, validator, constr
from datetime import datetime, date
from typing import Optional,List
import enum
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Enum

class Rate(BaseModel):
    objectiveid : int
    rating : int
    notes : str
    



class Rating(BaseModel):
    rating : List[dict]
    





class ManagerRating(BaseModel):
    rating : List[dict]
    appraiseeid : int


class EmployeeDiscussions(BaseModel):
    employee_id:int

class Test(BaseModel):
    objective_id:str
    weightage: int

class AssignObjectivesSchema(BaseModel):
    employees: List[int]
    objectives: List[Test]

class ObjectiveEdit(BaseModel):
    objective_id:str
    objective_name : constr(max_length=75)
    objective_description : constr(max_length=255)

class AssignManger(BaseModel):
    emp_list : List[int]
    manager_id : int

class ScheduledDate(BaseModel):
    dispute_id : int
    scheduled_date : date

class DiscussionRaisedEmployees(BaseModel):
    id : int
    first_name : str
    last_name : str
    scheduled_date : Optional[date] = None

class EmployeeListHR(BaseModel):
    id:int
    appraisee_id:str
    first_name:str
    last_name:str
    department_id : int
    department_name : str
    designation_id : int
    designation_name : str
    status:int
    manager_first_name: Optional[str] = None
    manager_last_name: Optional[str] = None

    class Config:
        orm_mode = True

    @validator('status')
    def set_name(cls, status):
        return "Active" if status==1 else "NotAssigned" if status==5 else "Assigned"

class ManagersList(BaseModel): 
    id:int
    first_name:str
    last_name:str

    class Config:
        orm_mode = True

class Baseentity(BaseModel):
    created_by : Optional[str]
    created_at : Optional[datetime]
    modified_by : Optional[str]
    modified_at : Optional[datetime]
    type : Optional[str]

class Status(enum.Enum):
    InActive = 0
    Active = 1
    Eligible = 2
    NotEligible = 3
    Assigned = 4
    NotAssigned = 5
    Disqualified = 6
    ObjectivesAssgined = 7
    SelfRatingPosted = 8
    ManagerRatingPosted = 9
    DiscussionRaised = 10

class CalendarStatus(enum.Enum):
    InactiveCalendar = 0
    ActiveCalendar = 1
    FutureCalendar = 2


#Designation
class DesignationBase(BaseModel):
    designation_name: str
    designation_grade: Optional[str]
    designation_description: Optional[str]

class DesignationCreate(DesignationBase):
    pass

class DesignationUpdate(DesignationBase):
    pass
   
class Designation(DesignationBase):
    designation_id: int
    class Config:
        orm_mode = True

#Department
class DepartmentBase(BaseModel):
    department_name: str
    department_description: Optional[str]

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    pass
   
class Department(DepartmentBase):
    department_id: int
    class Config:
        orm_mode = True

#Appraisee
class AppraiseeBase(BaseModel):
    appraisee_id : str
    first_name: str
    middle_name: Optional[str]
    last_name : str
    email_id : EmailStr
    mobile_number :str 
    joining_date : date
    location : str
    last_access_date : date

class AppraiseeCreate(AppraiseeBase, Baseentity):
    department_id : int
    designation_id : int
    password : str

class AppraiseeUpdate(AppraiseeBase, Baseentity):
    department_id : int
    designation_id : int

class Appraisee(AppraiseeBase):
    id : int
    department: Department
    designation : Designation
    class Config:
        orm_mode = True

class HRAppraisee(BaseModel):
    appraisee_id:int
    first_name:str
    last_name:str
    designation:Designation
    status:int
    appraiser_id:Appraisee

    class Config:
        orm_mode = True

#Calendar
class CalendarBase(BaseModel):
    appraisal_term : int
    objective_set_date : date
    self_appraisal_end_date : date
    appraisal_start_date : date
    review_end_date : date
    closer_date : date
    rating_scale : int
    qualification_criteria : int
    comments : Optional[str]

class  CalendarCreate(CalendarBase, Baseentity):
    pass

class  CalendarUpdate(CalendarBase, Baseentity):
    pass

class  Calendar(CalendarBase):
    calendar_id: int
    appraisee: Appraisee     
    class Config:
        orm_mode = True

# Employee Appraisers
class EmployeeAppraiserBase(BaseModel):
    pass
    

class  EmployeeAppraiserCreate(EmployeeAppraiserBase):
    appraisee_id: int
    appraiser_id: int
    calendar_id: int

class  EmployeeAppraiserUpdate(EmployeeAppraiserBase):
    appraisee_id: int
    appraiser_id: int
    calendar_id: int

class  EmployeeAppraiser(EmployeeAppraiserBase):
    id: int
    appraisee: Appraisee 
    appraiser: Appraisee
    calendar: Calendar
    
    class Config:
        orm_mode = True

# Objective
class ObjectiveBase(BaseModel):
    
    objective_name : str
    objective_description : str    

class ObjectiveCreate(ObjectiveBase):
    pass
    

class ObjectiveUpdate(ObjectiveBase):
    pass

class Objective(ObjectiveBase,Baseentity):
    objective_id : str 

    class Config:
        orm_mode = True

#Appraisee Objectives
class AppraiseeObjectivesBase(BaseModel):
    weightage: int    

class AppraiseeObjectivesCreate(AppraiseeObjectivesBase):
    appraisee_id: int
    objective_id: str
    calendar_id: int

class AppraiseeObjectivesUpdate(AppraiseeObjectivesBase):
    appraisee_id: int
    objective_id: str
    calendar_id: int
   
class AppraiseeObjectives(AppraiseeObjectivesBase):
    appraisee_objective_id: int
    appraisee: Appraisee
    calendar: Calendar
    objective: Objective

    class Config:
        orm_mode = True

# Appraisal Rating
class AppraisalRatingBase(BaseModel):
    rating : int

class Appraisalrating_create(AppraisalRatingBase):
    appraisal_objective_id: int

class AppraisalUpdate(AppraisalRatingBase):
    appraisal_objective_id: int

class Appraisalrating(AppraisalRatingBase):
    appraisal_rating_id: int
    appraisal_objective: AppraiseeObjectives
    class Config:
        orm_mode = True

# Discussion

class DiscussionBase(BaseModel):
    discussion_description : str
    
    comments : Optional[str]


class DiscussionCreate(BaseModel):
    discussion_description : str


class DiscussionUpdate(DiscussionBase):
    appraisee_id : int
    calendar_id : int


class Discussion(DiscussionBase):
    discussion_id : int
    appraisee : Appraisee
    calendar : Calendar

    class Config:
        orm_mode = True

# Authorities

class Authorities(BaseModel):
    authority_name:str

class AuthoritiesCreate(Authorities):
    pass

class AuthoritiesOut(Authorities):
    authority_id:int

    class Config:
        orm_mode = True

# Role
class Role(BaseModel):
    role_name:str

class RoleCreate(Role):
    pass

class RoleOut(Role):
    role_id:int

    class Config:
        orm_mode = True


#Role Authorities
class RoleAuthoritiesOut(BaseModel):
    role:RoleOut
    authority: AuthoritiesOut 
    class Config:
        orm_mode = True

class RoleAuthoritiesCreate(BaseModel):
    role_id:int  
    authority_id:int

# user Roles
class UserRolesBase(BaseModel):
    pass

class UserRolesCreate(UserRolesBase):
    appraisee_id: int
    role_id : int

class UserRolesUpdate(UserRolesBase):
    appraisee_id: int
    role_id : int

   
class UserRoles(UserRolesBase):
    role: RoleOut
    appraisee: Appraisee

    class Config:
        orm_mode = True
        
 
# Employee Appraisal

class EmployeeAppraisalBase(BaseModel):
    appraisee_total_rating: int
    appraiser_total_rating: int
    normalized_total_rating: int

class EmployeeAppraisalCreate(EmployeeAppraisalBase,Baseentity):
    appraisee_id: int
    calendar_id: int
    appraiser_id: int

class EmployeeAppraisalUpdate(EmployeeAppraisalBase):
    appraisee_id: int
    calendar_id: int
    appraiser_id: int
   
class EmployeeAppraisal(EmployeeAppraisalBase):
    id: int
    appraisee : Appraisee
    calendar: Calendar
    appraiser : Appraisee 

    class Config:
        orm_mode = True

class EmployeeAppraisers(BaseModel):
    id: int
    appraisee : Appraisee
    calendar: Calendar
    appraiser : Appraisee 

    class Config:
        orm_mode = True

class AppraiseByDeptDesg(BaseModel):
    department_id:int
    designation_id:int

class AppraiseByDeptDesgOut(BaseModel):
    pass

      
class TokenData(BaseModel):
    id: Optional[str] = None

class Token(BaseModel):
    access_token:str 
    token_type:str

class TokenData(BaseModel):
    user_id: Optional[int]
       
class UserLogin(BaseModel):
    email:EmailStr
    password:str
    
class PasswordChange(BaseModel):
    current_password:str
    new_password:str

class Disqualify(BaseModel):
    appraisee_id:int

class NewOut(BaseModel):
    authority_name: str

class EmployeeListDeptDesg(BaseModel):
    department_id:int
    designation_id:int

class GetRole(BaseModel):
    employee_id:int

class DisqualifyEmp(BaseModel):
    emp_list : List[int]

class listobj(BaseModel):
    obj_list : List[str]
    emp_list : List[int]

class ResetPassword(BaseModel):
    email:EmailStr
    base_url:str

class ChangePassword(BaseModel):
    password:str

class PasswordValidation(BaseModel):
    token:str

class EmployeeListManager(BaseModel):
    id:int
    appraisee_id:str
    first_name:str
    last_name:str
    designation_name : str
    status:int

    class Config:
        orm_mode = True

    @validator('status')
    def set_name(cls, status):
        return "Active" if status==1 else "Inactive"


class EmployeeListManager1(BaseModel):
    Appraisee : Appraisee
    class Config:
        orm_mode = True

class DObjective(BaseModel):
    weightage: int
    appraisal_objective_id : int
    rating : int
    type : str
    objective_description : Optional[str] = 'NA'
    objective_name : str

    class Config:
        orm_mode=True

class DEmployee(BaseModel):
    id:int
    appraisee_id:str
    first_name: str
    last_name:str 
    designation_name:str 
    department_name:str
    class Config:
        orm_mode=True

class DDispute(BaseModel):
    description: Optional[str] = 'NA'
    dispute_id :Optional[int] = None
    class Config:
        orm_mode = True

class DisputeRaisedEmpDetails(BaseModel):
    appraisee : DEmployee
    dispute : DDispute
    total_manager_rating: Optional[int] = None
    total_appraisee_rating: Optional[int] = None
    objectives_details: List[DObjective]
    class Config:
        orm_mode=True

class EmployeeCreate(BaseModel):
    appraisee_id : constr(max_length=12)
    first_name : constr(max_length=75)
    middle_name : Optional[constr(max_length=75)]
    last_name : constr(max_length=75)
    email_id : EmailStr
    mobile_number : constr(max_length=15)
    department_id : int
    designation_id : int
    role_id : int
    joining_date : date
    location: constr(max_length=25)

class EmployeeBulkCreate(BaseModel):
    appraisee_id : constr(max_length=12)
    first_name : constr(max_length=75)
    middle_name : Optional[constr(max_length=75)]
    last_name : constr(max_length=75)
    email_id : EmailStr
    mobile_number : constr(max_length=15)
    department_name : str
    designation_name : str
    role : str
    joining_date : date
    location: constr(max_length=25)

    @validator("joining_date", pre=True)
    def parse_joining_date(cls, value):
        return datetime.strptime(value,"%d-%m-%Y").date()    

class DiscussionRaisedEmployeeObj(BaseModel):
    weightage: int
    appraisal_objective_id : int
    rating : int
    type : str
    objective_description : Optional[str] = 'NA'
    objective_name : str
    comments : Optional[str]

    class Config:
        orm_mode=True

class ObjectiveList(BaseModel):
    objective_description : Optional[str] = 'NA'
    objective_name : str
    appraisee_objective_id : int
    class Config:
        orm_mode=True

class DiscussionRaisedEmployee(BaseModel):
    id:int
    appraisee_id:str
    first_name: str
    last_name:str 
    designation_name:str 
    department_name:str
    rating_scale:int
    class Config:
        orm_mode=True

class DiscussionRaised(BaseModel):
    description: Optional[str] = 'NA'
    dispute_id :Optional[int] = None
    class Config:
        orm_mode = True

class DiscussionRaisedEmployeeData(BaseModel):
    appraisee : DiscussionRaisedEmployee
    dispute : DiscussionRaised
    total_manager_rating: Optional[int] = None
    total_appraisee_rating: Optional[int] = None
    objectives_details: List[DiscussionRaisedEmployeeObj]
    objectives: List[ObjectiveList]

    class Config:
        orm_mode=True

class EmailValidator(BaseModel):
    email_id : EmailStr
    class Config:
        orm_mode = True

class MobileValidator(BaseModel):
    mobile_number : str
    class Config:
        orm_mode = True

class AppraiseeIdValidator(BaseModel):
    appraisee_id : str
    class Config:
        orm_mode = True