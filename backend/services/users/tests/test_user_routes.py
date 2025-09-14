import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..app.main import app
from ..app.config.database import get_db, Base
from ..app.models.user import User

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_user(setup_database):
    """Test creating a new user"""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        "bio": "Test bio"
    }
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["bio"] == user_data["bio"]
    assert "id" in data
    assert "created_at" in data

def test_get_users(setup_database):
    """Test getting list of users"""
    # Create a test user first
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    client.post("/users/", json=user_data)
    
    response = client.get("/users/")
    assert response.status_code == 200
    
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert len(data["users"]) == 1

def test_get_user_by_id(setup_database):
    """Test getting user by ID"""
    # Create a test user first
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/users/", json=user_data)
    user_id = response.json()["id"]
    
    # Get user by ID
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]

def test_get_nonexistent_user(setup_database):
    """Test getting non-existent user"""
    response = client.get("/users/999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

def test_update_user(setup_database):
    """Test updating user information"""
    # Create a test user first
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/users/", json=user_data)
    user_id = response.json()["id"]
    
    # Update user
    update_data = {
        "name": "Updated User",
        "bio": "Updated bio"
    }
    response = client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["bio"] == update_data["bio"]
    assert data["email"] == user_data["email"]  # Should remain unchanged

def test_delete_user(setup_database):
    """Test deleting a user"""
    # Create a test user first
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/users/", json=user_data)
    user_id = response.json()["id"]
    
    # Delete user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert "User deleted successfully" in response.json()["message"]
    
    # Verify user is deleted
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "users"
