import React, { useState, useEffect } from 'react';
import { getPhotos, uploadPhoto } from '../services/api';

const PhotoGallery = () => {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchPhotos();
  }, []);

  const fetchPhotos = async () => {
    try {
      setLoading(true);
      const photosData = await getPhotos();
      setPhotos(photosData);
    } catch (err) {
      setError('Failed to load photos');
      console.error('Error fetching photos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      await uploadPhoto(file);
      await fetchPhotos(); // Refresh the gallery
    } catch (err) {
      setError('Failed to upload photo');
      console.error('Error uploading photo:', err);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="text-center">Loading photos...</div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>Photo Gallery</h2>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      <div className="mb-2">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileUpload}
          disabled={uploading}
          style={{ marginBottom: '1rem' }}
        />
        {uploading && <p>Uploading...</p>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '1rem' }}>
        {photos.length > 0 ? (
          photos.map((photo) => (
            <div key={photo.id} style={{ border: '1px solid #ddd', borderRadius: '4px', padding: '0.5rem' }}>
              <img
                src={photo.url}
                alt={photo.title || 'Photo'}
                style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '4px' }}
              />
              <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                {photo.title || 'Untitled'}
              </p>
            </div>
          ))
        ) : (
          <p>No photos uploaded yet.</p>
        )}
      </div>
    </div>
  );
};

export default PhotoGallery;
