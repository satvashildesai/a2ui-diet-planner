import { useDietStore } from "../store/dietStore";

// A2UI message dispatcher - in a real implementation this would come from @a2ui/react-renderer
// Here we expose it through a global surface state
type A2UIMessage = Record<string, unknown>;
type A2UIDispatcher = (msg: A2UIMessage) => void;

let globalDispatcher: A2UIDispatcher | null = null;

export const registerA2UIDispatcher = (dispatcher: A2UIDispatcher) => {
  globalDispatcher = dispatcher;
};

export function useAgentSSE() {
  const { sessionId, setIsStreaming, setMode, setActivePlanExists } =
    useDietStore();

  const consumeStream = async (response: Response) => {
    const reader = response.body!.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const lines = decoder.decode(value).split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const raw = line.slice(6);
        if (raw === "[DONE]") {
          setIsStreaming(false);
          return;
        }
        try {
          const chunk = JSON.parse(raw);

          // Dispatch A2UI messages to the renderer
          if (
            chunk.surfaceUpdate ||
            chunk.dataModelUpdate ||
            chunk.beginRendering
          ) {
            if (globalDispatcher) {
              globalDispatcher(chunk);
            }
          }

          // Handle meta events
          if (chunk.type === "mode_change") {
            setMode(
              chunk.mode as
                | "intake"
                | "plan_active"
                | "interrupt_pending"
                | "guardrail"
            );
            if (chunk.mode === "plan_active") setActivePlanExists(true);
          }
          if (chunk.type === "reset") {
            useDietStore.getState().reset();
          }
        } catch {
          // Ignore parse errors on partial chunks
        }
      }
    }
    setIsStreaming(false);
  };

  const sendMessage = async (message: string) => {
    if (!sessionId) return;
    setIsStreaming(true);
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    await consumeStream(res);
  };

  const sendAction = async (actionName: string, context: object) => {
    if (!sessionId) return;
    setIsStreaming(true);
    const res = await fetch("/api/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        action_name: actionName,
        context,
      }),
    });
    await consumeStream(res);
  };

  return { sendMessage, sendAction };
}
