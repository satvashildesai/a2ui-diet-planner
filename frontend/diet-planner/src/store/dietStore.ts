import { create } from "zustand";

type AgentMode = "intake" | "plan_active" | "interrupt_pending" | "guardrail";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface DietStore {
  sessionId: string | null;
  mode: AgentMode;
  activePlanExists: boolean;
  conversationHistory: ChatMessage[];
  isStreaming: boolean;
  setSessionId: (id: string) => void;
  setMode: (mode: AgentMode) => void;
  addMessage: (msg: ChatMessage) => void;
  setActivePlanExists: (val: boolean) => void;
  setIsStreaming: (val: boolean) => void;
  reset: () => void;
}

export const useDietStore = create<DietStore>((set) => ({
  sessionId: null,
  mode: "intake",
  activePlanExists: false,
  conversationHistory: [],
  isStreaming: false,
  setSessionId: (id) => set({ sessionId: id }),
  setMode: (mode) => set({ mode }),
  addMessage: (msg) =>
    set((s) => ({
      conversationHistory: [...s.conversationHistory, msg],
    })),
  setActivePlanExists: (val) => set({ activePlanExists: val }),
  setIsStreaming: (val) => set({ isStreaming: val }),
  reset: () =>
    set({
      mode: "intake",
      activePlanExists: false,
      conversationHistory: [],
      isStreaming: false,
    }),
}));
