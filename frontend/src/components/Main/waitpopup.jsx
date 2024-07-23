import React from 'react';
import './waitpopup.css'; // You'll need to create this CSS file

const WaitPopup = ({}) => {
  return (
    <div className="wait-popup-overlay">
      <div className="wait-popup-content">
        <div className="spinner"></div>
        <h2>Chat With Pdf</h2>
        <h3>Once it is done you can chat with these pdfs</h3>
      </div>
    </div>
    
  );
};

export default WaitPopup;