import { useHealth } from "@/hooks/useHealth"
import { useDatabases } from "@/hooks/useDatabases"
import { useAnalyticsStats } from "@/hooks/useAnalytics"
import { StatsCards } from "./StatsCards"
import { SystemStatus } from "./SystemStatus"
import { QuickActions } from "./QuickActions"
import { NotificationSettings } from "@/components/shared/NotificationSettings"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"
import { ErrorMessage } from "@/components/shared/ErrorMessage"

export function DashboardPage() {
  const { data: health, isLoading: healthLoading, error: healthError } = useHealth()
  const { data: databases, isLoading: databasesLoading } = useDatabases()
  const { data: analytics, isLoading: analyticsLoading } = useAnalyticsStats(7)

  if (healthLoading || databasesLoading || analyticsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (healthError) {
    return <ErrorMessage message="Failed to load dashboard data" />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your system status and statistics
        </p>
      </div>

      <SystemStatus health={health} />

      <StatsCards
        databasesCount={databases?.length || 0}
        analytics={analytics}
      />

      <QuickActions />

      <NotificationSettings />
    </div>
  )
}

