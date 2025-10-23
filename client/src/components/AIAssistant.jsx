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
  const { activeProjectId } = useProject();
  
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const [mode, setMode] = useState('offline');
  const [template, setTemplate] = useState("default")
  const messagesEndRef = useRef(null);
  const activeProjectIdRef = useRef(activeProjectId); // Track active project in ref

  // Update ref when activeProjectId changes
  useEffect(() => {
    activeProjectIdRef.current = activeProjectId;
  }, [activeProjectId]);

  // Function to load messages from server
  const loadMessages = async (projectId) => {
    if (!projectId) {
      setMessages(INITIAL_MESSAGES);
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(API_ENDPOINTS.getProjectChat(projectId));
      if (!res.ok) throw new Error('Failed to load chat');
      const data = await res.json();
      const normalized = Array.isArray(data)
        ? data.map(m => ({ sender: m.sender, text: m.text }))
        : [];

      // If no messages exist, save and display the initial greeting
      if (normalized.length === 0) {
        const initialMessage = INITIAL_MESSAGES[0];
        setMessages(INITIAL_MESSAGES);
        
        // Save initial greeting to backend
        fetch(API_ENDPOINTS.postProjectChat(projectId), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            sender: initialMessage.sender, 
            message: initialMessage.text 
          })
        }).catch(err => console.error('Failed to save initial greeting:', err));
      } else {
        setMessages(normalized);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
      setMessages(INITIAL_MESSAGES);
    } finally {
      setLoading(false);
    }
  };

  // Load messages when a new active project is selected
  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      await loadMessages(activeProjectId);
      if (cancelled) {
        // If cancelled during load, reload the current active project
        await loadMessages(activeProjectIdRef.current);
      }
    };

    load();
    return () => { cancelled = true; };
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

    // Get project ID at send time
    const requestProjectId = activeProjectId;

    // Add user message to UI
    const nextAfterUser = [...messages, { sender: 'user', text: trimmedMessage }];
    setMessages(nextAfterUser);
    
    // Clear input field after sending
    setNewMessage('');

    // Sync user message to backend
    if (requestProjectId) {
      try {
        await fetch(API_ENDPOINTS.postProjectChat(requestProjectId), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sender: 'user', message: trimmedMessage })
        });
      } catch (error) {
        console.error('Failed to sync user message:', error);
      }
    }

    try {
      // Make POST request to FastAPI /generate endpoint
      console.log('Generating response for project:', requestProjectId);
      const response = await fetch(API_ENDPOINTS.GENERATE, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({ 
          prompt: trimmedMessage, 
          mode: mode,
          project: requestProjectId || 'default',
          template: template
        })

      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Error fetching response from AI');
      }

      const data = await response.json();
      console.log('AI response received:', data.response ?? data.message);

      // Check if user is still on the same project using ref
      if (activeProjectIdRef.current === requestProjectId) {
        // Reload messages from server to ensure consistency
        await loadMessages(requestProjectId);
      } else {
        console.log(`AI response saved to project ${requestProjectId}, but user switched to project ${activeProjectIdRef.current}`);
      }
      
      // Backend already saved the AI response
      
    } catch (error) {
      const errorMessage = `Error: ${error.message}`;
      // Only show error if still on same project
      if (activeProjectIdRef.current === requestProjectId) {
        // Show error message temporarily
        const errorMessages = [...nextAfterUser, { sender: 'ai', text: errorMessage }];
        setMessages(errorMessages);
      }
    }
    
    
  };

  return (
    <div className="bg-slate-800 rounded-xl shadow-sm p-4 h-full flex flex-col">
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
      <div className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden border border-slate-700 rounded-lg bg-slate-900 p-4 mb-4">
        {/* Messages list with vertical spacing */}
        <div className="space-y-4">
          {loading && (
            <div className="text-slate-300 text-sm">Loading chat…</div>
          )}
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
              <div className={`p-3 rounded-lg max-w-[80%] min-w-0 ${
                message.sender === 'ai' ? 
                  'bg-slate-800' :  // AI message background
                  'bg-slate-700'    // User message background
              }`}>
                <p 
                  className="text-sm text-slate-200 m-0 leading-relaxed break-words whitespace-pre-wrap overflow-hidden"
                  style={{ wordBreak: 'break-word', overflowWrap: 'anywhere' }}
                >
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
