/**
 * A2UI Component Catalog Registration
 * All components must be registered here before the agent can use them.
 * In a real setup, registerComponent comes from @a2ui/react-renderer.
 */

// Mock registration store (in production this would use @a2ui/react-renderer)
const componentRegistry = new Map<string, React.ComponentType<unknown>>();

export const registerComponent = (
  name: string,
  component: React.ComponentType<unknown>
) => {
  componentRegistry.set(name, component);
};

export const getComponent = (name: string) => componentRegistry.get(name);

export const getAllComponents = () =>
  Object.fromEntries(componentRegistry.entries());

import { UserProfileForm } from "./UserProfileForm";
import { DietPlanCard } from "./DietPlanCard";
import { ContextInterruptForm } from "./ContextInterruptForm";
import { ActionButton } from "../components/ActionButton";
import { MealSlotRow } from "../components/MealSlotRow";
import { FoodDetailCard } from "../components/FoodDetailCard";
import { NutritionBadge } from "../components/NutritionBadge";
import { GuardrailCard } from "./GuardrailCard";

// Register all components
registerComponent(
  "UserProfileForm",
  UserProfileForm as React.ComponentType<unknown>
);
registerComponent("DietPlanCard", DietPlanCard as React.ComponentType<unknown>);
registerComponent(
  "ContextInterruptForm",
  ContextInterruptForm as React.ComponentType<unknown>
);
registerComponent(
  "GuardrailCard",
  GuardrailCard as React.ComponentType<unknown>
);
registerComponent(
  "NutritionBadge",
  NutritionBadge as React.ComponentType<unknown>
);
registerComponent("ActionButton", ActionButton as React.ComponentType<unknown>);
registerComponent("MealSlotRow", MealSlotRow as React.ComponentType<unknown>);
registerComponent(
  "FoodDetailCard",
  FoodDetailCard as React.ComponentType<unknown>
);

export {
  UserProfileForm,
  DietPlanCard,
  ContextInterruptForm,
  GuardrailCard,
  NutritionBadge,
  ActionButton,
  MealSlotRow,
  FoodDetailCard,
};
