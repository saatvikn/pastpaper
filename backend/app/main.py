from fastapi import FastAPI
from app.routes import courses, health

app = FastAPI()

app.include_router(health.router)
app.include_router(courses.router)
