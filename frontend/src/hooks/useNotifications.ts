/**
 * Custom hook for managing notifications
 */

import { useEffect, useState, useCallback } from 'react'
import {
  requestNotificationPermission,
  showNotification,
  isNotificationSupported,
  hasNotificationPermission,
  type NotificationOptions,
} from '@/lib/notifications'
import { useToast } from '@/components/ui/use-toast'

export function useNotifications() {
  const [permission, setPermission] = useState<NotificationPermission>(
    typeof window !== 'undefined' && 'Notification' in window
      ? Notification.permission
      : 'default'
  )
  const [isSupported, setIsSupported] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    setIsSupported(isNotificationSupported())
    if ('Notification' in window) {
      setPermission(Notification.permission)
    }
  }, [])

  const requestPermission = useCallback(async () => {
    const newPermission = await requestNotificationPermission()
    setPermission(newPermission)
    if (newPermission === 'granted') {
      toast({
        title: 'Notifications Enabled',
        description: 'You will now receive notifications for important events',
      })
    } else if (newPermission === 'denied') {
      toast({
        title: 'Notifications Disabled',
        description: 'Please enable notifications in your browser settings',
        variant: 'destructive',
      })
    }
    return newPermission
  }, [toast])

  const sendNotification = useCallback(
    async (options: NotificationOptions) => {
      if (!isSupported) {
        toast({
          title: 'Not Supported',
          description: 'Notifications are not supported in this browser',
          variant: 'destructive',
        })
        return
      }

      if (!hasNotificationPermission()) {
        const granted = await requestPermission()
        if (granted !== 'granted') {
          return
        }
      }

      await showNotification(options)
    },
    [isSupported, requestPermission, toast]
  )

  return {
    permission,
    isSupported,
    hasPermission: hasNotificationPermission(),
    requestPermission,
    sendNotification,
  }
}

