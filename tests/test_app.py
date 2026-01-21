"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for students",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["jordan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and improve acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create visual art including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in debates and develop public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 12,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestActivitiesEndpoint:
    """Test cases for GET /activities endpoint"""
    
    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_get_activities_has_required_fields(self, client):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        
    def test_get_activities_participants_list(self, client):
        """Test that participants are returned as a list"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert isinstance(activity["participants"], list)
        assert "michael@mergington.edu" in activity["participants"]


class TestSignupEndpoint:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "signed up" in data["message"].lower()
        
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        
    def test_signup_invalid_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_signup_duplicate_student(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()


class TestUnregisterEndpoint:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "unregistered" in data["message"].lower()
        
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
        
    def test_unregister_invalid_activity(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_unregister_student_not_registered(self, client):
        """Test unregistering a student who is not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_unregister(self, client):
        """Test signing up then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Tennis Club"
        
        # Signup
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
        
    def test_multiple_signups_same_activity(self, client):
        """Test multiple students signing up for the same activity"""
        activity = "Drama Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
            
    def test_signup_multiple_activities(self, client):
        """Test a student signing up for multiple activities"""
        email = "student@mergington.edu"
        activities_to_join = ["Chess Club", "Tennis Club", "Art Studio"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        for activity in activities_to_join:
            assert email in data[activity]["participants"]
