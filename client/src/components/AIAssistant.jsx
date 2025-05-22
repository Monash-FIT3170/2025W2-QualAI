import React, { useState } from 'react';

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
  <div className="bg-slate-800 rounded-xl shadow-sm p-4 h-full flex flex-col">
    <h2 className="text-lg font-semibold text-white mb-4">AI Assistant</h2>
    <div className="flex flex-col flex-1 min-h-0">
      <div className="flex-1 overflow-y-auto border border-slate-700 rounded-lg bg-slate-900 p-4 mb-4 min-h-0">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`flex mb-4 ${message.sender === 'ai' ? 'items-start' : 'items-start flex-row-reverse text-right'}`}
          >
            <div className="flex-shrink-0 mx-3">
              <i className={`${message.sender === 'ai' ? 'bi bi-robot' : 'bi bi-person'}`}></i>
            </div>
            <div className={`p-3 rounded-lg max-w-[80%] ${message.sender === 'ai' ? 'bg-slate-800' : 'bg-slate-700'}`}>
              <p className="text-sm text-slate-200 m-0 leading-6">{message.text}</p>
            </div>
          </div>
        ))}
      </div>
      
      <form className="flex gap-3" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="flex-1 px-3 py-3 border border-slate-700 bg-slate-900 text-white rounded-lg focus:outline-none focus:border-indigo-600"
          placeholder="Type your question here..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
        />
        <button 
          type="submit" 
          className="flex-shrink-0 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <i className="bi bi-send mr-2"></i> Send
        </button>
      </form>
    </div>
  </div>
  );
};

export default AIAssistant;