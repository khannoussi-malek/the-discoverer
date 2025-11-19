/**
 * Query Progress Component
 * Displays real-time query execution progress via WebSocket
 */

import { useQueryWebSocket } from "@/hooks/useQueryWebSocket"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Activity, CheckCircle2, XCircle, Clock } from "lucide-react"

interface QueryProgressProps {
  queryId: string | null
  onUpdate?: (status: string) => void
}

export function QueryProgress({ queryId, onUpdate }: QueryProgressProps) {
  const { lastMessage, connectionState, isConnected } = useQueryWebSocket({
    queryId,
    enabled: !!queryId,
    onMessage: (message) => {
      if (message.type === 'query_update' && onUpdate) {
        onUpdate(message.data?.status || 'unknown')
      }
    },
  })

  if (!queryId) {
    return null
  }

  const status = lastMessage?.type === 'query_update' 
    ? lastMessage.data?.status 
    : 'pending'

  const getStatusConfig = () => {
    switch (status) {
      case 'completed':
        return {
          icon: CheckCircle2,
          label: 'Completed',
          variant: 'default' as const,
          color: 'text-green-600',
        }
      case 'failed':
        return {
          icon: XCircle,
          label: 'Failed',
          variant: 'destructive' as const,
          color: 'text-red-600',
        }
      case 'running':
        return {
          icon: Activity,
          label: 'Running',
          variant: 'secondary' as const,
          color: 'text-blue-600',
        }
      default:
        return {
          icon: Clock,
          label: 'Pending',
          variant: 'secondary' as const,
          color: 'text-gray-600',
        }
    }
  }

  const config = getStatusConfig()
  const Icon = config.icon

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">Query Progress</CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant={isConnected ? "default" : "secondary"}>
              {connectionState}
            </Badge>
            <Badge variant={config.variant}>
              <Icon className="mr-1 h-3 w-3" />
              {config.label}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {status === 'running' && (
          <div className="space-y-2">
            <div className="w-full bg-secondary rounded-full h-2">
              <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: '50%' }} />
            </div>
            <p className="text-xs text-muted-foreground">
              Query is executing...
            </p>
          </div>
        )}
        {lastMessage?.type === 'query_update' && (
          <div className="space-y-2 text-sm">
            {lastMessage.data?.total_rows && (
              <div>
                <span className="text-muted-foreground">Total rows: </span>
                <span className="font-medium">{lastMessage.data.total_rows}</span>
              </div>
            )}
            {lastMessage.data?.page && (
              <div>
                <span className="text-muted-foreground">Page: </span>
                <span className="font-medium">
                  {lastMessage.data.page} / {lastMessage.data.page_size || 'N/A'}
                </span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

