import { useEffect, useRef, useState } from "react";
import { ChatInput } from "./components/ChatInput";
import { ChatBubble } from "./components/ChatBubble";
import { DisclaimerBanner } from "./components/DisclaimerBanner";
import { useDietStore } from "./store/dietStore";
import { useAgentSSE } from "./hooks/useAgentSSE";
import "./catalog";

// A2UI Surface renderer — in production this would be @a2ui/react-renderer
// Here we implement a lightweight surface that processes A2UI messages
import { A2UISurface } from "./A2UISurface";

export default function App() {
  const {
    sessionId,
    setSessionId,
    conversationHistory,
    addMessage,
    mode,
    isStreaming,
  } = useDietStore();
  const { sendMessage } = useAgentSSE();
  const chatRef = useRef<HTMLDivElement>(null);
  const [showWelcome, setShowWelcome] = useState(true);

  useEffect(() => {
    fetch("/api/session", { method: "POST" })
      .then((r) => r.json())
      .then(({ session_id }) => setSessionId(session_id))
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [conversationHistory, isStreaming]);

  const handleSend = (message: string) => {
    setShowWelcome(false);
    addMessage({
      role: "user",
      content: message,
      timestamp: new Date().toISOString(),
    });
    sendMessage(message);
  };

  const suggestions = [
    "I want to lose weight 🏃",
    "Build muscle with vegetarian diet",
    "Jain diet plan for me",
    "I need to gain healthy weight",
  ];

  return (
    <div className="min-h-screen bg-orange-50 flex flex-col max-w-3xl mx-auto">
      {/* Header */}
      <header
        className="bg-white border-b border-orange-100 px-6 py-4
                         flex items-center gap-3 shadow-sm sticky top-0 z-50"
      >
        <div
          className="w-11 h-11 bg-gradient-to-br from-orange-500 to-amber-400
                        rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
        >
          🥗
        </div>
        <div>
          <h1
            className="text-xl font-bold text-gray-800"
            style={{ fontFamily: "'Playfair Display', serif" }}
          >
            AaharAI
          </h1>
          <p className="text-xs text-gray-500">
            Your Indian Diet Planning Assistant
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span
            className={`text-xs px-3 py-1 rounded-full font-semibold uppercase tracking-wide
            ${
              mode === "plan_active"
                ? "bg-green-100 text-green-700"
                : mode === "interrupt_pending"
                ? "bg-amber-100 text-amber-700"
                : "bg-orange-100 text-orange-700"
            }`}
          >
            {mode === "plan_active"
              ? "Plan Active"
              : mode === "interrupt_pending"
              ? "Needs Info"
              : "Intake"}
          </span>
        </div>
      </header>

      {/* Disclaimer */}
      <DisclaimerBanner />

      {/* Chat area */}
      <div ref={chatRef} className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {/* Welcome screen */}
        {showWelcome && conversationHistory.length === 0 && (
          <div
            className="flex flex-col items-center justify-center text-center
                          py-12 px-6 gap-5 animate-fade-in"
          >
            <div className="text-6xl">🥗</div>
            <div>
              <h2
                className="text-2xl font-bold text-gray-800 mb-2"
                style={{ fontFamily: "'Playfair Display', serif" }}
              >
                Namaste! I'm AaharAI
              </h2>
              <p className="text-gray-500 text-sm leading-relaxed max-w-md">
                Your culturally intelligent Indian diet planning assistant. I
                create personalised meal plans using real Indian dishes — dal,
                roti, sabzi, and everything in between!
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-center mt-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => handleSend(s)}
                  className="bg-white border-2 border-orange-200 hover:border-orange-400
                             hover:bg-orange-50 text-gray-600 hover:text-orange-700
                             rounded-2xl px-4 py-2 text-sm transition-all font-medium"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message history */}
        {conversationHistory.map((msg, i) => (
          <ChatBubble key={i} role={msg.role} content={msg.content} />
        ))}

        {/* Streaming indicator */}
        {isStreaming && (
          <div className="flex gap-2.5">
            <div
              className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-amber-400
                            flex items-center justify-center text-white flex-shrink-0 self-end"
            >
              🥗
            </div>
            <div
              className="bg-white border border-orange-100 rounded-2xl rounded-bl-sm
                            shadow-sm px-4 py-3 flex gap-1.5 items-center"
            >
              <span
                className="w-2 h-2 rounded-full bg-orange-400 animate-bounce"
                style={{ animationDelay: "0ms" }}
              />
              <span
                className="w-2 h-2 rounded-full bg-orange-400 animate-bounce"
                style={{ animationDelay: "150ms" }}
              />
              <span
                className="w-2 h-2 rounded-full bg-orange-400 animate-bounce"
                style={{ animationDelay: "300ms" }}
              />
            </div>
          </div>
        )}

        {/* A2UI Surface — renders all agent-driven components */}
        <A2UISurface surfaceId="diet_surface" />
      </div>

      {/* Input */}
      <div className="border-t border-orange-100 bg-white px-4 py-4 sticky bottom-0">
        <ChatInput
          onSend={handleSend}
          disabled={isStreaming || mode === "interrupt_pending"}
          placeholder={
            mode === "intake"
              ? 'Tell me your diet goal (e.g. "I want to lose weight")'
              : mode === "interrupt_pending"
              ? "Please answer the quick questions above to continue..."
              : "Ask about your plan, a food, or a substitution..."
          }
        />
      </div>
    </div>
  );
}
