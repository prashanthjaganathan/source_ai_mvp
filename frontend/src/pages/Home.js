import React from 'react';
import UserDashboard from '../components/UserDashboard';
import PhotoGallery from '../components/PhotoGallery';

const Home = () => {
  return (
    <div>
      <h1>Welcome to Source AI MVP</h1>
      <p>This is a full-stack application with microservices architecture.</p>
      
      <UserDashboard />
      <PhotoGallery />
    </div>
  );
};

export default Home;
