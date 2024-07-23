// groq.js

// Define the base URL of your FastAPI server
import axios from 'axios';

// Function to send a query to the FastAPI server and get a response
async function runChat(messages,message) {
      const newArray = messages.map((message,index) => ({
      role: message.role,
      content: message.content
  }));

  newArray.push({ role: 'user', content: message });
  const chat_response = await axios.post('http://localhost:8000/doctor/', {messages:newArray});
  const response = chat_response.data.response;
  console.log(chat_response.data);
  return response;
  
}



export default runChat;
