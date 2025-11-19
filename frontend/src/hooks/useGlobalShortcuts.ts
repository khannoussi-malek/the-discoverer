/**
 * Global keyboard shortcuts for the application
 */

import { useNavigate } from 'react-router-dom'
import { useKeyboardShortcuts } from './useKeyboardShortcuts'

export function useGlobalShortcuts() {
  const navigate = useNavigate()

  useKeyboardShortcuts(
    [
      {
        key: '1',
        ctrl: true,
        action: () => navigate('/'),
        description: 'Go to Dashboard',
      },
      {
        key: '2',
        ctrl: true,
        action: () => navigate('/databases'),
        description: 'Go to Databases',
      },
      {
        key: '3',
        ctrl: true,
        action: () => navigate('/query'),
        description: 'Go to Query',
      },
      {
        key: '4',
        ctrl: true,
        action: () => navigate('/dashboards'),
        description: 'Go to Dashboards',
      },
      {
        key: '5',
        ctrl: true,
        action: () => navigate('/templates'),
        description: 'Go to Templates',
      },
      {
        key: '6',
        ctrl: true,
        action: () => navigate('/scheduler'),
        description: 'Go to Scheduler',
      },
      {
        key: '7',
        ctrl: true,
        action: () => navigate('/analytics'),
        description: 'Go to Analytics',
      },
      {
        key: '8',
        ctrl: true,
        action: () => navigate('/webhooks'),
        description: 'Go to Webhooks',
      },
    ],
    true
  )
}

