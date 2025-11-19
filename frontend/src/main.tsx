import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { initTheme } from './lib/theme'

// Initialize theme before rendering to prevent flash
initTheme()

// Service worker is automatically registered by vite-plugin-pwa
// Push notification handlers are in the generated service worker

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
