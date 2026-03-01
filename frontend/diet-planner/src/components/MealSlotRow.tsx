// MealSlotRow
interface MealSlotRowProps {
  time: string;
  slot_name: string;
  dish_name: string;
  portion: string;
  calories: number;
  protein_g: number;
  recipe_tip?: string;
}

const SLOT_ICONS: Record<string, string> = {
  "Morning Breakfast": "🌅",
  "Mid-Morning Snack": "🍎",
  Lunch: "🍱",
  "Evening Snack": "☕",
  Dinner: "🌙",
};

export function MealSlotRow({
  time,
  slot_name,
  dish_name,
  portion,
  calories,
  protein_g,
  recipe_tip,
}: MealSlotRowProps) {
  return (
    <div className="flex items-start gap-3 p-3 hover:bg-orange-50/40 rounded-xl transition-colors">
      <span className="text-2xl">{SLOT_ICONS[slot_name] || "🍽️"}</span>
      <div className="flex-1 min-w-0">
        <div className="flex justify-between">
          <span className="text-[10px] font-bold text-orange-500 uppercase tracking-wider">
            {slot_name}
          </span>
          <span className="text-[10px] text-gray-400">{time}</span>
        </div>
        <p className="font-semibold text-gray-800 text-sm mt-0.5">
          {dish_name}
        </p>
        <div className="flex gap-2 items-center mt-1">
          <span className="text-xs text-gray-400">{portion}</span>
          <span className="text-orange-600 font-semibold text-xs">
            {calories} kcal
          </span>
          <span className="text-teal-600 text-xs">{protein_g}g prot</span>
        </div>
        {recipe_tip && (
          <p className="text-xs text-blue-600 italic mt-1.5">💡 {recipe_tip}</p>
        )}
      </div>
    </div>
  );
}
