interface Props {
  message: string;
  suggestion: string;
}

export function GuardrailCard({ message, suggestion }: Props) {
  return (
    <div
      className="bg-gray-50 border border-gray-200 rounded-2xl p-5
                    max-w-lg mx-auto text-center"
    >
      <span className="text-4xl">🙏</span>
      <p className="text-gray-700 mt-3 font-medium">{message}</p>
      <p className="text-sm text-orange-600 mt-2">{suggestion}</p>
    </div>
  );
}
