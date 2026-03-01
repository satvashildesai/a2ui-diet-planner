// GuardrailCard
interface GuardrailProps {
  message: string;
  suggestion: string;
}

export function GuardrailCard({ message, suggestion }: GuardrailProps) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-2xl p-8 text-center max-w-lg mx-auto">
      <div className="text-5xl mb-4">🙏</div>
      <p className="text-gray-700 font-semibold text-base mb-3">{message}</p>
      <p className="text-sm text-orange-600 leading-relaxed">{suggestion}</p>
    </div>
  );
}
