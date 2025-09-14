
Based on your application's requirements for a data-collection app, here are good, scalable data models using Pydantic's BaseModel for your backend APIs and a conceptual representation for the frontend and database. These models are designed to ensure data integrity, facilitate efficient data transfer, and support the modular microservices architecture you've planned.

Pydantic Data Models (Backend & APIs)

These models define the structure of data sent to and from your APIs. They provide data validation, serialization, and deserialization.

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Used for both request and response in the user service
class UserBase(BaseModel):
    name: str = Field(..., example="Alice Johnson", description="The user's full name.")
    email: str = Field(..., example="alice@example.com", description="A unique email address for the user.")
    age: int = Field(..., ge=18, le=120, description="The user's age.")
    profile_picture_url: Optional[str] = Field(None, example="https://s3.aws/avatars/alice.jpg", description="URL to the user's profile picture.")

# Response model for user data, including database-specific fields
class User(UserBase):
    user_id: str = Field(..., example="user_12345", description="A unique identifier for the user.")
    created_at: datetime = Field(..., example="2025-09-14T10:00:00Z", description="The timestamp when the user profile was created.")
    data_collection_enabled: bool = Field(False, description="Indicates if the user has enabled data collection.")
    collection_frequency_hours: Optional[int] = Field(None, ge=1, description="The frequency in hours for photo collection.")
    total_earnings: float = Field(0.0, ge=0.0, description="The total amount of money earned by the user.")
    last_photo_id: Optional[str] = Field(None, description="The ID of the last valid photo collected from this user.")

# Request model for updating user settings
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    data_collection_enabled: Optional[bool] = None
    collection_frequency_hours: Optional[int] = None

# Model for a single photo record
class Photo(BaseModel):
    photo_id: str = Field(..., example="photo_abcde", description="Unique identifier for the photo.")
    user_id: str = Field(..., example="user_12345", description="The ID of the user who uploaded the photo.")
    s3_url: str = Field(..., example="https://s3.aws/photos/user_12345/photo_abcde.jpg", description="The S3 URL where the photo is stored.")
    timestamp: datetime = Field(..., example="2025-09-14T11:00:00Z", description="The timestamp when the photo was collected.")
    is_valid: bool = Field(False, description="True if the photo contains a valid face, for monetization.")
    validation_notes: Optional[str] = Field(None, description="Notes on why the photo was deemed valid or invalid.")
    monetary_value: float = Field(0.0, ge=0.0, description="The earnings value of this specific photo.")

# Model for a photo upload request
class PhotoUploadRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user uploading the photo.")
    image_base64: str = Field(..., description="The photo data encoded in Base64.")

# Model for the data marketplace API to third-parties
class DataQuery(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    limit: int = 100
    offset: int = 0

# Response model for the data marketplace
class DataQueryResult(BaseModel):
    user_id: str = Field(..., description="Anonymized user ID for data aggregation.")
    age: int = Field(..., description="The user's age.")
    s3_url: str = Field(..., description="A secure, temporary S3 URL to the photo.")
    timestamp: datetime = Field(..., description="The timestamp of the photo.")
    
class DataQueryResponse(BaseModel):
    total_count: int
    data: List[DataQueryResult]
```


Database Models (NoSQL - Firestore/MongoDB)

The data models for the database reflect the Pydantic models but are structured for optimal storage and query performance.

Users Collection: users/{user_id}

_id: (or user_id) string, primary key.

name: string.

email: string, unique index.

age: integer.

profile_picture_url: string.

created_at: timestamp.

data_collection_enabled: boolean.

collection_frequency_hours: integer.

total_earnings: float.

last_photo_id: string.

Photos Collection: photos/{photo_id}

_id: (or photo_id) string, primary key.

user_id: string, foreign key to users collection.

s3_url: string.

timestamp: timestamp.

is_valid: boolean.

monetary_value: float.

Frontend Models

Frontend data models are conceptual, representing the structure of data retrieved from the backend to be displayed in the UI. They will be similar to the Pydantic User and Photo models but might be simplified to include only the fields needed for the user interface.

User Object: Used to display the user's profile and settings.

userId

name

age

profilePictureUrl

totalEarnings

collectionEnabled

collectionFrequency

Earnings Object: A simplified view of earnings data.

amount

isRedeemable

lastUpdate