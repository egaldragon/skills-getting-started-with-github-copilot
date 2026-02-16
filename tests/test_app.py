"""Tests for the Mergington High School Activities API"""
import pytest


def test_get_root_redirects(client):
    """Test that root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting list of all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "Soccer" in data
    assert "Art Club" in data
    
    # Verify activity structure
    basketball = data["Basketball"]
    assert "description" in basketball
    assert "schedule" in basketball
    assert "max_participants" in basketball
    assert "participants" in basketball
    assert basketball["participants"][0] == "james@mergington.edu"


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    email = "newstudent@mergington.edu"
    activity = "Basketball"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signup fails for non-existent activity"""
    email = "student@mergington.edu"
    activity = "Nonexistent Club"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_remove_participant_success(client):
    """Test successfully removing a participant"""
    email = "james@mergington.edu"
    activity = "Basketball"
    
    # Verify participant is there initially
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity]["participants"]
    
    # Remove participant
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert email in data["message"]
    
    # Verify participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity]["participants"]


def test_remove_participant_from_nonexistent_activity(client):
    """Test removing participant from non-existent activity"""
    email = "student@mergington.edu"
    activity = "Nonexistent Club"
    
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_remove_nonexistent_participant(client):
    """Test removing a participant that's not in the activity"""
    email = "notregistered@mergington.edu"
    activity = "Basketball"
    
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "Student not found in activity" in data["detail"]


def test_signup_multiple_participants(client):
    """Test multiple participants can sign up for same activity"""
    activity = "Basketball"
    emails = ["student1@mergington.edu", "student2@mergington.edu"]
    
    for email in emails:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all participants are listed
    response = client.get("/activities")
    activities = response.json()
    for email in emails:
        assert email in activities[activity]["participants"]


def test_signup_and_remove_workflow(client):
    """Test complete workflow of signup and removal"""
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    
    # Sign up
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify signup
    response = client.get("/activities")
    assert email in response.json()[activity]["participants"]
    
    # Remove
    response = client.delete(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify removal
    response = client.get("/activities")
    assert email not in response.json()[activity]["participants"]
