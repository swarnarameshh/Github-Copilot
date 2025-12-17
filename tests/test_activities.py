import copy
from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)
# snapshot original activities to restore between tests
_original_activities = copy.deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # restore original state before each test
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_original_activities))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_original_activities))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester@example.com"

    # ensure clean start
    assert email not in app_module.activities[activity]["participants"]

    # signup should succeed
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # duplicate signup returns 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # unregister should succeed
    r3 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r3.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # unregistering again returns 400
    r4 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert r4.status_code == 400
