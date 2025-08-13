import React, { useState,useEffect,useRef  } from 'react';
/**
 * AI Assistant chat component for research analysis
 * Provides interactive chat interface between user and AI assistant
 */
const AIAssistant = () => {
  // State for chat messages with initial conversation
  const [messages, setMessages] = useState([
    {
      sender: 'ai', 
      text: "Hello! I'm your AI research assistant. How can I help you analyze your interview data today?"
    },
    // {
    //   sender: 'user',
    //   text: "Can you identify common themes related to user experience in the latest interviews?"
    // }
  ]);
  
  const [newMessage, setNewMessage] = useState('');
  const [mode, setMode] = useState('offline');
  const messagesEndRef = useRef(null);
  // scroll to bottom of chat when there is a new message 
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth'});}, [messages]);

  /**
   * Handles sending a new message
   * @param {Event} e - Form submit event
   */
  const handleSendMessage = async(e) => {
    e.preventDefault();
    
    // Don't send empty messages
    if (newMessage.trim() === '') return;
    
    // Add user message to chat history
    setMessages([
      ...messages,
      { sender: 'user', text: newMessage }
    ]);
    const userPrompt = newMessage;
    // Clear input field after sending
    setNewMessage('');

    try {
      // Make POST request to FastAPI /generate endpoint
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: userPrompt, mode: mode })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Error fetching response from AI');
      }

      const data = await response.json();

      const aiResponse = data.response ?? data.message ?? "AI could not generate a proper response.";

      setMessages(prevMessages => [
        ...prevMessages,
        { sender: 'ai', text: aiResponse }
      ]);

    } catch (error) {
      setMessages(prevMessages => [
        ...prevMessages,
        { sender: 'ai', text: `Error: ${error.message}` }
      ]);
    }
    
    
  };

  const removeThinkingText = (text) => {
    const split = text.split('</think>')
    return split.length > 1 ? split[1].trim() : text;
  };


  return (
    <div className="bg-slate-800 rounded-xl shadow-sm p-4 h-full flex flex-col">
      {/* Chat header */}
      <h2 className="text-lg font-semibold text-white mb-4">AI Assistant</h2>
      
      {/* Mode selector */}
      <div className="text-white text-sm mb-2">
          <label htmlFor="mode" className="mr-2">Mode:</label>
          <select
            id="mode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            className="bg-slate-700 border border-slate-600 rounded px-2 py-1 text-white"
          >
            <option value="offline">Offline</option>
            <option value="online">Online</option>
          </select>
        </div>



      {/* Scrollable messages container */}
      <div className="flex-1 min-h-0 overflow-y-auto border border-slate-700 rounded-lg bg-slate-900 p-4 mb-4">
        {/* Messages list with vertical spacing */}
        <div className="space-y-4">
          {messages.map((message, index) => (
            /* Individual message bubble container */
            <div 
              key={index} 
              /* Conditional styling based on sender */
              className={`flex ${message.sender === 'ai' ? 
                'items-start' :  // AI messages align left
                'items-start flex-row-reverse text-right'  // User messages align right
              }`}
            >
              {/* Sender icon */}
              <div className="flex-shrink-0 mx-3">
                <i className={`${message.sender === 'ai' ? 
                  'bi bi-robot' :  // AI icon
                  'bi bi-person'   // User icon
                }`}></i>
              </div>
              
              {/* Message bubble with conditional styling */}
              <div className={`p-3 rounded-lg max-w-[80%] ${
                message.sender === 'ai' ? 
                  'bg-slate-800' :  // AI message background
                  'bg-slate-700'    // User message background
              }`}>
                <p className="text-sm text-slate-200 m-0 leading-6">
                  {message.sender === 'ai' ? (
                  removeThinkingText(message.text)) : (message.text)}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>
    
      {/* Message input form */}
      <form className="mt-4 flex gap-3" onSubmit={handleSendMessage}>
        {/* Text input field */}
        <input
          type="text"
          className="flex-1 px-3 py-3 border border-slate-700 bg-slate-900 text-white rounded-lg focus:outline-none focus:border-indigo-600"
          placeholder="Type your question here..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          aria-label="Type your message"
        />
        {/* Send button */}
        <button 
          type="submit" 
          className="flex-shrink-0 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          aria-label="Send message"
        >
          <i className="bi bi-send mr-2"></i> Send
        </button>
      </form>
    </div>
  );
};

export default AIAssistant;