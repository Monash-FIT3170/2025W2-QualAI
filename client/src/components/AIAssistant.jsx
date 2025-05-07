import React, { useState } from 'react';
import '../assets/styles/AIAssistant.css';

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: "Hello! I'm your AI research assistant. How can I help you analyze your interview data today?"
    },
    {
      sender: 'user',
      text: "Can you identify common themes related to user experience in the latest interviews?"
    }
  ]);
  
  const [newMessage, setNewMessage] = useState('');

  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (newMessage.trim() === '') return;
    
    setMessages([
      ...messages,
      { sender: 'user', text: newMessage }
    ]);
    
    // Mock AI response - in a real app, this would be an API call
    setTimeout(() => {
      setMessages(prev => [
        ...prev,
        { 
          sender: 'ai', 
          text: "I've analyzed the interviews and found several recurring themes related to user experience. The main themes include navigation difficulties, appreciation for the interface design, and requests for additional features. Would you like me to elaborate on any specific theme?"
        }
      ]);
    }, 1000);
    
    setNewMessage('');
  };

  return (
    <div className="ai-assistant-card">
      <h2 className="card-title">AI Assistant</h2>
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`chat-message ${message.sender === 'ai' ? 'ai-message' : 'user-message'}`}
            >
              <div className="message-icon">
                <i className={message.sender === 'ai' ? 'icon-robot' : 'icon-user'}></i>
              </div>
              <div className="message-text">
                <p>{message.text}</p>
              </div>
            </div>
          ))}
        </div>
        
        <form className="chat-input" onSubmit={handleSendMessage}>
          <input
            type="text"
            placeholder="Type your question here..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">
            <i className="icon-paper-plane"></i> Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default AIAssistant;