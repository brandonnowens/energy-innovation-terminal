import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary.tsx'

// Production API Base URL
export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'https://energy-innovation-api.onrender.com').replace(/\/+$/, '');

// Intercept all relative /api requests and route directly to live backend
const originalFetch = window.fetch;
window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  if (typeof input === 'string') {
    if (input.startsWith('/api/') || input.startsWith('/api?') || input === '/api') {
      input = `${API_BASE_URL}${input}`;
    }
  } else if (input instanceof URL) {
    if ((input.pathname.startsWith('/api/') || input.pathname === '/api') && input.origin === window.location.origin) {
      input = new URL(`${API_BASE_URL}${input.pathname}${input.search}`);
    }
  } else if (input instanceof Request) {
    const url = new URL(input.url);
    if ((url.pathname.startsWith('/api/') || url.pathname === '/api') && url.origin === window.location.origin) {
      const newUrl = `${API_BASE_URL}${url.pathname}${url.search}`;
      input = new Request(newUrl, input);
    }
  }
  return originalFetch(input, init);
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)

