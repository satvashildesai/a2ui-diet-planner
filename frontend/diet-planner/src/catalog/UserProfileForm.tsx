import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAgentSSE } from "../hooks/useAgentSSE";

interface Field {
  id: string;
  label: string;
  type: "number" | "text" | "select";
  options?: string[];
  required: boolean;
}

interface Props {
  goal?: string | null;
  fields?: Field[] | null;
  submitAction?: string | null;
}

export function UserProfileForm({ goal, fields, submitAction }: Props) {
  const { sendAction } = useAgentSSE();
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm({
    resolver: zodResolver(z.object({}).passthrough()),
  });

  if (!fields || fields.length === 0) return null;

  const onSubmit = (data: Record<string, unknown>) => {
    sendAction(submitAction ?? "submit_profile", {
      ...data,
      goal: goal ?? "lose_weight",
    });
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-orange-100">
      <div className="bg-gradient-to-r from-orange-500 to-amber-500 p-6 text-white">
        <div className="flex items-center gap-3">
          <span className="text-3xl">🥗</span>
          <div>
            <h2 className="text-xl font-bold">Your Diet Profile</h2>
            {goal && (
              <p className="text-orange-100 text-sm mt-1">
                Goal: <strong>{goal}</strong>
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {fields.map((field) => (
              <div
                key={field.id}
                className={field.type === "text" ? "col-span-2" : ""}
              >
                <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">
                  {field.label}
                  {field.required && (
                    <span className="text-orange-500 ml-1">*</span>
                  )}
                </label>
                {field.type === "select" ? (
                  <select
                    {...register(field.id)}
                    className="w-full rounded-xl border-2 border-gray-200 px-3 py-2.5
                               text-sm focus:outline-none focus:border-orange-400
                               bg-orange-50/30 transition-colors appearance-none"
                  >
                    <option value="">Select...</option>
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
                    className="w-full rounded-xl border-2 border-gray-200 px-3 py-2.5
                               text-sm focus:outline-none focus:border-orange-400
                               bg-orange-50/30 transition-colors"
                    placeholder={
                      field.id === "height_cm"
                        ? "e.g. 165"
                        : field.id === "weight_kg"
                        ? "e.g. 68"
                        : field.id === "age"
                        ? "e.g. 28"
                        : field.id === "allergies"
                        ? "e.g. peanuts, shellfish"
                        : ""
                    }
                  />
                )}
              </div>
            ))}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-gradient-to-r from-orange-500 to-amber-500
                       hover:from-orange-600 hover:to-amber-600 text-white
                       font-semibold py-3 rounded-xl transition-all
                       disabled:opacity-60 disabled:cursor-not-allowed
                       flex items-center justify-center gap-2 mt-2"
          >
            {isSubmitting ? (
              <>
                <svg
                  className="animate-spin h-4 w-4"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Generating Plan...
              </>
            ) : (
              "Generate My Indian Diet Plan →"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
