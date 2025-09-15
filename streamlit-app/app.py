import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Source AI Dashboard",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URLS = {
    "users": "http://localhost:8001",
    "photos": "http://localhost:8002",
    "scheduler": "http://localhost:8003"
}

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None

def make_api_request(url, method="GET", data=None, headers=None):
    """Make API request with error handling"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def login_user(email, password):
    """Login user and store token"""
    url = f"{API_BASE_URLS['users']}/users/login"
    data = {"email": email, "password": password}
    
    response = make_api_request(url, "POST", data)
    if response and "access_token" in response:
        st.session_state.auth_token = response["access_token"]
        # Get user profile
        headers = {"Authorization": f"Bearer {response['access_token']}"}
        profile_url = f"{API_BASE_URLS['users']}/users/profile"
        profile = make_api_request(profile_url, headers=headers)
        if profile:
            st.session_state.user_data = profile
            st.session_state.authenticated = True
            return True
    return False

def register_user(email, password, full_name, username):
    """Register new user"""
    url = f"{API_BASE_URLS['users']}/users/register"
    data = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "username": username
    }
    
    response = make_api_request(url, "POST", data)
    if response and "id" in response:
        return True
    return False

def get_user_stats():
    """Get user statistics"""
    if not st.session_state.auth_token:
        return None
    
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
    url = f"{API_BASE_URLS['users']}/users/profile/stats"
    return make_api_request(url, headers=headers)

def get_photos():
    """Get user photos from scheduler service"""
    if not st.session_state.auth_token:
        return []
    
    # Get photos from scheduler service where they're actually stored
    url = f"{API_BASE_URLS['scheduler']}/capture/photos/{st.session_state.user_data['id']}"
    
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        photos = data.get("photos", [])
        # Transform the data to match expected format
        transformed_photos = []
        for photo in photos:
            transformed_photos.append({
                "id": photo.get("filename", ""),
                "url": photo.get("photo_url", ""),
                "title": photo.get("filename", "Untitled"),
                "created_at": photo.get("last_modified", "")
            })
        return transformed_photos
    return []

def get_schedules():
    """Get user schedules"""
    if not st.session_state.auth_token:
        return []
    
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
    url = f"{API_BASE_URLS['scheduler']}/scheduler/schedules/"
    params = {"user_id": str(st.session_state.user_data["id"])}
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    return []

def create_schedule(frequency_hours, notifications_enabled, silent_mode_enabled):
    """Create new schedule"""
    if not st.session_state.auth_token:
        return False
    
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
    url = f"{API_BASE_URLS['scheduler']}/scheduler/schedules/"
    data = {
        "user_id": str(st.session_state.user_data["id"]),
        "frequency_hours": frequency_hours,
        "notifications_enabled": notifications_enabled,
        "silent_mode_enabled": silent_mode_enabled
    }
    
    response = make_api_request(url, "POST", data, headers)
    return response is not None

def trigger_manual_capture():
    """Trigger manual photo capture"""
    if not st.session_state.auth_token:
        return False
    
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
    url = f"{API_BASE_URLS['scheduler']}/capture/capture"
    data = {"user_id": str(st.session_state.user_data["id"])}
    
    response = make_api_request(url, "POST", data, headers)
    return response is not None

# Main App
def main():
    st.title("📸 Source AI Dashboard")
    st.markdown("---")
    
    # Sidebar for authentication
    with st.sidebar:
        st.header("🔐 Authentication")
        
        if not st.session_state.authenticated:
            # Login/Register tabs
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                st.subheader("Login")
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                
                if st.button("Login", type="primary"):
                    if email and password:
                        if login_user(email, password):
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Login failed. Please check your credentials.")
                    else:
                        st.error("Please fill in all fields.")
            
            with tab2:
                st.subheader("Register")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_full_name = st.text_input("Full Name", key="reg_full_name")
                reg_username = st.text_input("Username", key="reg_username")
                
                if st.button("Register", type="primary"):
                    if reg_email and reg_password and reg_full_name and reg_username:
                        if register_user(reg_email, reg_password, reg_full_name, reg_username):
                            st.success("Registration successful! Please login.")
                        else:
                            st.error("Registration failed. Please try again.")
                    else:
                        st.error("Please fill in all fields.")
        else:
            # User info and logout
            st.success(f"Welcome, {st.session_state.user_data['name']}!")
            st.write(f"**Email:** {st.session_state.user_data['email']}")
            st.write(f"**User ID:** {st.session_state.user_data['id']}")
            
            if st.button("Logout", type="secondary"):
                st.session_state.authenticated = False
                st.session_state.user_data = None
                st.session_state.auth_token = None
                st.rerun()
    
    # Main content
    if st.session_state.authenticated:
        # Dashboard
        st.header("📊 Dashboard")
        
        # Get user stats
        stats = get_user_stats()
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="📸 Photos Captured",
                    value=stats.get("total_photos_captured", 0)
                )
            
            with col2:
                st.metric(
                    label="💰 Total Earnings",
                    value=f"${stats.get('total_earnings', 0):.2f}"
                )
            
            with col3:
                st.metric(
                    label="📈 This Month",
                    value=f"${stats.get('monthly_earnings', 0):.2f}"
                )
            
            with col4:
                st.metric(
                    label="⏰ Active Schedules",
                    value=stats.get("active_schedules", 0)
                )
        
        st.markdown("---")
        
        # Quick Actions
        st.header("⚡ Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📸 Capture Photo Now", type="primary", use_container_width=True):
                if trigger_manual_capture():
                    st.success("Photo capture initiated!")
                else:
                    st.error("Failed to trigger photo capture.")
        
        with col2:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        # Tabs for different sections
        tab1, tab2, tab3 = st.tabs(["📷 Photo Gallery", "⏰ Schedules", "⚙️ Settings"])
        
        with tab1:
            st.header("📷 Photo Gallery")
            
            photos = get_photos()
            if photos:
                st.write(f"**Total Photos:** {len(photos)}")
                
                # Display photos in a grid
                cols = st.columns(3)
                for i, photo in enumerate(photos[:9]):  # Show first 9 photos
                    with cols[i % 3]:
                        st.image(photo.get("url", ""), caption=photo.get("title", "Untitled"))
                        st.caption(f"📅 {datetime.fromisoformat(photo['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}")
            else:
                st.info("No photos found. Start capturing photos to see them here!")
        
        with tab2:
            st.header("⏰ Photo Schedules")
            
            # Create new schedule
            with st.expander("➕ Create New Schedule"):
                col1, col2 = st.columns(2)
                
                with col1:
                    frequency = st.number_input("Frequency (hours)", min_value=1, value=24)
                    notifications = st.checkbox("Enable Notifications", value=True)
                
                with col2:
                    silent_mode = st.checkbox("Silent Mode", value=False)
                
                if st.button("Create Schedule"):
                    if create_schedule(frequency, notifications, silent_mode):
                        st.success("Schedule created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create schedule.")
            
            # Display existing schedules
            schedules = get_schedules()
            if schedules:
                for schedule in schedules:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            freq_text = f"Every {schedule['frequency_hours']} hours" if schedule['frequency_hours'] < 24 else f"Every {schedule['frequency_hours']//24} days"
                            st.write(f"**{freq_text}**")
                            st.write(f"🔔 Notifications: {'On' if schedule['notifications_enabled'] else 'Off'}")
                            st.write(f"🔇 Silent Mode: {'On' if schedule['silent_mode_enabled'] else 'Off'}")
                            st.write(f"📊 Triggered: {schedule['trigger_count']} times")
                        
                        with col2:
                            status = "🟢 Active" if schedule['is_active'] else "🔴 Paused"
                            st.write(status)
                        
                        with col3:
                            if schedule['last_triggered_at']:
                                last_triggered = datetime.fromisoformat(schedule['last_triggered_at'].replace('Z', '+00:00'))
                                st.write(f"Last: {last_triggered.strftime('%m/%d %H:%M')}")
                        
                        st.markdown("---")
            else:
                st.info("No schedules found. Create a schedule to automatically capture photos!")
        
        with tab3:
            st.header("⚙️ Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📱 App Settings")
                st.write("**Version:** 1.0.0")
                st.write("**Last Updated:** Today")
                
                if st.button("🔄 Refresh All Data"):
                    st.rerun()
            
            with col2:
                st.subheader("🔧 System Status")
                
                # Check API status
                for service, url in API_BASE_URLS.items():
                    try:
                        response = requests.get(f"{url}/health", timeout=5)
                        if response.status_code == 200:
                            st.success(f"✅ {service.title()} Service")
                        else:
                            st.error(f"❌ {service.title()} Service")
                    except:
                        st.error(f"❌ {service.title()} Service")
    
    else:
        # Welcome screen for unauthenticated users
        st.markdown("""
        ## Welcome to Source AI! 📸
        
        Source AI is an automated photo capture platform that helps you:
        
        - 📸 **Automatically capture photos** on a schedule
        - 💰 **Earn money** from your photos
        - 📊 **Track your progress** with detailed analytics
        - ⏰ **Manage schedules** for optimal photo capture
        
        ### Getting Started
        
        1. **Register** a new account using the sidebar
        2. **Login** to access your dashboard
        3. **Create schedules** for automatic photo capture
        4. **Monitor your earnings** and photo collection
        
        ### Features
        
        - 🔐 **Secure Authentication** - Your data is protected
        - 📱 **Mobile-Friendly** - Access from any device
        - ⚡ **Real-time Updates** - See changes instantly
        - 📈 **Analytics Dashboard** - Track your performance
        
        **Ready to start?** Use the sidebar to register or login!
        """)
        
        # System status for unauthenticated users
        st.markdown("---")
        st.subheader("🔧 System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            try:
                response = requests.get(f"{API_BASE_URLS['users']}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Users Service")
                else:
                    st.error("❌ Users Service")
            except:
                st.error("❌ Users Service")
        
        with col2:
            try:
                response = requests.get(f"{API_BASE_URLS['photos']}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Photos Service")
                else:
                    st.error("❌ Photos Service")
            except:
                st.error("❌ Photos Service")
        
        with col3:
            try:
                response = requests.get(f"{API_BASE_URLS['scheduler']}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Scheduler Service")
                else:
                    st.error("❌ Scheduler Service")
            except:
                st.error("❌ Scheduler Service")

if __name__ == "__main__":
    main()
