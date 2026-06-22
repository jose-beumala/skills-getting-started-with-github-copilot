from fastapi.testclient import TestClient
import copy

from src.app import app, activities

client = TestClient(app)


def setup_function():
    # Preserve original activity data for each test
    setup_function.original_activities = copy.deepcopy(activities)


def teardown_function():
    # Restore original activity data after each test
    activities.clear()
    activities.update(copy.deepcopy(setup_function.original_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_names = set(activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert set(result.keys()) == expected_activity_names


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert new_email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"


def test_signup_returns_400_for_duplicate_participant():
    # Arrange
    activity_name = "Programming Class"
    duplicate_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={duplicate_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_returns_404_for_unknown_activity():
    # Arrange
    activity_name = "Nonexistent Activity"
    new_email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_deletes_existing_participant():
    # Arrange
    activity_name = "Gym Class"
    email_to_remove = activities[activity_name]["participants"][0]
    assert email_to_remove in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={email_to_remove}"
    )

    # Assert
    assert response.status_code == 200
    assert email_to_remove not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"


def test_remove_participant_returns_404_for_missing_participant():
    # Arrange
    activity_name = "Gym Class"
    missing_email = "missing@mergington.edu"
    assert missing_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={missing_email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
