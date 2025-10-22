import React, { createContext, useContext, useState } from "react";
import { API_ENDPOINTS } from "../config/api";
import { useProject } from "./ProjectContext";

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const { activeProjectId } = useProject();
  const [messages, setMessages] = useState([]);

  const sendMessage = async (text, mode = "offline", template = "default") => {
    const trimmed = text.trim();
    if (!trimmed) return;

    setMessages((prev) => [...prev, { sender: "user", text: trimmed }]);

    console.log("🟡 Sending fetch to:", API_ENDPOINTS.GENERATE);

    try {
      console.log("🟡 Sending fetch to:", API_ENDPOINTS.GENERATE);

      const res = await fetch(API_ENDPOINTS.GENERATE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: trimmed,
          mode,
          project: activeProjectId || "default",
          template,
        }),
      });

      console.log("🔵 Response status:", res.status);

      // Log raw response body text before parsing JSON
      const textResponse = await res.text();
      console.log("🟣 Raw body:", textResponse);

      let data;
      try {
        data = JSON.parse(textResponse);
      } catch {
        console.error("❌ Could not parse JSON, using fallback object");
        data = { response: "Invalid JSON response from backend" };
      }

      console.log("AI raw response:", data);

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
