from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.course import Course
from app.models.paper import Paper
from app.schemas.paper import PaperCreate

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("", status_code=201)
def create_paper(payload: PaperCreate, db: Session = Depends(get_db)):
    course = db.get(Course, payload.course_id)
    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )

    paper = Paper(
        course_id=payload.course_id,
        year=payload.year,
        exam_type=payload.exam_type,
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    return {
        "id": paper.id,
        "course_id": paper.course_id,
        "year": paper.year,
        "exam_type": paper.exam_type,
    }
