/**
 * Webhook Statistics Component
 * Displays webhook statistics including success/failure counts and rates
 */

import { useWebhookStats } from "@/hooks/useWebhooks"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"
import { ErrorMessage } from "@/components/shared/ErrorMessage"
import { CheckCircle2, XCircle, Clock, TrendingUp } from "lucide-react"

interface WebhookStatsProps {
  webhookId: string
}

export function WebhookStats({ webhookId }: WebhookStatsProps) {
  const { data: stats, isLoading, error } = useWebhookStats(webhookId)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return <ErrorMessage message="Failed to load webhook statistics" />
  }

  if (!stats) {
    return (
      <div className="text-center text-muted-foreground py-8">
        No statistics available
      </div>
    )
  }

  const successRate = stats.success_rate || 0
  const totalAttempts = stats.total_attempts || 0

  const getHealthBadge = () => {
    if (successRate >= 0.95) {
      return <Badge variant="default" className="bg-green-600">Excellent</Badge>
    }
    if (successRate >= 0.8) {
      return <Badge variant="default" className="bg-yellow-600">Good</Badge>
    }
    return <Badge variant="destructive">Poor</Badge>
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              Success Count
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.success_count || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-600" />
              Failure Count
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.failure_count || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Success Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(successRate * 100).toFixed(1)}%
            </div>
            {getHealthBadge()}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Total Attempts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalAttempts}</div>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-2 text-sm">
        {stats.last_triggered && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Last Triggered:</span>
            <span className="font-medium">
              {new Date(stats.last_triggered).toLocaleString()}
            </span>
          </div>
        )}
        {stats.last_success && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Last Success:</span>
            <span className="font-medium text-green-600">
              {new Date(stats.last_success).toLocaleString()}
            </span>
          </div>
        )}
        {stats.last_failure && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Last Failure:</span>
            <span className="font-medium text-red-600">
              {new Date(stats.last_failure).toLocaleString()}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

