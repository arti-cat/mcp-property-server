import { useOpenAiGlobal } from './useOpenAiGlobal';
import type { ToolOutput } from '../types/property';

/**
 * Hook to read the tool output from the MCP server
 * This contains the initial property data returned by query_listings
 */
export function useToolOutput(): ToolOutput | null {
  return useOpenAiGlobal('toolOutput');
}
