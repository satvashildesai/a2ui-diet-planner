import { useForm } from "react-hook-form";
import { useAgentSSE } from "../hooks/useAgentSSE";

interface Field {
  id: string;
  label: string;
  type: string;
  options?: string[];
}

interface Props {
  title?: string | null;
  subtitle?: string | null;
  fields?: Field[] | null;
  submitAction?: string | null;
  pendingQuestion?: string | null;
}

export function ContextInterruptForm({
  title,
  subtitle,
  fields,
  submitAction,
  pendingQuestion,
}: Props) {
  const { sendAction } = useAgentSSE();
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm();

  if (!fields || fields.length === 0) return null;

  const onSubmit = (data: Record<string, unknown>) => {
    sendAction(submitAction ?? "submit_interrupt_context", {
      ...data,
      pending_question: pendingQuestion,
    });
  };

  return (
    <div className="bg-white border-2 border-amber-300 rounded-2xl overflow-hidden shadow-lg">
      <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border-b border-amber-200 p-5">
        <div className="flex items-start gap-3">
          <span className="text-2xl">🤔</span>
          <div>
            <h3 className="font-bold text-gray-800">
              {title ?? "Quick Check"}
            </h3>
            <p className="text-sm text-gray-600 mt-0.5">
              {subtitle ??
                "These details help me personalise the answer for you."}
            </p>
          </div>
        </div>
      </div>

      {pendingQuestion && (
        <div className="mx-5 mt-4 bg-orange-50 border border-orange-200 rounded-xl p-3">
          <p className="text-[10px] font-bold text-orange-500 uppercase tracking-wider mb-1">
            Your question (on hold):
          </p>
          <p className="text-sm text-gray-700 italic">"{pendingQuestion}"</p>
        </div>
      )}

      <div className="p-5">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {fields.map((field) => (
            <div key={field.id}>
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                {field.label}
              </label>
              {field.type === "select" ? (
                <select
                  {...register(field.id)}
                  className="w-full rounded-xl border-2 border-amber-200 px-3 py-2.5
                             text-sm focus:outline-none focus:border-amber-400
                             bg-amber-50/30 transition-colors"
                >
                  <option value="">Choose...</option>
                  {(field.options ?? []).map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  {...register(field.id)}
                  type={field.type}
                  className="w-full rounded-xl border-2 border-amber-200 px-3 py-2.5
                             text-sm focus:outline-none focus:border-amber-400
                             bg-amber-50/30 transition-colors"
                />
              )}
            </div>
          ))}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-gradient-to-r from-amber-500 to-orange-500
                       hover:from-amber-600 hover:to-orange-600 text-white
                       font-semibold py-3 rounded-xl transition-all
                       disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {isSubmitting
              ? "Analysing..."
              : "Submit & Get My Personalised Answer →"}
          </button>
        </form>
      </div>
    </div>
  );
}
