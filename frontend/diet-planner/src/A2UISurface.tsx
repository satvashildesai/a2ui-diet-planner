/**
 * A2UISurface - Lightweight A2UI renderer
 * Processes surfaceUpdate, dataModelUpdate, and beginRendering messages
 * and renders the appropriate catalog components.
 *
 * Key fix: All three messages are buffered and committed atomically only
 * when beginRendering fires. This prevents components from rendering with
 * null/undefined props due to the surfaceUpdate arriving before dataModelUpdate.
 */

import React, { useState, useEffect, useRef } from "react";
import { registerA2UIDispatcher } from "./hooks/useAgentSSE";
import { getComponent } from "./catalog";

interface Props {
  surfaceId: string;
}

type DataValue =
  | string
  | number
  | boolean
  | DataValue[]
  | { [key: string]: DataValue }
  | null;
type DataModel = Record<string, DataValue>;
type ComponentDef = {
  [componentName: string]: Record<
    string,
    {
      path?: string;
      literalString?: string;
      literalInt?: number;
      literalFloat?: number;
      literalBool?: boolean;
    }
  >;
};
type ComponentTree = Record<string, ComponentDef>;

const resolvePath = (path: string, dataModel: DataModel): DataValue => {
  const parts = path.replace(/^\//, "").split("/");
  let current: DataValue = dataModel;
  for (const part of parts) {
    if (
      current === null ||
      typeof current !== "object" ||
      Array.isArray(current)
    )
      return null;
    current = (current as Record<string, DataValue>)[part] ?? null;
  }
  return current;
};

const resolveValue = (
  binding: {
    path?: string;
    literalString?: string;
    literalInt?: number;
    literalFloat?: number;
    literalBool?: boolean;
  },
  dataModel: DataModel
): DataValue => {
  if (binding.path !== undefined) return resolvePath(binding.path, dataModel);
  if (binding.literalString !== undefined) return binding.literalString;
  if (binding.literalInt !== undefined) return binding.literalInt;
  if (binding.literalFloat !== undefined) return binding.literalFloat;
  if (binding.literalBool !== undefined) return binding.literalBool;
  return null;
};

const parseContents = (contents: unknown[]): DataModel => {
  const result: DataModel = {};
  for (const item of contents as Record<string, unknown>[]) {
    const key = item.key as string;
    if (item.valueString !== undefined)
      result[key] = item.valueString as string;
    else if (item.valueInt !== undefined) result[key] = item.valueInt as number;
    else if (item.valueFloat !== undefined)
      result[key] = item.valueFloat as number;
    else if (item.valueBool !== undefined)
      result[key] = item.valueBool as boolean;
    else if (item.valueStringList !== undefined)
      result[key] = item.valueStringList as string[];
    else if (item.valueIntList !== undefined)
      result[key] = item.valueIntList as number[];
    else if (item.valueMap !== undefined)
      result[key] = parseContents(item.valueMap as unknown[]);
    else if (item.valueMapList !== undefined) {
      result[key] = (item.valueMapList as Array<{ valueMap: unknown[] }>).map(
        (mapItem) => parseContents(mapItem.valueMap)
      );
    }
  }
  return result;
};

export function A2UISurface({ surfaceId }: Props) {
  const [componentTree, setComponentTree] = useState<ComponentTree>({});
  const [dataModel, setDataModel] = useState<DataModel>({});
  const [rootId, setRootId] = useState<string | null>(null);

  // Staging refs - accumulate updates without triggering renders
  const pendingTree = useRef<ComponentTree | null>(null);
  const pendingData = useRef<DataModel | null>(null);
  const committedData = useRef<DataModel>({});

  useEffect(() => {
    committedData.current = dataModel;
  }, [dataModel]);

  useEffect(() => {
    const dispatcher = (msg: Record<string, unknown>) => {
      // Stage new component layout
      if (msg.surfaceUpdate) {
        const update = msg.surfaceUpdate as {
          surfaceId: string;
          components: Array<{ id: string; component: ComponentDef }>;
        };
        if (update.surfaceId !== surfaceId) return;
        const newTree: ComponentTree = {};
        for (const comp of update.components) {
          newTree[comp.id] = comp.component;
        }
        pendingTree.current = newTree;
      }

      // Stage data updates - merge into pending or committed base
      if (msg.dataModelUpdate) {
        const update = msg.dataModelUpdate as {
          surfaceId: string;
          contents: unknown[];
        };
        if (update.surfaceId !== surfaceId) return;

        const base: DataModel = pendingData.current
          ? { ...pendingData.current }
          : { ...committedData.current };

        for (const item of update.contents as Record<string, unknown>[]) {
          const key = item.key as string;
          if (item.valueMap !== undefined) {
            base[key] = parseContents(item.valueMap as unknown[]);
          } else {
            const parsed = parseContents([item]);
            if (key in parsed) base[key] = parsed[key];
          }
        }
        pendingData.current = base;
      }

      // Commit everything atomically when beginRendering fires
      if (msg.beginRendering) {
        const br = msg.beginRendering as { surfaceId: string; root: string };
        if (br.surfaceId !== surfaceId) return;

        if (pendingTree.current !== null) {
          setComponentTree(pendingTree.current);
          pendingTree.current = null;
        }
        if (pendingData.current !== null) {
          setDataModel(pendingData.current);
          committedData.current = pendingData.current;
          pendingData.current = null;
        }
        setRootId(br.root);
      }
    };

    registerA2UIDispatcher(dispatcher);
  }, [surfaceId]);

  if (!rootId || !componentTree[rootId]) return null;

  const renderComponent = (compId: string): React.ReactNode => {
    const compDef = componentTree[compId];
    if (!compDef) return null;

    const componentName = Object.keys(compDef)[0];

    if (componentName === "Column") {
      const children =
        (compDef.Column as { children?: string[] }).children || [];
      return (
        <div key={compId} className="space-y-4">
          {children.map((childId: string) => renderComponent(childId))}
        </div>
      );
    }
    if (componentName === "Row") {
      const children = (compDef.Row as { children?: string[] }).children || [];
      return (
        <div key={compId} className="flex gap-3 flex-wrap">
          {children.map((childId: string) => renderComponent(childId))}
        </div>
      );
    }

    const Component = getComponent(componentName);
    if (!Component) {
      console.warn(`A2UI: Component "${componentName}" not registered`);
      return null;
    }

    const rawProps = compDef[componentName] as Record<
      string,
      {
        path?: string;
        literalString?: string;
        literalInt?: number;
        literalFloat?: number;
        literalBool?: boolean;
      }
    >;
    const resolvedProps: Record<string, DataValue> = {};
    for (const [propName, binding] of Object.entries(rawProps)) {
      resolvedProps[propName] = resolveValue(binding, dataModel);
    }

    return <Component key={compId} {...resolvedProps} />;
  };

  return (
    <div className="a2ui-surface animate-fade-in">
      {renderComponent(rootId)}
    </div>
  );
}
