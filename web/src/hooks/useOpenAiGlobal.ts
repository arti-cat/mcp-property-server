import { useSyncExternalStore } from 'react';
import type { OpenAiGlobals } from '../types/property';

const SET_GLOBALS_EVENT_TYPE = 'openai:set_globals';

/**
 * Hook to subscribe to a specific window.openai global value
 * Automatically updates when the host dispatches set_globals events
 */
export function useOpenAiGlobal<K extends keyof OpenAiGlobals>(
  key: K
): OpenAiGlobals[K] {
  return useSyncExternalStore(
    (onChange) => {
      const handleSetGlobal = (event: CustomEvent) => {
        const value = event.detail?.globals?.[key];
        if (value !== undefined) {
          onChange();
        }
      };

      window.addEventListener(SET_GLOBALS_EVENT_TYPE, handleSetGlobal as EventListener, {
        passive: true,
      });

      return () => {
        window.removeEventListener(SET_GLOBALS_EVENT_TYPE, handleSetGlobal as EventListener);
      };
    },
    () => window.openai?.[key]
  );
}
