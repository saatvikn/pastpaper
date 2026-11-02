import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.paper import Paper
from app.models.processing_job import ProcessingJob


def create_paper_for_job(db):
    course = Course(code="OS101", name="Operating Systems")
    db.add(course)
    db.flush()

    paper = Paper(course_id=course.id, year=2025, exam_type="midsem")
    db.add(paper)
    db.flush()
    return paper


def test_job_receives_defaults(test_engine):
    with Session(test_engine) as db:
        paper = create_paper_for_job(db)
        job = ProcessingJob(paper_id=paper.id)
        db.add(job)
        db.flush()

        assert job.status == "queued"
        assert job.created_at is not None
        assert job.created_at.tzinfo is not None


def test_job_rejects_invalid_status(test_engine):
    with Session(test_engine) as db:
        paper = create_paper_for_job(db)
        db.add(ProcessingJob(paper_id=paper.id, status="banana"))

        with pytest.raises(IntegrityError) as error:
            db.flush()

        db.rollback()
        assert error.value.orig.diag.constraint_name == "ck_processing_jobs_status"
