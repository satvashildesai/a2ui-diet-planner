interface MealSlot {
  time: string;
  slot_name: string;
  dish_name: string;
  portion: string;
  calories: number;
  protein_g: number;
  recipe_tip: string;
}

interface Props {
  goal?: string | null;
  calorie_target?: number | null;
  bmi?: number | null;
  dietary_preference?: string | null;
  meals?: MealSlot[] | null;
  hydration_tip?: string | null;
  general_notes?: string[] | null;
}

const ICONS: Record<string, string> = {
  "Morning Breakfast": "🌅",
  "Mid-Morning Snack": "🍎",
  Lunch: "🍱",
  "Evening Snack": "☕",
  Dinner: "🌙",
};

const getBMIStatus = (bmi: number) => {
  if (bmi < 18.5) return { label: "Underweight", color: "text-blue-300" };
  if (bmi <= 24.9) return { label: "Normal", color: "text-green-300" };
  if (bmi <= 29.9) return { label: "Overweight", color: "text-yellow-300" };
  return { label: "Obese", color: "text-red-300" };
};

export function DietPlanCard({
  goal,
  calorie_target,
  bmi,
  dietary_preference,
  meals,
  hydration_tip,
  general_notes,
}: Props) {
  // Defensive: wait until all required data is present
  if (!goal || !calorie_target || !meals || meals.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-orange-100 shadow-sm p-8 text-center">
        <div className="text-3xl mb-3">🥗</div>
        <p className="text-gray-400 text-sm">Loading your diet plan...</p>
      </div>
    );
  }

  const goalLabel = goal.replace(/_/g, " ");
  const bmiValue = bmi ?? 0;
  const bmiStatus = getBMIStatus(bmiValue);

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-orange-100 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-800 to-teal-700 p-5 text-white">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-bold">Your Personalised Diet Plan</h2>
            <p className="text-green-200 text-sm mt-1 capitalize">
              Goal: {goalLabel}
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold">{calorie_target}</p>
            <p className="text-green-200 text-xs mt-0.5">kcal / day</p>
          </div>
        </div>
        <div className="flex gap-2 mt-3 flex-wrap">
          {bmi && (
            <span className="bg-white/15 border border-white/25 px-3 py-1 rounded-full text-xs">
              BMI: {bmiValue}{" "}
              <span className={bmiStatus.color}>({bmiStatus.label})</span>
            </span>
          )}
          {dietary_preference && (
            <span className="bg-white/15 border border-white/25 px-3 py-1 rounded-full text-xs capitalize">
              {dietary_preference}
            </span>
          )}
        </div>
      </div>

      {/* Meals */}
      <div className="divide-y divide-orange-50">
        {meals.map((meal, i) => (
          <div key={i} className="p-4 hover:bg-orange-50/50 transition-colors">
            <div className="flex items-start gap-3">
              <span className="text-2xl mt-0.5 flex-shrink-0">
                {ICONS[meal.slot_name] || "🍽️"}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center gap-2">
                  <span className="text-[10px] font-bold text-orange-500 uppercase tracking-wider">
                    {meal.slot_name}
                  </span>
                  <span className="text-[10px] text-gray-400 flex-shrink-0">
                    {meal.time}
                  </span>
                </div>
                <p className="font-semibold text-gray-800 text-sm mt-0.5 leading-snug">
                  {meal.dish_name}
                </p>
                <div className="flex items-center gap-1.5 mt-1 flex-wrap">
                  <span className="text-xs text-gray-400">{meal.portion}</span>
                  <span className="text-gray-300 text-xs">·</span>
                  <span className="text-xs font-semibold text-orange-600">
                    {meal.calories} kcal
                  </span>
                  <span className="text-gray-300 text-xs">·</span>
                  <span className="text-xs text-teal-600 font-medium">
                    {meal.protein_g}g protein
                  </span>
                </div>
                {meal.recipe_tip && (
                  <div className="mt-2 bg-blue-50 border-l-2 border-blue-300 px-2.5 py-1.5 rounded-r-lg">
                    <p className="text-xs text-blue-700 italic">
                      💡 {meal.recipe_tip}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      {(hydration_tip || (general_notes && general_notes.length > 0)) && (
        <div className="bg-amber-50 border-t border-orange-100 p-4">
          {hydration_tip && (
            <p className="text-sm text-blue-700 mb-2">💧 {hydration_tip}</p>
          )}
          {general_notes && (
            <div className="space-y-1">
              {general_notes.map((note, i) => (
                <p key={i} className="text-xs text-gray-600 flex gap-1.5">
                  <span className="text-orange-400 flex-shrink-0">•</span>
                  {note}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
