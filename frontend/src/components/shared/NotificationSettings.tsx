/**
 * Notification Settings Component
 * Allows users to enable/disable push notifications
 */

import { useNotifications } from "@/hooks/useNotifications"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Bell, BellOff, CheckCircle2, XCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

export function NotificationSettings() {
  const { permission, isSupported, hasPermission, requestPermission } = useNotifications()

  const handleToggle = async () => {
    if (!hasPermission) {
      await requestPermission()
    }
  }

  if (!isSupported) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BellOff className="h-5 w-5" />
            Notifications Not Supported
          </CardTitle>
          <CardDescription>
            Your browser does not support push notifications
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Push Notifications
        </CardTitle>
        <CardDescription>
          Receive notifications for query updates, database syncs, and other important events
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="font-medium">Enable Notifications</span>
              {permission === 'granted' && (
                <Badge variant="default" className="bg-green-600">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  Enabled
                </Badge>
              )}
              {permission === 'denied' && (
                <Badge variant="destructive">
                  <XCircle className="h-3 w-3 mr-1" />
                  Blocked
                </Badge>
              )}
              {permission === 'default' && (
                <Badge variant="secondary">Not Set</Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
              {permission === 'granted'
                ? 'You will receive notifications for important events'
                : permission === 'denied'
                ? 'Notifications are blocked. Please enable them in your browser settings.'
                : 'Click the button below to enable notifications'}
            </p>
          </div>
          <Switch checked={hasPermission} onCheckedChange={handleToggle} />
        </div>

        {permission === 'default' && (
          <Button onClick={requestPermission} className="w-full">
            <Bell className="mr-2 h-4 w-4" />
            Enable Notifications
          </Button>
        )}

        {permission === 'denied' && (
          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              To enable notifications, please:
            </p>
            <ol className="list-decimal list-inside mt-2 text-sm text-muted-foreground space-y-1">
              <li>Click the lock icon in your browser's address bar</li>
              <li>Find "Notifications" in the permissions list</li>
              <li>Change it from "Block" to "Allow"</li>
              <li>Refresh this page</li>
            </ol>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

