import React from 'react';
import './infopopup.css'; // You'll need to create this CSS file

const InfoPopup = ({ onClose, title, content }) => {
  return (
    <div className="info-popup-overlay">
      <div className="info-popup-content">
        <h2>Chat With Pdf</h2>
        {/* steps to use  */}
        <div className="info-content">
          <p>1. Click on the 'Upload PDF'.</p>
          <p>2. You can select one or more pdf files to chat with.</p>
          <p>3. Choose a RAG model.</p>
          <p>4. Start chatting with the your pdfs.</p>
        </div>
    

        {/* <div className="info-content">{content}</div> */}
        <div className="info-popup-buttons">
          <button type="button" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default InfoPopup;