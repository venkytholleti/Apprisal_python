from fastapi import FastAPI
from . import models
from .database import engine
from fastapi.middleware.cors import CORSMiddleware
from .routers import employee,hr,manager, discussion,static, objective, calendar,employee_appraisal,user_roles,appraisee_objectives,appraisee, apprisalrating,all_api, auth, department, designation

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title='Appraisal System')

origins = [

    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(posts.router)
# app.include_router(users.router)
app.include_router(auth.router)
#app.include_router(department.router)
#app.include_router(designation.router)
#app.include_router(all_api.router)
#app.include_router(apprisalrating.router)
#app.include_router(appraisee.router)
#app.include_router(appraisee_objectives.router)
#app.include_router(employee_appraisal.router)
#app.include_router(user_roles.router)
#app.include_router(calendar.router)
#app.include_router(objective.router)
#app.include_router(discussion.router)
app.include_router(static.router)
app.include_router(manager.router)
app.include_router(hr.router)
app.include_router(employee.router)

@app.get('/')
def index():
    return 'Welcome to new World'