interface Props {
  role: "user" | "assistant";
  content: string;
}

export function ChatBubble({ role, content }: Props) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center
                    text-sm flex-shrink-0 self-end
                    ${
                      isUser
                        ? "bg-teal-700 text-white font-semibold"
                        : "bg-gradient-to-br from-orange-500 to-amber-400 text-white"
                    }`}
      >
        {isUser ? "U" : "🥗"}
      </div>
      <div
        className={`max-w-[72%] px-4 py-3 rounded-2xl text-sm leading-relaxed
                    ${
                      isUser
                        ? "bg-teal-700 text-white rounded-br-sm"
                        : "bg-white border border-orange-100 text-gray-800 rounded-bl-sm shadow-sm"
                    }`}
      >
        {content}
      </div>
    </div>
  );
}
