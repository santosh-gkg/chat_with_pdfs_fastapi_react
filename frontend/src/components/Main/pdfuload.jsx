import React, { useState } from 'react';
import './pdfupload.css'; // You'll need to create this CSS file

const PdfUploadPopup = ({ onClose, onUpload }) => {
    const [files, setFiles] = useState([]);

    const handleFileChange = (e) => {
        setFiles(Array.from(e.target.files));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onUpload(files);
    };

    return (
        <div className="popup-overlay">
            <div className="popup-content">
                <h2>Upload PDF Files</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="file"
                        accept=".pdf"
                        multiple
                        onChange={handleFileChange}
                    />
                    <div className="popup-buttons">
                        <button type="submit">Upload</button>
                        <button type="button" onClick={onClose}>Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default PdfUploadPopup;