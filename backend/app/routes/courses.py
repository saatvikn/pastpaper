from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from sqlalchemy import select

from app.database import get_db
from app.models.course import Course
from app.schemas.course import CourseCreate

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("")
def list_courses(db: Session = Depends(get_db)):
    statement = select(Course).order_by(Course.id)
    courses = db.scalars(statement).all()

    return [
        {"id": course.id, "code": course.code, "name": course.name}
        for course in courses
    ]


@router.post("", status_code=201)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    course = Course(code=payload.code, name=payload.name)
    db.add(course)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if exc.orig.diag.constraint_name == "courses_code_key":
            raise HTTPException(
                status_code=409,
                detail="Course code already exists",
            ) from exc
        raise

    db.refresh(course)
    return {"id": course.id, "code": course.code, "name": course.name}
