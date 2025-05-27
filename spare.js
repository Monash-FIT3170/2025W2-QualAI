const messagesEndRef = useRef(null);

  // scroll to bottom of chat when there is a new message 
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth'});}, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (newMessage.trim() === '') return;

    // Add the user's message to the chat
    setMessages(prevMessages => [
      ...prevMessages,
      { sender: 'user', text: newMessage }
    ]);

    const userPrompt = newMessage;
    setNewMessage('');

    try {
      // Make POST request to FastAPI /generate endpoint
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: userPrompt })
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
                <i className={message.sender === 'ai' ? 'bi bi-robot mr-3 text-gray-400' : 'bi bi-person mr-3 text-gray-400'}></i>
              </div>
              <div className="message-text">
                {message.sender === 'ai' ? (
                  <ReactMarkdown>{removeThinkingText(message.text)}</ReactMarkdown>) : (<p>{message.text}</p>)}
              </div>
            </div>
          ))}
           <div ref={messagesEndRef} />
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