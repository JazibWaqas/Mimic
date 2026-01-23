import React from 'react';
import { FiLoader } from 'react-icons/fi';
import '../styles/PageLoader.css';

const PageLoader = () => {
  return (
    <div className="page-loader-container">
      <FiLoader className="spinner-icon" />
      <p>Loading Page...</p>
    </div>
  );
};

export default PageLoader; 