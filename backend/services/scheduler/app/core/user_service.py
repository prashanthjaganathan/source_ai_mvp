# /backend/services/scheduler/app/core/user_service.py
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class UserService:
    """
    Service to interact with the Users microservice
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from users service"""
        try:
            response = await self.http_client.get(f"{self.base_url}/users/{user_id}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user {user_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def get_user_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user capture settings"""
        try:
            user = await self.get_user(user_id)
            if user:
                return {
                    "capture_frequency_hours": user.get("capture_frequency_hours", 1),
                    "notifications_enabled": user.get("notifications_enabled", True),
                    "silent_mode_enabled": user.get("silent_mode_enabled", False),
                    "max_daily_captures": user.get("max_daily_captures", 10)
                }
            return None
        except Exception as e:
            logger.error(f"Error getting user settings for {user_id}: {e}")
            return None
    
    async def update_user_stats(self, user_id: str, **stats) -> bool:
        """Update user statistics after photo capture"""
        try:
            # For now, we'll just log the stats update
            # In a real implementation, you'd make an API call to update the user
            logger.info(f"Updating stats for user {user_id}: {stats}")
            return True
        except Exception as e:
            logger.error(f"Error updating user stats for {user_id}: {e}")
            return False
    
    async def check_user_exists(self, user_id: str) -> bool:
        """Check if user exists"""
        try:
            user = await self.get_user(user_id)
            return user is not None
        except Exception as e:
            logger.error(f"Error checking if user {user_id} exists: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup user service"""
        await self.http_client.aclose()
        logger.info("User Service cleanup completed")