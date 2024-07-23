import { createContext, useState, useEffect } from "react";
import runChat from "./groq";
import processPdfs from "./pdfs";
export const Context = createContext();

const ContextProvider = (props) => {
    const [input, setInput] = useState('');
    const [currentChat, setCurrentChat] = useState(null);
    const [chats, setChats] = useState([]);
    const [mobile, setMobile] = useState(false);
    const [extended, setExtended] = useState(false);
    const [filesuploaded, setFilesUploaded] = useState(false);
    const [vectordbcreated, setVectordbCreated] = useState(false);
    const [showInfoPopup, setShowInfoPopup] = useState(false);
    const [showWaitPopup, setShowWaitPopup] = useState(false);

    useEffect(() => {
        const storedChats = JSON.parse(localStorage.getItem('chats')) || [];
        setChats(storedChats);
        if (storedChats.length === 0){
            startNewChat();
        }
        else{
            setCurrentChat(storedChats[0].id);
        }
    }, []);
    
    useEffect(() => {
        localStorage.setItem('chats', JSON.stringify(chats));
    }, [chats]);

    const startNewChat = () => {
        let newid = chats.length === 0 ? 1 : chats[0].id + 1;
        const newChat = { id: newid, messages: [] };
        
        // console.log(chats[1].id);
        setChats([newChat, ...chats]);
        // console.log(chats[0].id);
        setCurrentChat(newChat.id);
        setFilesUploaded(false);
        setVectordbCreated(false);
        
    };
    const start=() => {
        
    };
    useEffect(() => {
        start();
    }, []); // Runs only once when the component mounts

    
    
    const saveChatsToLocalStorage = (updatedChats) => {
        localStorage.setItem('chats', JSON.stringify(updatedChats));
        setChats(updatedChats);
    };
    const deleteChat = (chatId) => {
        const updatedChats = chats.filter(chat => chat.id !== chatId);
       
        saveChatsToLocalStorage(updatedChats);
    };
    const sendMessage = async (message) => {
        
        setChats(prevChats =>
            prevChats.map(chat =>
                chat.id === currentChat ? { ...chat, messages: [...chat.messages, { role: 'user', content: message }] } : chat
            )
        );
        setInput('');
        
        const currentChatMessages = chats.find(chat => chat.id === currentChat)?.messages || [];
        const response = await runChat(currentChatMessages,message);
        setChats(prevChats =>
            prevChats.map(chat =>
                chat.id === currentChat ? { ...chat, messages: [...chat.messages, { role: 'assistant', content: response }] } : chat
            )
        );
    };

    
    const processUploads = async () => {
        setShowWaitPopup(true);
        const response = await processPdfs();
        setShowWaitPopup(false);
        
    };
        

    const loadChat = (chatId) => {
        setCurrentChat(chatId);
    };

    return (
        <Context.Provider value={{ input, setInput, currentChat, chats, startNewChat, sendMessage, loadChat, deleteChat,mobile,setMobile,extended,setExtended,processUploads,filesuploaded,setFilesUploaded,vectordbcreated,setVectordbCreated,showInfoPopup,setShowInfoPopup,showWaitPopup,setShowWaitPopup}}>
            {props.children}
        </Context.Provider>
    );
};

export default ContextProvider;
