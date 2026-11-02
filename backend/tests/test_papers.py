import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.paper import Paper


def test_paper_rejects_unknown_course(test_engine):
    with Session(test_engine) as db:
        missing_course_id = 999999
        assert db.get(Course, missing_course_id) is None

        db.add(
            Paper(
                course_id=missing_course_id,
                year=2025,
                exam_type="midsem",
            )
        )

        with pytest.raises(IntegrityError) as error:
            db.flush()

        db.rollback()

        assert error.value.orig.diag.constraint_name == "papers_course_id_fkey"
