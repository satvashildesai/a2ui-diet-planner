// NutritionBadge
interface NutritionBadgeProps {
  protein?: number;
  carbs?: number;
  fat?: number;
  fiber?: number;
  calories?: number;
}

export function NutritionBadge({
  protein,
  carbs,
  fat,
  fiber,
  calories,
}: NutritionBadgeProps) {
  const items = [
    {
      label: "Cal",
      value: calories,
      unit: "kcal",
      color: "bg-orange-100 text-orange-700",
    },
    {
      label: "Protein",
      value: protein,
      unit: "g",
      color: "bg-teal-100 text-teal-700",
    },
    {
      label: "Carbs",
      value: carbs,
      unit: "g",
      color: "bg-amber-100 text-amber-700",
    },
    { label: "Fat", value: fat, unit: "g", color: "bg-red-100 text-red-700" },
    {
      label: "Fiber",
      value: fiber,
      unit: "g",
      color: "bg-green-100 text-green-700",
    },
  ].filter((i) => i.value !== undefined);

  return (
    <div className="flex gap-2 flex-wrap">
      {items.map(({ label, value, unit, color }) => (
        <span
          key={label}
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${color}`}
        >
          {label}: {value}
          {unit}
        </span>
      ))}
    </div>
  );
}
