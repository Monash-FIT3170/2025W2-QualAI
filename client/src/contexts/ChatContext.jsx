import React, { createContext, useContext, useState } from "react";
import { API_ENDPOINTS } from "../config/api";
import { useProject } from "./ProjectContext";

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const { activeProjectId } = useProject();
  const [messages, setMessages] = useState([]);

  /**
   * Send a message to the model.
   * @param {string} text - The actual prompt sent to the backend.
   * @param {("offline"|"online")} mode
   * @param {string} template
   * @param {string|null} displayText - Optional: what to show in the user's bubble (if different from `text`)
   */
  const sendMessage = async (text, mode = "offline", template = "default", displayText = null) => {
    const trimmed = (text ?? "").trim();
    if (!trimmed) return;

    // What the UI will show for the user's message
    const shown = (displayText ?? trimmed).trim();
    setMessages((prev) => [...prev, { sender: "user", text: shown }]);

    try {
      // Build request body
      const body = {
        prompt: trimmed,                          // actual prompt sent to backend
        mode,
        project: Number.isInteger(activeProjectId) ? activeProjectId : 0,
        template,
      };
      console.log("POST /generate payload:", body);

      const res = await fetch(API_ENDPOINTS.GENERATE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      // Read raw text first (helps debugging non-JSON responses)
      const textResponse = await res.text();
      let data;
      try {
        data = JSON.parse(textResponse);
      } catch {
        console.error("❌ Could not parse JSON, using fallback object");
        data = { response: "Invalid JSON response from backend" };
      }

      const aiResponse =
        data.response ??
        data.message ??
        data.output ??
        data.text ??
        "AI could not respond.";

      setMessages((prev) => [...prev, { sender: "ai", text: aiResponse }]);
    } catch (err) {
      console.error("❌ sendMessage error:", err);
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: `Error: ${err.message}` },
      ]);
    }
  };

  return (
    <ChatContext.Provider value={{ messages, sendMessage, setMessages }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);
