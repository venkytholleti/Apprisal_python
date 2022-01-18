from .database import Base
from sqlalchemy import Column, Integer,String, Boolean, ForeignKey, Date
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import null, text
from sqlalchemy.orm import relationship

class BaseEntity:
	created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
	created_by = Column(String(75),nullable=True)
	modified_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
	modified_by = Column(String(75),nullable=True)
	status = Column(Integer,nullable=True,default=1)
	type = Column(String(20),nullable=True)


class Designation(Base):
	__tablename__ = 'designation'

	designation_id = Column(Integer,primary_key=True,nullable=False)
	designation_name = Column(String(75),nullable=False)
	designation_grade = Column(String(10),nullable=True)
	designation_description = Column(String(255),nullable=True)

class Department(Base):
	__tablename__ = 'department'

	department_id = Column(Integer,primary_key=True,nullable=False)
	department_name = Column(String(75),nullable=False)
	department_description = Column(String(255),nullable=True)
	
class Appraisee(Base, BaseEntity):
	__tablename__ = 'appraisee'

	id = Column(Integer,primary_key=True,nullable=False)
	appraisee_id = Column(String(12),nullable=False,unique=True)
	first_name = Column(String(75),nullable=False)
	middle_name = Column(String(75),nullable=True)
	last_name = Column(String(75),nullable=False)
	password = Column(String(75),nullable=False)
	email_id = Column(String(150),nullable=False,unique=True) 
	mobile_number = Column(String(15),nullable=False,unique=True)
	joining_date = Column(Date,nullable=False)
	location = Column(String(25),nullable=True)
	last_access_date = Column(Date,nullable=False)
	designation_id = Column(Integer,ForeignKey("designation.designation_id",ondelete="CASCADE"),nullable=False)
	department_id = Column(Integer,ForeignKey("department.department_id",ondelete="CASCADE"),nullable=False)
	department = relationship("Department")
	designation = relationship("Designation")
	

#Appraisal Calendar
class AppraisalCalendar(Base, BaseEntity):
	__tablename__ = 'appraisal_calendar'

	calendar_id = Column(Integer,primary_key=True,nullable=False)
	appraisal_term = Column(Integer,nullable=False)
	objective_set_date = Column(Date,nullable=False)
	appraisal_start_date = Column(Date,nullable=False)
	self_appraisal_end_date = Column(Date,nullable=False)
	review_end_date = Column(Date,nullable=False)
	closer_date = Column(Date,nullable=False)
	rating_scale = Column(Integer,nullable=False)
	comments = Column(String(255),nullable=True)
	qualification_criteria = Column(Integer,nullable=False)
	approved_by = Column(Integer,ForeignKey("appraisee.id",ondelete="CASCADE"),nullable=True)
	appraisee = relationship("Appraisee")

# Employee Appraisers
class EmployeeAppraisers(Base,BaseEntity):
	__tablename__ = 'employee_appraisers'
 
	id = Column(Integer,primary_key=True,nullable=False)
	appraisee_id = Column(Integer,ForeignKey("appraisee.id",ondelete="CASCADE"),nullable=False)
	appraiser_id = Column(Integer,ForeignKey("appraisee.id",ondelete="CASCADE"),nullable=False)
	calendar_id = Column(Integer,ForeignKey("appraisal_calendar.calendar_id",ondelete="CASCADE"),nullable=False)
	appraisee = relationship("Appraisee",foreign_keys="EmployeeAppraisers.appraisee_id")
	appraiser = relationship("Appraisee",foreign_keys="EmployeeAppraisers.appraiser_id")
	calendar = relationship("AppraisalCalendar")
  
#objective
class Objective(Base, BaseEntity):
	__tablename__ = 'objective'

	objective_id = Column(String(40),primary_key=True,nullable=False)
	objective_name = Column(String(75),nullable=False)
	objective_description = Column(String(255),nullable=True)


class AppraiseeObjectives(Base, BaseEntity):
	__tablename__ = 'appraisee_objectives'

	appraisee_objective_id = Column(Integer,primary_key=True,nullable=False)
	appraisee_id = Column(Integer,ForeignKey("appraisee.id",ondelete="CASCADE"),nullable=False)
	calendar_id = Column(Integer,ForeignKey("appraisal_calendar.calendar_id",ondelete="CASCADE"),nullable=False)
	objective_id = Column(String(40),ForeignKey("objective.objective_id",ondelete="CASCADE"),nullable=False)
	weightage = Column(Integer,nullable=True)
	appraisee = relationship("Appraisee")
	calendar = relationship("AppraisalCalendar")
	objective = relationship("Objective")


class AppraisalRating(Base, BaseEntity):
	__tablename__ = 'appraisal_rating'

	appraisal_rating_id = Column(Integer,primary_key=True,nullable=False)
	appraisal_objective_id = Column(Integer,ForeignKey("appraisee_objectives.appraisee_objective_id",ondelete="CASCADE"),nullable=False)
	rating = Column(Integer,nullable=False)
	comments = Column(String(255),nullable=True)
	appraisal_objective = relationship("AppraiseeObjectives")


class Discussion(Base, BaseEntity):
    __tablename__ = 'discussion'

    discussion_id = Column(Integer,primary_key=True,nullable=False)
    discussion_description = Column(String(255),nullable=False)
    appraisee_id = Column(Integer,ForeignKey("appraisee.id",ondelete="CASCADE"),nullable=False)
    calendar_id = Column(Integer,ForeignKey("appraisal_calendar.calendar_id",ondelete="CASCADE"),nullable=False)
    comments = Column(String(255),nullable=True)
    scheduled_date = Column(Date,nullable=True)
    appraisee = relationship("Appraisee")
    calendar = relationship("AppraisalCalendar")



class Authorities(Base):
	__tablename__ = 'authorities'

	authority_id = Column(Integer,primary_key=True,nullable=False)
	authority_name = Column(String(255),nullable=False)
	


class Role(Base):
	__tablename__ = 'role'

	role_id = Column(Integer,primary_key=True,nullable=False)
	role_name = Column(String(75),nullable=False)
	


class  RoleAuthorities(Base):
	__tablename__= 'role_authorities'

	role_id = Column(Integer,ForeignKey("role.role_id",ondelete="CASCADE"),nullable=False,primary_key=True)
	authority_id = Column(Integer,ForeignKey("authorities.authority_id",ondelete="CASCADE"),nullable=False,primary_key=True)
	authority = relationship("Authorities")
	role = relationship("Role")




class  UserRoles(Base,BaseEntity):
	__tablename__= 'user_roles'

	appraisee_id = Column(Integer,ForeignKey("appraisee.id",ondelete="CASCADE"),nullable=False,primary_key=True)
	role_id = Column(Integer,ForeignKey("role.role_id",ondelete="CASCADE"),nullable=False,primary_key=True)
	role = relationship("Role")
	appraisee = relationship("Appraisee")




class  EmployeeAppraisal(Base, BaseEntity):
	__tablename__= 'employee_appraisal'

	id = Column(Integer,primary_key=True,nullable=False)
	appraisee_id = Column(Integer,ForeignKey("appraisee.id",ondelete="CASCADE"),nullable=False)
	calendar_id = Column(Integer,ForeignKey("appraisal_calendar.calendar_id",ondelete="CASCADE"),nullable=False)
	appraiser_id = Column(Integer,ForeignKey("appraisee.id",ondelete="CASCADE"),nullable=False)
	appraisee_total_rating = Column(Integer,nullable=True)
	appraiser_total_rating = Column(Integer,nullable=True)
	normalized_total_rating = Column(Integer,nullable=True)
	appraisee = relationship("Appraisee",foreign_keys="EmployeeAppraisal.appraisee_id")
	calendar = relationship("AppraisalCalendar")
	appraiser = relationship("Appraisee",foreign_keys="EmployeeAppraisal.appraiser_id")
    
class PasswordMailStatus(Base):         
    __tablename__ = 'password_mail_status'

    token_id = Column(Integer, primary_key=True)
    token = Column(String(255), nullable=False)
    token_status = Column(Integer, nullable=False)    



