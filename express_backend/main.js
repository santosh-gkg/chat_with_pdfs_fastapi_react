const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, '../backend/pdfs')
    },
    filename: function (req, file, cb) {
        cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname))
    }
});

const upload = multer({ storage: storage });

app.post('/upload-pdfs', upload.array('pdfs'), (req, res) => {
    res.send('PDFs uploaded successfully');
});

app.listen(5000, () => {
    console.log('Server running on port 5000');
});

// ... rest of your server code