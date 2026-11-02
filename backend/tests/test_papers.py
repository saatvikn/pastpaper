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


def test_create_paper_metadata(client):
    course_response = client.post(
        "/courses",
        json={"code": "OS101", "name": "Operating Systems"},
    )
    assert course_response.status_code == 201
    course_id = course_response.json()["id"]

    response = client.post(
        "/papers",
        json={
            "course_id": course_id,
            "year": 2025,
            "exam_type": "midsem",
        },
    )
    assert response.status_code == 201

    paper = response.json()
    assert isinstance(paper["id"], int)
    assert paper["course_id"] == course_id
    assert paper["year"] == 2025
    assert paper["exam_type"] == "midsem"


def test_create_paper_with_unknown_course(client):
    response = client.post(
        "/papers",
        json={
            "course_id": 999999,
            "year": 2025,
            "exam_type": "midsem",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Course not found"}


@pytest.mark.parametrize(
    "field,value",
    [
        ("course_id", 0),
        ("year", 1899),
        ("year", 2101),
        ("exam_type", "quiz"),
    ],
)
def test_create_paper_rejects_invalid_metadata(client, field, value):
    payload = {
        "course_id": 1,
        "year": 2025,
        "exam_type": "midsem",
    }
    payload[field] = value

    response = client.post("/papers", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]
