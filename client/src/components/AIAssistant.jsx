import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useProject } from '../contexts/ProjectContext';
import { useChat } from "../contexts/ChatContext";

/** Helpers to clean text before using it as a prompt **/
const removeThinkingText = (text) => {
  const split = text.split('</think>');
  return split.length > 1 ? split[1].trim() : text;
};
const stripTags = (text) => text.replace(/<\/?[^>]+>/g, '');
const collapseWS = (t) => t.replace(/\s+/g, ' ').trim();
const cleanForAction = (raw) => collapseWS(stripTags(removeThinkingText(raw)));

const AIAssistant = () => {
  const { activeProjectId } = useProject();
  const { messages, sendMessage, setMessages } = useChat();

  const [mode, setMode] = useState('offline');
  const [template, setTemplate] = useState('default');
  const [newMessage, setNewMessage] = useState('');
  const [hoveredIndex, setHoveredIndex] = useState(null);
  const [pendingAction, setPendingAction] = useState({}); // { [index]: 'summary'|'explain'|'rewrite'|null }

  const messagesEndRef = useRef(null);
  const activeProjectIdRef = useRef(activeProjectId); // Track active project in ref

  // Persistence handled in ChatContext

  /** Auto scroll **/
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /** Send from input — clear immediately **/
  const handleSendMessage = (e) => {
    e.preventDefault();
    const trimmed = newMessage.trim();
    if (!trimmed) return;
    setNewMessage(''); // clear instantly
    sendMessage(trimmed, mode, template); // fire-and-forget
  };

  /** Click actions on an AI bubble **/
  const handleBubbleAction = async (index, action) => {
    const m = messages[index];
    if (!m || m.sender !== 'ai') return;
    if (pendingAction[index]) return;

    const cleaned = cleanForAction(m.text);
    if (!cleaned) return;

    const templateMap = {
      summary: 'summary_direct',
      explain: 'explain',
      rewrite: 'rewrite',
    };
    const labelMap = {
      summary: 'Summarise',
      explain: 'Explain',
      rewrite: 'Rewrite',
    };

    const chosenTemplate = templateMap[action] || 'summary_direct';
    const displayLabel = labelMap[action] || 'Summarise';

    try {
      setPendingAction(prev => ({ ...prev, [index]: action }));
      // ⬇️ Display a concise user bubble ("Summarise/Explain/Rewrite") while sending the cleaned AI text
      await sendMessage(cleaned, mode, chosenTemplate, displayLabel);
    } finally {
      setPendingAction(prev => ({ ...prev, [index]: null }));
    }
  };

  const pendingLabel = useMemo(() => ({
    summary: 'Summarising…',
    explain: 'Explaining…',
    rewrite: 'Rewriting…'
  }), []);

  return (
    <div className="bg-slate-800 rounded-xl shadow-sm p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-white">AI Assistant</h2>

        <div className="flex items-center gap-6">
          {/* Template select (for normal prompts) */}
          <div className="flex flex-col text-left justify-end">
            <span className="text-white text-sm font-semibold mb-1">Template:</span>
            <select
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
              className="bg-slate-700 border border-slate-600 rounded px-2 py-1 text-white"
            >
              <option value="default">None</option>
              <option value="summary">Summarise (RAG)</option>
              <option value="code_theme">Find Themes</option>
              <option value="outlier">Find Outliers</option>
              <option value="quote">Find Quotes</option>
            </select>
          </div>

          {/* Mode toggle */}
          <div className="flex items-center gap-3 text-sm text-white">
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
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 min-h-0 overflow-y-auto border border-slate-700 rounded-lg bg-slate-900 p-4 mb-4">
        <div className="space-y-4">
          {messages.map((message, index) => {
            const isAI = message.sender === 'ai';
            const isHovered = hoveredIndex === index;
            const isPending = Boolean(pendingAction[index]);
            const currentAction = pendingAction[index];

            return (
              <div
                key={index}
                className={`group relative flex ${isAI ? 'items-start' : 'items-start flex-row-reverse text-right'}`}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(prev => (prev === index ? null : prev))}
              >
                {/* Avatar */}
                <div className="flex-shrink-0 mx-3">
                  <i className={isAI ? 'bi bi-robot' : 'bi bi-person'}></i>
                </div>

                {/* Bubble */}
                <div className={`p-3 rounded-lg max-w-[80%] ${isAI ? 'bg-slate-800' : 'bg-slate-700'}`}>
                  <p className="text-sm text-slate-200 m-0 leading-6">
                    {isAI ? removeThinkingText(message.text) : message.text}
                  </p>
                </div>

                {/* Hover actions for AI bubbles */}
                {isAI && (
                  <div
                    className={`absolute -top-3 left-10 transition-opacity ${
                      isHovered ? 'opacity-100' : 'opacity-0'
                    }`}
                  >
                    <div className="flex items-center gap-2 bg-indigo-600 text-white text-[11px] px-2 py-[2px] rounded shadow-md border border-indigo-600">
                      <button
                        className={`px-2 py-[3px] rounded ${isPending ? 'opacity-60 cursor-not-allowed' : 'hover:bg-indigo-700'}`}
                        onClick={() => handleBubbleAction(index, 'summary')}
                        disabled={isPending}
                        aria-label="Summarise this message"
                        title="Summarise"
                      >
                        {isPending && currentAction === 'summary' ? pendingLabel.summary : 'Summarise'}
                      </button>
                      <span className="text-white">•</span>
                      <button
                        className={`px-2 py-[3px] rounded ${isPending ? 'opacity-60 cursor-not-allowed' : 'hover:bg-indigo-700'}`}
                        onClick={() => handleBubbleAction(index, 'explain')}
                        disabled={isPending}
                        aria-label="Explain this message"
                        title="Explain"
                      >
                        {isPending && currentAction === 'explain' ? pendingLabel.explain : 'Explain'}
                      </button>
                      <span className="text-white">•</span>
                      <button
                        className={`px-2 py-[3px] rounded ${isPending ? 'opacity-60 cursor-not-allowed' : 'hover:bg-indigo-700'}`}
                        onClick={() => handleBubbleAction(index, 'rewrite')}
                        disabled={isPending}
                        aria-label="Rewrite this message"
                        title="Rewrite"
                      >
                        {isPending && currentAction === 'rewrite' ? pendingLabel.rewrite : 'Rewrite'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Composer */}
      <form className="mt-4 flex gap-3" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="flex-1 px-3 py-3 border border-slate-700 bg-slate-900 text-white rounded-lg focus:outline-none focus:border-indigo-600"
          placeholder="Type your question here..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          aria-label="Type your message"
        />
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
