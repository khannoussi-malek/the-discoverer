import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, XCircle, AlertTriangle } from "lucide-react"

interface SystemStatusProps {
  health?: {
    status: "healthy" | "degraded" | "unhealthy" | "unknown"
    services?: Record<string, string>
  }
}

export function SystemStatus({ health }: SystemStatusProps) {
  const status = health?.status || "unknown"

  const statusConfig = {
    healthy: {
      icon: CheckCircle2,
      label: "Healthy",
      variant: "default" as const,
      color: "text-green-600",
    },
    degraded: {
      icon: AlertTriangle,
      label: "Degraded",
      variant: "secondary" as const,
      color: "text-yellow-600",
    },
    unhealthy: {
      icon: XCircle,
      label: "Unhealthy",
      variant: "destructive" as const,
      color: "text-red-600",
    },
    unknown: {
      icon: AlertTriangle,
      label: "Unknown",
      variant: "secondary" as const,
      color: "text-gray-600",
    },
  }

  const config = statusConfig[status] || statusConfig.unknown
  const Icon = config.icon

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <Icon className={`h-8 w-8 ${config.color}`} />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-semibold">Status:</span>
              <Badge variant={config.variant}>{config.label}</Badge>
            </div>
            {health?.services && (
              <div className="mt-2 space-y-1">
                {Object.entries(health.services).map(([service, status]) => (
                  <div key={service} className="text-sm text-muted-foreground">
                    <span className="font-medium">{service}:</span> {status}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

