// FoodDetailCard
interface FoodDetailCardProps {
  food_name: string;
  calories_per_serving?: number;
  macros?: { protein?: number; carbs?: number; fat?: number; fiber?: number };
  benefits?: string[];
  drawbacks?: string[];
  verdict_for_user?: string;
}

export function FoodDetailCard({
  food_name,
  calories_per_serving,
  macros = {},
  benefits = [],
  drawbacks = [],
  verdict_for_user,
}: FoodDetailCardProps) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-md p-5">
      <h3 className="font-bold text-lg text-gray-800 capitalize mb-3">
        🔍 {food_name} Analysis
      </h3>

      {verdict_for_user && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-4">
          <p className="text-sm text-gray-700 leading-relaxed">
            {verdict_for_user}
          </p>
        </div>
      )}

      {calories_per_serving && (
        <div className="grid grid-cols-4 gap-2 mb-4">
          {[
            {
              label: "Calories",
              value: `${calories_per_serving}`,
              unit: "kcal",
            },
            { label: "Protein", value: `${macros.protein ?? "—"}`, unit: "g" },
            { label: "Carbs", value: `${macros.carbs ?? "—"}`, unit: "g" },
            { label: "Fat", value: `${macros.fat ?? "—"}`, unit: "g" },
          ].map(({ label, value, unit }) => (
            <div
              key={label}
              className="bg-gray-50 rounded-xl p-2.5 text-center"
            >
              <p className="font-bold text-gray-800 text-base">
                {value}
                <span className="text-xs font-normal text-gray-400 ml-0.5">
                  {unit}
                </span>
              </p>
              <p className="text-[10px] text-gray-400 uppercase tracking-wide mt-0.5">
                {label}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        {benefits.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">
              ✅ Benefits
            </h4>
            {benefits.map((b, i) => (
              <p key={i} className="text-xs text-gray-700 flex gap-1.5 mb-1">
                <span className="text-green-500 flex-shrink-0">✓</span>
                {b}
              </p>
            ))}
          </div>
        )}
        {drawbacks.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">
              ⚠️ Watch Out
            </h4>
            {drawbacks.map((d, i) => (
              <p key={i} className="text-xs text-gray-700 flex gap-1.5 mb-1">
                <span className="text-amber-500 flex-shrink-0">!</span>
                {d}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
