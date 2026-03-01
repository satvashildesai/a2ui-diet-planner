// ActionButton
interface ActionButtonProps {
  label: string;
  action: string;
  context?: Record<string, unknown>;
  variant?: "primary" | "secondary" | "outline";
  onAction?: (action: string, context?: Record<string, unknown>) => void;
}

export function ActionButton({
  label,
  action,
  context,
  variant = "primary",
  onAction,
}: ActionButtonProps) {
  const variants = {
    primary: "bg-orange-500 hover:bg-orange-600 text-white",
    secondary: "bg-teal-600 hover:bg-teal-700 text-white",
    outline: "border-2 border-orange-500 text-orange-600 hover:bg-orange-50",
  };

  return (
    <button
      onClick={() => onAction?.(action, context)}
      className={`px-4 py-2 rounded-lg font-semibold text-sm transition-colors ${variants[variant]}`}
    >
      {label}
    </button>
  );
}
