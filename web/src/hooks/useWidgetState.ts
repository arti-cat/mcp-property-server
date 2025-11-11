import { useState, useEffect, useCallback } from 'react';
import { useOpenAiGlobal } from './useOpenAiGlobal';
import type { WidgetState } from '../types/property';

/**
 * Hook to manage widget state that persists across sessions
 * State is stored in ChatGPT and rehydrated when the widget loads
 */
export function useWidgetState(
  defaultState: WidgetState
): readonly [WidgetState, (state: WidgetState | ((prev: WidgetState) => WidgetState)) => void] {
  const widgetStateFromWindow = useOpenAiGlobal('widgetState');

  const [widgetState, _setWidgetState] = useState<WidgetState>(() => {
    if (widgetStateFromWindow != null) {
      return widgetStateFromWindow;
    }
    return defaultState;
  });

  // Sync with window.openai.widgetState when it changes
  useEffect(() => {
    if (widgetStateFromWindow != null) {
      _setWidgetState(widgetStateFromWindow);
    }
  }, [widgetStateFromWindow]);

  const setWidgetState = useCallback(
    (state: WidgetState | ((prev: WidgetState) => WidgetState)) => {
      _setWidgetState((prevState) => {
        const newState = typeof state === 'function' ? state(prevState) : state;
        
        // Persist to ChatGPT
        if (window.openai?.setWidgetState) {
          window.openai.setWidgetState(newState);
        }
        
        return newState;
      });
    },
    []
  );

  return [widgetState, setWidgetState] as const;
}
