import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile

from ..app.main import app
from ..app.config.database import get_db, Base
from ..app.models.photo import Photo

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

@pytest.fixture
def sample_image():
    """Create a sample image file for testing"""
    # Create a simple test image file
    test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        tmp.write(test_image_content)
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Cleanup
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)

def test_upload_photo(setup_database, sample_image):
    """Test photo upload"""
    with open(sample_image, 'rb') as f:
        files = {"file": ("test.png", f, "image/png")}
        data = {
            "title": "Test Photo",
            "description": "Test description",
            "user_id": 1
        }
        
        response = client.post("/photos/upload", files=files, data=data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["message"] == "Photo uploaded successfully"
        assert "photo" in data
        assert data["photo"]["title"] == "Test Photo"
        assert data["photo"]["description"] == "Test description"
        assert data["photo"]["user_id"] == 1

def test_upload_invalid_file(setup_database):
    """Test uploading non-image file"""
    with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
        tmp.write(b"not an image")
        tmp_path = tmp.name
        
        with open(tmp_path, 'rb') as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = client.post("/photos/upload", files=files)
            assert response.status_code == 400
            assert "File must be an image" in response.json()["detail"]

def test_get_photos(setup_database, sample_image):
    """Test getting list of photos"""
    # Upload a test photo first
    with open(sample_image, 'rb') as f:
        files = {"file": ("test.png", f, "image/png")}
        client.post("/photos/upload", files=files)
    
    response = client.get("/photos/")
    assert response.status_code == 200
    
    data = response.json()
    assert "photos" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert len(data["photos"]) == 1

def test_get_photo_by_id(setup_database, sample_image):
    """Test getting photo by ID"""
    # Upload a test photo first
    with open(sample_image, 'rb') as f:
        files = {"file": ("test.png", f, "image/png")}
        response = client.post("/photos/upload", files=files)
        photo_id = response.json()["photo"]["id"]
    
    # Get photo by ID
    response = client.get(f"/photos/{photo_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == photo_id
    assert "url" in data

def test_get_nonexistent_photo(setup_database):
    """Test getting non-existent photo"""
    response = client.get("/photos/999")
    assert response.status_code == 404
    assert "Photo not found" in response.json()["detail"]

def test_update_photo_metadata(setup_database, sample_image):
    """Test updating photo metadata"""
    # Upload a test photo first
    with open(sample_image, 'rb') as f:
        files = {"file": ("test.png", f, "image/png")}
        response = client.post("/photos/upload", files=files)
        photo_id = response.json()["photo"]["id"]
    
    # Update photo metadata
    update_data = {
        "title": "Updated Title",
        "description": "Updated description"
    }
    response = client.put(f"/photos/{photo_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"

def test_delete_photo(setup_database, sample_image):
    """Test deleting a photo"""
    # Upload a test photo first
    with open(sample_image, 'rb') as f:
        files = {"file": ("test.png", f, "image/png")}
        response = client.post("/photos/upload", files=files)
        photo_id = response.json()["photo"]["id"]
    
    # Delete photo
    response = client.delete(f"/photos/{photo_id}")
    assert response.status_code == 200
    assert "Photo deleted successfully" in response.json()["message"]
    
    # Verify photo is deleted
    response = client.get(f"/photos/{photo_id}")
    assert response.status_code == 404

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "photos"
