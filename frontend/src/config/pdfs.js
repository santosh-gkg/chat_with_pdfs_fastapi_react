// groq.js

// Define the base URL of your FastAPI server
import axios from 'axios';

// Function to send a query to the FastAPI server and get a response
async function processPdfs(text) {
      
  const chat_response = await axios.post('http://localhost:8000/create_db/',{rag: 'naive'});
  const response = chat_response.data.response;
  return response;
  
}





export default processPdfs;
