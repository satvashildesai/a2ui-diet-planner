import { useState, useRef, KeyboardEvent } from "react";

interface Props {
  onSend: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export function ChatInput({ onSend, placeholder, disabled }: Props) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const msg = value.trim();
    if (!msg || disabled) return;
    onSend(msg);
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
  };

  return (
    <div
      className="flex items-end gap-3 bg-orange-50 border-2 border-orange-200
                    focus-within:border-orange-400 rounded-2xl px-4 py-3 transition-colors"
    >
      <textarea
        ref={textareaRef}
        rows={1}
        value={value}
        onChange={handleInput}
        onKeyDown={handleKey}
        placeholder={placeholder || "Ask me about Indian diet and nutrition..."}
        disabled={disabled}
        className="flex-1 bg-transparent border-none outline-none resize-none
                   font-sans text-sm text-gray-800 placeholder-gray-400
                   disabled:opacity-50 leading-relaxed"
        style={{ minHeight: "22px", maxHeight: "120px" }}
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        className="w-9 h-9 rounded-xl bg-orange-500 hover:bg-orange-600
                   disabled:bg-gray-300 disabled:cursor-not-allowed
                   text-white flex items-center justify-center flex-shrink-0
                   transition-all hover:scale-105 active:scale-95"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
      </button>
    </div>
  );
}
