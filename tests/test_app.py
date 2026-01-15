"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a clean state before each test"""
    from app import activities
    
    # Store original state
    original_activities = {}
    for name, details in activities.items():
        original_activities[name] = {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": details["participants"].copy()
        }
    
    yield
    
    # Restore original state
    for name in activities:
        activities[name]["participants"] = original_activities[name]["participants"].copy()


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Basketball Team" in data
        assert "Chess Club" in data
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_activities_with_existing_participants(self, client, reset_activities):
        """Test that activities with existing participants are returned correctly"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "student@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
    
    def test_participant_added_after_signup(self, client, reset_activities):
        """Test that participant is actually added after signup"""
        email = "newstudent@mergington.edu"
        activity_name = "Art Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        new_count = len(response.json()[activity_name]["participants"])
        assert new_count == initial_count + 1
        assert email in response.json()[activity_name]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_duplicate_signup(self, client, reset_activities):
        """Test that duplicate signup returns 400 error"""
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Try to sign up with an email that's already in the activity
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_with_special_characters_in_activity_name(self, client, reset_activities):
        """Test signup for activities with spaces in their names"""
        email = "test@mergington.edu"
        
        # Test with "Programming Class"
        response = client.post(
            "/activities/Programming%20Class/signup?email=" + email
        )
        assert response.status_code == 200
        
        # Verify the signup worked
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Programming Class"]["participants"]


class TestRootEndpoint:
    """Tests for the GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestDataIntegrity:
    """Tests for data integrity and consistency"""
    
    def test_max_participants_not_exceeded(self, client, reset_activities):
        """Test that we can sign up multiple students to an activity"""
        from app import activities
        
        activity_name = "Math Club"
        activity = activities[activity_name]
        initial_participants = len(activity["participants"])
        
        # Sign up new students
        for i in range(3):
            email = f"newstudent{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify participants were added
        response = client.get("/activities")
        final_participants = len(response.json()[activity_name]["participants"])
        assert final_participants == initial_participants + 3
    
    def test_participant_list_consistency(self, client, reset_activities):
        """Test that participant lists remain consistent"""
        # Sign up multiple students
        students = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu"
        ]
        
        for student in students:
            response = client.post(
                f"/activities/Drama%20Club/signup?email={student}"
            )
            assert response.status_code == 200
        
        # Verify all are in the list
        response = client.get("/activities")
        participants = response.json()["Drama Club"]["participants"]
        for student in students:
            assert student in participants
