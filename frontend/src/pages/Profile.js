import React, { useState, useEffect } from 'react';
import { getUserProfile, updateUserProfile } from '../services/api';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      const userData = await getUserProfile();
      setUser(userData);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      setMessage('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      setMessage('');
      
      const formData = new FormData(e.target);
      const updateData = {
        name: formData.get('name'),
        email: formData.get('email'),
        bio: formData.get('bio')
      };

      await updateUserProfile(updateData);
      await fetchUserProfile(); // Refresh the profile
      setMessage('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="text-center">Loading profile...</div>
      </div>
    );
  }

  return (
    <div>
      <h1>User Profile</h1>
      
      {message && (
        <div className={`card ${message.includes('success') ? '' : ''}`} style={{ 
          backgroundColor: message.includes('success') ? '#d4edda' : '#f8d7da',
          color: message.includes('success') ? '#155724' : '#721c24',
          border: `1px solid ${message.includes('success') ? '#c3e6cb' : '#f5c6cb'}`
        }}>
          {message}
        </div>
      )}

      <div className="card">
        <h2>Edit Profile</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Name:</label>
            <input
              type="text"
              id="name"
              name="name"
              defaultValue={user?.name || ''}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              name="email"
              defaultValue={user?.email || ''}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="bio">Bio:</label>
            <textarea
              id="bio"
              name="bio"
              rows="4"
              defaultValue={user?.bio || ''}
              placeholder="Tell us about yourself..."
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Update Profile'}
          </button>
        </form>
      </div>

      <div className="card">
        <h2>Profile Information</h2>
        <p><strong>User ID:</strong> {user?.id || 'N/A'}</p>
        <p><strong>Name:</strong> {user?.name || 'Not set'}</p>
        <p><strong>Email:</strong> {user?.email || 'Not set'}</p>
        <p><strong>Bio:</strong> {user?.bio || 'Not set'}</p>
        <p><strong>Created:</strong> {user?.created_at ? new Date(user.created_at).toLocaleString() : 'N/A'}</p>
        <p><strong>Last Updated:</strong> {user?.updated_at ? new Date(user.updated_at).toLocaleString() : 'N/A'}</p>
      </div>
    </div>
  );
};

export default Profile;
