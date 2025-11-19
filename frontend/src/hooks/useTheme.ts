/**
 * Custom hook for theme management
 */

import { useState, useEffect } from 'react'
import { getTheme, setTheme, applyTheme, getEffectiveTheme, type Theme } from '@/lib/theme'

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => getTheme())
  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>(() => getEffectiveTheme())

  useEffect(() => {
    // Initialize theme on mount
    applyTheme(theme)
    setEffectiveTheme(getEffectiveTheme())

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      if (theme === 'system') {
        setEffectiveTheme(getEffectiveTheme())
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  const updateTheme = (newTheme: Theme) => {
    setTheme(newTheme)
    setThemeState(newTheme)
    setEffectiveTheme(getEffectiveTheme())
  }

  const toggleTheme = () => {
    const current = getEffectiveTheme()
    updateTheme(current === 'dark' ? 'light' : 'dark')
  }

  return {
    theme,
    effectiveTheme,
    setTheme: updateTheme,
    toggleTheme,
  }
}

