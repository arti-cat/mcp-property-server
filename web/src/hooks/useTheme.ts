import { useOpenAiGlobal } from './useOpenAiGlobal';

/**
 * Hook to get the current theme (light or dark)
 * Automatically updates when user switches theme in ChatGPT
 */
export function useTheme(): 'light' | 'dark' {
  return useOpenAiGlobal('theme') || 'light';
}
