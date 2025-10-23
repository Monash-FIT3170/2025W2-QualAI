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

  // Hidden input bar for the generate code
  const [showCodeGenInput, setCodeGenInput] = useState(false);
  const [researchQuestionMessage, setResearchQuestionMessage] = useState('');
  const researchTemplate = 'research';

  //Hidden output popup for code generation
  const [showCodeResultBox, setShowCodeResultBox] = useState(false);
  const [codeResult, setCodeResult] = useState('');

  //output for codes buttons
  const [codes, setCodes] = useState([]);

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


  /** Shared send handler for both the regular text box and code generator**/
  const sendMessage = async (text) => {
    const trimmedMessage = text.trim();
    if (!trimmedMessage) return;

    const nextAfterUser = [...messages, { sender: 'user', text: trimmedMessage }];
    setMessages(nextAfterUser);

    if (activeProjectId) {
      localStorage.setItem(`aiMessages_${activeProjectId}`, JSON.stringify(nextAfterUser));
    }

    try {
      const response = await fetch(API_ENDPOINTS.GENERATE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: trimmedMessage,
          mode: mode,
          project: activeProjectId || 'default',
        }),
      });

      if (!response.ok) throw new Error(await response.text() || 'Error fetching response from AI');

      const data = await response.json();
      const aiResponse = data.response ?? data.message ?? "AI could not generate a proper response.";

      setMessages((prev) => {
        const next = [...prev, { sender: 'ai', text: aiResponse }];
        if (activeProjectId) {
          localStorage.setItem(`aiMessages_${activeProjectId}`, JSON.stringify(next));
        }
        return next;
      });
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: 'ai', text: `Error: ${error.message}` },
      ]);
    }
  };

  /** Main textbox submit **/
  const handleSendMessage = (e) => {
    e.preventDefault();
    sendMessage(newMessage);
    setNewMessage('');
  };

  /** Research question submit **/
  const handleSendSecondary = async (e) => {
    e.preventDefault();
    const text = researchQuestionMessage.trim()
    if (!text) return

    setResearchQuestionMessage('')

    try {
      const response = await fetch(API_ENDPOINTS.GENERATE_CODE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: text,
          mode: mode,
          project: activeProjectId || 'default',
          template: researchTemplate
        }),
      });

    if (!response.ok) throw new Error(await response.text() || 'Error fetching response from AI');

      const data = await response.json();
      const aiResponse = data.response ?? data.message ?? "AI could not generate a proper response.";

    await codesDisplay()
    setShowCodeResultBox(true);
    
  } catch (error) {
    setCodeResult(`Error: ${error.message}`);
    setShowCodeResultBox(true);
  }
  };

  const handleDeleteCode = async (codeId) => {
  try {
    await fetch(`${API_ENDPOINTS.deleteCode(codeId)}`, { method: "DELETE" }); 

    setCodes((prev) => prev.filter((code) => code.id !== codeId));

    
  } catch (error) {
    console.error("Error deleting code:", error);
  }
};

  const codesDisplay = async () => {
    console.log("wwwwwwwwwwwwww")
    if (!activeProjectId) return;
    console.log("wwwwwwwwwwwwww")

    try {
      const response = await fetch(API_ENDPOINTS.listProjectCodes(activeProjectId), {
      method: "GET", // explicitly specify GET (optional; default is GET)
      headers: {
        "Content-Type": "application/json", // optional for GET
      },
    });

      console.log("wwwwwwwwwwwwww")
      console.log(response)
      if (!response.ok) throw new Error("Failed to fetch codes");

      console.log("wwwwwwwwwwwwww")
      const data = await response.json();
      console.log(data)
      setCodes(data.codes || []); // expect [{ id, code, quotes }]
  } catch (error) {
    console.error(error);
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



      {/* Research Question Text Box */}
      <div className="mt-3">
        <button
          onClick={() => setCodeGenInput((s) => !s)}
          className="w-full px-3 py-2 text-sm bg-slate-700 text-white rounded-lg hover:bg-slate-600"
        >
          {showCodeGenInput ? "Hide Code Generator" : "Open Code Generator"}
        </button>

        {showCodeGenInput && (
          <div className="mt-3">

            {/* 👇 Secondary input form */}
            <form className="flex gap-3" onSubmit={handleSendSecondary}>
              <input
                type="text"
                className="flex-1 px-3 py-3 border border-slate-700 bg-slate-900 text-white rounded-lg focus:outline-none focus:border-green-600"
                placeholder={`Enter Research Question`}
                value={researchQuestionMessage}
                onChange={(e) => setResearchQuestionMessage(e.target.value)}
              />
              <button
                type="submit"
                className="flex-shrink-0 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <i className="bi bi-play-fill mr-2"></i> Run
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Research Code Results Box */}
      {showCodeResultBox && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-xl shadow-lg w-11/12 md:w-2/3 lg:w-1/2 p-6 relative">
            <button
              onClick={() => {
                setShowCodeResultBox(false);
                setCodes([]);        
              }}
              
              className="absolute top-3 right-3 text-slate-400 hover:text-white"
            >
              <i className="bi bi-x-lg"></i>
            </button>

            <h3 className="text-lg font-semibold text-white mb-4">Generated Codes</h3>

            <div className="bg-slate-900 p-4 rounded-lg max-h-[60vh] overflow-y-auto">
              {codes.length === 0 ? (
                <p className="text-slate-400">No codes found for this project.</p>
              ) : (
                <div className="flex flex-col gap-2">
                  {codes.map((codeItem) => (
                    <button
                      key={codeItem.id}
                      onClick={() => {
                            if (confirm("Delete this code?")) handleDeleteCode(codeItem.id)
                          }}
                      className="w-full text-left px-3 py-2 bg-slate-700 hover:bg-red-600 text-white rounded-lg transition-colors"
                    >
                      {codeItem.code}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>

    
  );
};


export default AIAssistant;
