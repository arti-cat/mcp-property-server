// TypeScript interfaces for property data

export interface Property {
  property_id: string;
  ld_name: string;
  ld_image: string;
  ld_photos?: string[];
  price_text: string;
  price_amount: number;
  bedrooms: number;
  bathrooms: number;
  property_type: string;
  postcode: string;
  garden: boolean;
  parking: boolean;
  status: string;
  overview?: string[];
  description?: string;
  detail_url: string;
  lat?: string;
  lng?: string;
}

export interface ToolOutput {
  properties: Property[];
  filters_applied?: {
    postcode?: string;
    property_type?: string;
    max_price?: number;
    min_bedrooms?: number;
    has_garden?: boolean;
    has_parking?: boolean;
  };
  total_results?: number;
  showing?: number;
}

export interface WidgetState {
  favorites: string[];
  hidden: string[];
  sortBy: 'price_asc' | 'price_desc' | 'bedrooms_desc';
}

// window.openai API types
export interface OpenAiGlobals {
  theme: 'light' | 'dark';
  toolOutput: ToolOutput | null;
  widgetState: WidgetState | null;
  displayMode: 'inline' | 'pip' | 'fullscreen';
  maxHeight: number;
}

export interface OpenAiAPI {
  callTool: (name: string, args: Record<string, unknown>) => Promise<any>;
  setWidgetState: (state: WidgetState) => Promise<void>;
  sendFollowUpMessage: (args: { prompt: string }) => Promise<void>;
  requestDisplayMode: (args: { mode: 'inline' | 'pip' | 'fullscreen' }) => Promise<{ mode: string }>;
  openExternal: (payload: { href: string }) => void;
}

declare global {
  interface Window {
    openai: OpenAiAPI & OpenAiGlobals;
  }
}
