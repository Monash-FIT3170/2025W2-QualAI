import React, { useState,useEffect,useRef  } from 'react';
import { API_ENDPOINTS } from "../config/api";
import { useProject } from '../contexts/ProjectContext';

/** Constants **/
const INITIAL_MESSAGES = [
  {
    sender: "ai",
    text: "Hello! I'm your AI research assistant. How can I help you analyze your interview data today?",
  },
];

/** Utility to strip AI thinking tags **/
  const removeThinkingText = (text) => {
    const split = text.split('</think>')
    return split.length > 1 ? split[1].trim() : text;
  };

/**
 * AI Assistant chat component for research analysis
 * Provides interactive chat interface between user and AI assistant
 */
const AIAssistant = () => {
  const { activeProjectId, activeProject } = useProject();
  
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  const [mode, setMode] = useState('offline');
  const [template, setTemplate] = useState("default")
  const messagesEndRef = useRef(null);

  // Load messages when a new active project is selected
  useEffect(() => {
    if (activeProjectId) {
      const savedMessages = localStorage.getItem(`aiMessages_${activeProjectId}`);
      setMessages(savedMessages ? JSON.parse(savedMessages) : INITIAL_MESSAGES);
    } else {
      // If no project is selected, show initial messages
      setMessages(INITIAL_MESSAGES);
    }
  }, [activeProjectId]);

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
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage) return;

    const nextAfterUser = [...messages, { sender: 'user', text: trimmedMessage }];
    // Add user message to chat history
    setMessages(nextAfterUser);
    // Clear input field after sending
    setNewMessage('');

    if (activeProjectId) {
      localStorage.setItem(`aiMessages_${activeProjectId}`, JSON.stringify(nextAfterUser));
    }

    try {
      // Make POST request to FastAPI /generate endpoint
      console.log(activeProjectId);
      const response = await fetch(API_ENDPOINTS.GENERATE, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({ 
          prompt: trimmedMessage, 
          mode: mode,
          project: activeProjectId || 'default'
        })

      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Error fetching response from AI');
      }

      const data = await response.json();
      const aiResponse = data.response ?? data.message ?? "AI could not generate a proper response.";

      setMessages(prev => {
        const next = [...prev, { sender: 'ai', text: aiResponse }];
        if (activeProjectId) {
          localStorage.setItem(`aiMessages_${activeProjectId}`, JSON.stringify(next));
        }
          return next;
        });
    } catch (error) {
      setMessages(prev => {
        const next = [...prev, { sender: 'ai', text: `Error: ${error.message}` }];
        if (activeProjectId) {
          localStorage.setItem(`aiMessages_${activeProjectId}`, JSON.stringify(next));
        }
        return next;
      });
    }
    
    
  };

  return (
    <div className="bg-slate-800 rounded-xl shadow-sm p-4 h-full flex flex-col w-full">
      <div className="flex justify-between items-center mb-4">
        {/* Chat header */}
        <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
        <div className="flex flex-col text-left justify-end">
          <span className="text-white text-sm font-semibold mb-1">Template:</span>

          <select
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
            className="bg-slate-700 border border-slate-600 rounded px-2 py-1 text-white"
          >
            <option value="default">None</option>
            <option value="summary">Summarise</option>
            <option value="code_theme">Find Themes</option>
            <option value="outlier">Find Outliers</option>
            <option value="quote">Find Quotes</option>
          </select>
        </div>
      </div>
        {/* Mode selector */}
        <div className="flex items-center gap-3 text-sm text-white mb-2">
              <span className="text-slate-300">{mode}</span>
              <button
                onClick={() => setMode(mode === "offline" ? "online" : "offline")}
                className={`relative inline-flex h-6 w-12 items-center rounded-full transition-colors ${
                  mode === "online" ? "bg-green-500" : "bg-slate-600"
                }`}
              >
                <span
                  className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                    mode === "online" ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
          </div>

      {/* Scrollable messages container */}
      <div className="flex-1 min-h-0 overflow-y-auto border border-slate-700 rounded-lg bg-slate-900 p-4 mb-4 w-full">
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
      <div className="w-full max-w-full overflow-hidden">

      </div>
      <form className="flex w-full items-center" onSubmit={handleSendMessage}>
        {/* Text input field */}
        <input
          type="text"
          className="flex-1 min-w-0 px-3 py-2 border border-slate-700 bg-slate-900 text-white rounded-lg focus:outline-none focus:border-indigo-600"
          placeholder="Ask a question..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          aria-label="Type your message"
        />
        {/* Send button */}
        <button 
          type="submit" 
          className="flex-shrink-0 px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          aria-label="Send message"
        >
          <i className="bi bi-send mr-2"></i>
        </button>
      </form>
    </div>
  );
};


export default AIAssistant;
