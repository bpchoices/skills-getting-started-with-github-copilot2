import os
import sys
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)

from app import app, activities  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    snapshot = deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"]


def test_signup_adds_participant():
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_duplicate_rejected():
    email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant():
    email = "tempstudent@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")

    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 200

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert email not in participants


def test_unregister_missing_participant():
    email = "absent@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
