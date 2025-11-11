import React from 'react';
import { createRoot } from 'react-dom/client';
import { PropertyListWidget } from './PropertyListWidget';
import './styles/index.css';

// Wait for DOM to be ready
function init() {
  const rootElement = document.getElementById('root');
  
  if (!rootElement) {
    console.error('Root element not found');
    return;
  }

  const root = createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <PropertyListWidget />
    </React.StrictMode>
  );
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
