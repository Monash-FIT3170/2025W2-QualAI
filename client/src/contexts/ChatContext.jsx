import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import { API_ENDPOINTS } from "../config/api";
import { useProject } from "./ProjectContext";

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const { activeProjectId } = useProject();
  const hasMountedRef = useRef(false);
  const [loaded, setLoaded] = useState(false);

  // Determine last active project synchronously for initial render
  const storedActiveRaw = (typeof window !== 'undefined') ? localStorage.getItem('activeProjectId') : null;
  const storedActiveId = storedActiveRaw !== null && storedActiveRaw !== ''
    ? (isNaN(Number(storedActiveRaw)) ? storedActiveRaw : Number(storedActiveRaw))
    : null;

  // Default greeting shown when a project has no saved chat
  const INITIAL_MESSAGES = [
    {
      sender: "ai",
      text: "Hello! I'm your AI research assistant. How can I help you analyze your interview data today?",
    },
  ];

  // Helper: load messages (prefer non-empty sources)
  const loadFromStorage = (pid) => {
    if (pid === null || pid === undefined) return INITIAL_MESSAGES;
    const key = `aiMessages_${pid}`;
    const mapRaw = localStorage.getItem("aiMessagesByProject");
    let mapParsed;
    if (mapRaw) {
      try {
        const map = JSON.parse(mapRaw) || {};
        mapParsed = map[String(pid)];
      } catch {}
    }
    const perRaw = localStorage.getItem(key);
    const perParsed = perRaw ? (() => { try { return JSON.parse(perRaw); } catch { return null; } })() : null;
    const legacyRaw = localStorage.getItem("aiMessages");
    const legacyParsed = legacyRaw ? (() => { try { return JSON.parse(legacyRaw); } catch { return null; } })() : null;

    if (Array.isArray(mapParsed) && mapParsed.length > 0) return mapParsed;
    if (Array.isArray(perParsed) && perParsed.length > 0) return perParsed;
    if (Array.isArray(legacyParsed) && legacyParsed.length > 0) return legacyParsed;
    return mapParsed || perParsed || legacyParsed || INITIAL_MESSAGES;
  };

  // Initialize messages synchronously from stored active project for immediate render on refresh
  const [messages, setMessages] = useState(() => loadFromStorage(storedActiveId));
  const lastProjectIdRef = useRef(storedActiveId);
  const currentProjectIdRef = useRef(storedActiveId);

  // Keep a ref to the current project id for save-on-message changes
  useEffect(() => {
    currentProjectIdRef.current = activeProjectId;
  }, [activeProjectId]);

  // When the active project changes, first save the current messages to the previous project's key/map,
  // then load messages for the new project.
  useEffect(() => {
    try {
      // On initial mount, don't attempt to save a previous project's messages
      const prevId = lastProjectIdRef.current;
      if (hasMountedRef.current) {
        if (prevId !== null && prevId !== undefined) {
          try {
            // Save to consolidated map
            const mapRaw = localStorage.getItem("aiMessagesByProject");
            const map = mapRaw ? JSON.parse(mapRaw) : {};
            map[String(prevId)] = messages || [];
            localStorage.setItem("aiMessagesByProject", JSON.stringify(map));
            // Keep per-project key for backward compatibility
            localStorage.setItem(`aiMessages_${prevId}`, JSON.stringify(messages || []));
          } catch (e) {
            console.error(`[Chat] Failed saving messages for project ${prevId}:`, e);
          }
        }
      }

      // Reset loaded flag while we switch projects
      setLoaded(false);
      if (activeProjectId !== null && activeProjectId !== undefined) {
        const key = `aiMessages_${activeProjectId}`;
        const mapRaw = localStorage.getItem("aiMessagesByProject");
        let mapParsed;
        if (mapRaw) {
          try {
            const map = JSON.parse(mapRaw) || {};
            mapParsed = map[String(activeProjectId)];
          } catch {}
        }
        const perRaw = localStorage.getItem(key);
        const perParsed = perRaw ? (() => { try { return JSON.parse(perRaw); } catch { return null; } })() : null;
        const legacyRaw = localStorage.getItem("aiMessages");
        const legacyParsed = legacyRaw ? (() => { try { return JSON.parse(legacyRaw); } catch { return null; } })() : null;

        let parsed = null;
        // Prefer non-empty data source
        if (Array.isArray(mapParsed) && mapParsed.length > 0) {
          parsed = mapParsed;
        } else if (Array.isArray(perParsed) && perParsed.length > 0) {
          parsed = perParsed;
          // heal map from per-project storage
          try {
            const mapObj = mapRaw ? JSON.parse(mapRaw) || {} : {};
            mapObj[String(activeProjectId)] = perParsed;
            localStorage.setItem("aiMessagesByProject", JSON.stringify(mapObj));
          } catch {}
        } else if (Array.isArray(legacyParsed) && legacyParsed.length > 0) {
          parsed = legacyParsed;
          // migrate legacy to per-project and map
          try {
            localStorage.setItem(key, JSON.stringify(legacyParsed));
            const mapObj = mapRaw ? JSON.parse(mapRaw) || {} : {};
            mapObj[String(activeProjectId)] = legacyParsed;
            localStorage.setItem("aiMessagesByProject", JSON.stringify(mapObj));
          } catch {}
        } else {
          // fallbacks if everything is empty
          parsed = mapParsed || perParsed || legacyParsed || INITIAL_MESSAGES;
        }

        setMessages(parsed);
        setLoaded(true);
      } else {
        setMessages(INITIAL_MESSAGES);
        setLoaded(true);
      }

      lastProjectIdRef.current = activeProjectId;
      hasMountedRef.current = true;
    } catch (e) {
      console.error("Failed to handle project switch for chat:", e);
      setMessages(INITIAL_MESSAGES);
      setLoaded(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeProjectId]);

  // Persist messages whenever they change, under the current project id (map + per-project)
  useEffect(() => {
    try {
      const pid = currentProjectIdRef.current;
      if (!loaded) return; // avoid clobbering before initial load completes
      if (pid === null || pid === undefined) return;
      // Update consolidated map
      const mapRaw = localStorage.getItem("aiMessagesByProject");
      const map = mapRaw ? JSON.parse(mapRaw) : {};
      map[String(pid)] = messages || [];
      localStorage.setItem("aiMessagesByProject", JSON.stringify(map));
      // Backward-compatible per-project key
      localStorage.setItem(`aiMessages_${pid}`, JSON.stringify(messages || []));
    } catch (e) {
      console.error("Failed to save chat to localStorage:", e);
    }
  }, [messages, loaded]);

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
