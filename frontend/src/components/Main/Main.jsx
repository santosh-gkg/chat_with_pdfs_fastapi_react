import React, { useContext, useEffect, useRef, useState } from 'react';
import './Main.css';
import { assets } from '../../assets/assets';
import { Context } from '../../config/context';
import { marked } from 'marked';
import remarkGfm from 'remark-gfm';
import PdfUploadPopup from './pdfuload'; // We'll create this component next
import InfoPopup from './infopopup';
import WaitPopup from './waitpopup';


const Main = () => {
    const { input, setInput, currentChat, chats, sendMessage, startNewChat, mobile, setMobile, extended, setExtended, processUploads,filesuploaded,setFilesUploaded,vectordbcreated,setVectordbCreated,showInfoPopup,setShowInfoPopup,showWaitPopup,setShowWaitPopup} = useContext(Context);
    const [showUploadPopup, setShowUploadPopup] = useState(false);


    // ... (keep all the existing functions)
    const handleCardClick = (text) => {
        processUploads(text);
        setVectordbCreated(true);
    };
    const isMobileDevice = () => {
        return /Mobi|Android/i.test(window.navigator.userAgent);
      };
    
      useEffect(() => {
        // Set the mobile state based on the device type
        setExtended(isMobileDevice());
        setMobile(isMobileDevice());
    
        // You can set other state variables based on the device type
      }, [setExtended,setMobile]);
    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            sendMessage(input);
        }
    };
    const resultRef = useRef(null);
    const getHtmlContent = (message) => {
        // Use marked to convert Markdown to HTML
        return marked(message, {
          gfm: true, // Enable GitHub-flavored markdown
          breaks: true // Convert line breaks to <br>
        });
      };

    const currentChatMessages = chats.find(chat => chat.id === currentChat)?.messages || [];
    useEffect(() => {
        if (resultRef.current) {
            resultRef.current.scrollTop = resultRef.current.scrollHeight;
        }
    }, [currentChatMessages]);

    

    
    const handleFileUpload = async (files) => {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('pdfs', files[i]);
        }

        try {
            const response = await fetch('http://localhost:5000/upload-pdfs', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                console.log('PDFs uploaded successfully');
                // You can add more logic here, like updating the UI or state
                

            } else {
                console.error('Failed to upload PDFs');
            }
        } catch (error) {
            console.error('Error uploading PDFs:', error);
        }
        // processUploads();
        startNewChat();
        setFilesUploaded(true);
        setShowUploadPopup(false);
    };

    return (
        <div className='main'>
            {/* ... (keep all the existing JSX) */}
            <div className="nav">
            <button type="button" onClick={() => setMobile(prev => !prev)} className="sidebar-button"><span ></span>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" >
                    <path fill="currentColor" fillRule="evenodd" d="M3 8a1 1 0 0 1 1-1h16a1 1 0 1 1 0 2H4a1 1 0 0 1-1-1m0 8a1 1 0 0 1 1-1h10a1 1 0 1 1 0 2H4a1 1 0 0 1-1-1" clipRule="evenodd">
                        
                    </path>
                </svg>
            </button>
                <p>Chat with Pdfs</p>
                <div onClick={startNewChat} className="new-chat">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" ><path d="M15.673 3.913a3.121 3.121 0 1 1 4.414 4.414l-5.937 5.937a5 5 0 0 1-2.828 1.415l-2.18.31a1 1 0 0 1-1.132-1.13l.311-2.18A5 5 0 0 1 9.736 9.85zm3 1.414a1.12 1.12 0 0 0-1.586 0l-5.937 5.937a3 3 0 0 0-.849 1.697l-.123.86.86-.122a3 3 0 0 0 1.698-.849l5.937-5.937a1.12 1.12 0 0 0 0-1.586M11 4A1 1 0 0 1 10 5c-.998 0-1.702.008-2.253.06-.54.052-.862.141-1.109.267a3 3 0 0 0-1.311 1.311c-.134.263-.226.611-.276 1.216C5.001 8.471 5 9.264 5 10.4v3.2c0 1.137 0 1.929.051 2.546.05.605.142.953.276 1.216a3 3 0 0 0 1.311 1.311c.263.134.611.226 1.216.276.617.05 1.41.051 2.546.051h3.2c1.137 0 1.929 0 2.546-.051.605-.05.953-.142 1.216-.276a3 3 0 0 0 1.311-1.311c.126-.247.215-.569.266-1.108.053-.552.06-1.256.06-2.255a1 1 0 1 1 2 .002c0 .978-.006 1.78-.069 2.442-.064.673-.192 1.27-.475 1.827a5 5 0 0 1-2.185 2.185c-.592.302-1.232.428-1.961.487C15.6 21 14.727 21 13.643 21h-3.286c-1.084 0-1.958 0-2.666-.058-.728-.06-1.369-.185-1.96-.487a5 5 0 0 1-2.186-2.185c-.302-.592-.428-1.233-.487-1.961C3 15.6 3 14.727 3 13.643v-3.286c0-1.084 0-1.958.058-2.666.06-.729.185-1.369.487-1.961A5 5 0 0 1 5.73 3.545c.556-.284 1.154-.411 1.827-.475C8.22 3.007 9.021 3 10 3A1 1 0 0 1 11 4"></path></svg>
                </div>
                
                <img src={assets.question_mark_icon} onClick={() => setShowInfoPopup(true)} alt="" />

            </div>
            <div className="main-container">
                        
                {!filesuploaded ? 
                <>
                <div className="greet">
                        <div className="upload-pdf-container">
                            <button className="upload-pdf-button" onClick={() => setShowUploadPopup(true)}>
                                <span className="upload-pdf-icon">📁</span>
                                <span className="upload-pdf-text">Click to Upload PDFs</span>
                            </button>
                        </div>
                </div>
                    
            
            </>:
            <>
            {vectordbcreated ? 
            <>
                <div id="result" ref={resultRef} className="result">
                {currentChatMessages.map((message, index) => (
                    
                    <div key={index} className={message.role === 'user' ? 'result-title' : 'result-data'}  dangerouslySetInnerHTML={{__html:getHtmlContent(message.content)}}>
                         
                        
                    </div>
                ))}

            </div>
            <div className="main-bottom">
                <div className="search-box">
                    <input
                        id="input-box"
                        onChange={(e) => setInput(e.target.value)}
                        value={input}
                        type="text"
                        placeholder="Please ask a question from the pdfs?"
                        onKeyDown={handleKeyPress}
                    />
                    <div>
                        <img id='send' onClick={() => sendMessage(input)} src={assets.send_icon} alt="" />
                        {/* <img id='mic' src={assets.gallery_icon} alt="" onClick={() => setShowUploadPopup(true)} /> */}
                    </div>
                </div>
                <p className="bottom-info">
                    Copyright@Santosh
                </p>
            </div>
            </>
            :
            <>
            <p className='rag'>Please Choose a RAG Type?</p>
            <div className="cards">
                <div onClick={() => handleCardClick("naive")} className="card">
                    <p>Simple Naive RAG</p>
                    <img src={assets.question_mark_icon} alt="" />
                </div>
                <div onClick={() => handleCardClick("parent")} className="card">
                    <p>Summary Based RAG Multi Query Retriever</p>
                    <img src={assets.glowing_bulb_icon} alt="" />
                </div>
                <div onClick={() => handleCardClick("question")} className="card">
                    <p>Question Based RAG Multi Query Retriever</p>
                    <img src={assets.brain_icon} alt="" />
                </div>
                <div onClick={() => handleCardClick("parent")} className="card">
                    <p>Parent Document Retriever Technique</p>
                    <img src={assets.bulb_icon} alt="" />
                </div>
            </div>
            </>
            }
            </>
            
                

                }
            
            </div>
            
            {showUploadPopup && (
                <PdfUploadPopup onClose={() => setShowUploadPopup(false)} onUpload={handleFileUpload} />
            )}
            {showInfoPopup && (
                <InfoPopup
                    onClose={() => setShowInfoPopup(false)}
                    title="How to use?"
                    content="This is some important information that the user needs to know."
                />
            )}
            {showWaitPopup && (
                
                <WaitPopup/>
            )}
            
        </div>
    );
};

export default Main;