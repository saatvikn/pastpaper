def test_create_course_rejects_blank_code(client):
    response = client.post(
        "/courses",
        json={"code": "   ", "name": "Operating Systems"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "code"]


def test_list_courses_is_empty(client):
    response = client.get("/courses")

    assert response.status_code == 200
    assert response.json() == []


def test_create_course_is_listed(client):
    response = client.post(
        "/courses",
        json={"code": " OS101 ", "name": " Operating Systems "},
    )

    assert response.status_code == 201
    created = response.json()

    assert isinstance(created["id"], int)
    assert created["code"] == "OS101"
    assert created["name"] == "Operating Systems"

    listing = client.get("/courses")
    assert listing.status_code == 200
    assert listing.json() == [created]


def test_duplicate_course_code_returns_conflict(client):
    first = client.post(
        "/courses",
        json={"code": "OS101", "name": "Operating Systems"},
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/courses",
        json={"code": "OS101", "name": "Changed name"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json() == {"detail": "Course code already exists"}

    listing = client.get("/courses")
    assert listing.status_code == 200
    assert listing.json() == [first.json()]

    recovered = client.post(
        "/courses",
        json={"code": "OS102", "name": "Another course"},
    )
    assert recovered.status_code == 201
