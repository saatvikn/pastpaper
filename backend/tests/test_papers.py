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

    detail = client.get(f"/papers/{paper['id']}")
    assert detail.status_code == 200
    assert detail.json() == paper


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


def test_list_papers_pagination(client):
    course_response = client.post(
        "/courses",
        json={"code": "OS101", "name": "Operating Systems"},
    )
    assert course_response.status_code == 201
    course_id = course_response.json()["id"]

    created = []
    for year in (2025, 2023, 2024):
        response = client.post(
            "/papers",
            json={
                "course_id": course_id,
                "year": year,
                "exam_type": "midsem",
            },
        )
        assert response.status_code == 201
        created.append(response.json())

    first = client.get("/papers", params={"limit": 2, "offset": 0})
    assert first.status_code == 200
    assert first.json() == created[:2]

    second = client.get("/papers", params={"limit": 2, "offset": 2})
    assert second.status_code == 200
    assert second.json() == created[2:]

    empty = client.get("/papers", params={"limit": 2, "offset": 3})
    assert empty.status_code == 200
    assert empty.json() == []


def test_list_papers_is_empty(client):
    response = client.get("/papers")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ],
)
def test_list_papers_rejects_invalid_pagination(client, params):
    response = client.get("/papers", params=params)

    assert response.status_code == 422


def test_get_unknown_paper(client):
    response = client.get("/papers/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Paper not found"}


@pytest.mark.parametrize("paper_id", [0, -1, "abc"])
def test_get_paper_rejects_invalid_id(client, paper_id):
    response = client.get(f"/papers/{paper_id}")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "paper_id"]


@pytest.mark.parametrize(
    "field,constraint_name",
    [
        ("storage_key", "uq_papers_storage_key"),
        ("content_hash", "uq_papers_content_hash"),
    ],
)
def test_paper_file_metadata_is_unique(test_engine, field, constraint_name):
    with Session(test_engine) as db:
        course = Course(code="OS101", name="Operating Systems")
        db.add(course)
        db.flush()

        first_values = {
            "course_id": course.id,
            "year": 2025,
            "exam_type": "midsem",
            "storage_key": "first.pdf",
            "content_hash": "a" * 64,
        }
        db.add(Paper(**first_values))
        db.flush()

        second_values = first_values.copy()
        second_values["storage_key"] = "second.pdf"
        second_values["content_hash"] = "b" * 64
        second_values[field] = first_values[field]

        db.add(Paper(**second_values))
        with pytest.raises(IntegrityError) as error:
            db.flush()

        db.rollback()
        assert error.value.orig.diag.constraint_name == constraint_name
