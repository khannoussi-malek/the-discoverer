import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Database, TrendingUp, Clock, Zap } from "lucide-react"

interface StatsCardsProps {
  databasesCount: number
  analytics?: {
    total_queries?: number
    avg_execution_time?: number
    cache_hit_rate?: number
  }
}

export function StatsCards({ databasesCount, analytics }: StatsCardsProps) {
  const stats = [
    {
      title: "Databases",
      value: databasesCount.toString(),
      icon: Database,
      description: "Registered databases",
    },
    {
      title: "Total Queries",
      value: (analytics?.total_queries || 0).toString(),
      icon: TrendingUp,
      description: "Last 7 days",
    },
    {
      title: "Avg Execution",
      value: analytics?.avg_execution_time
        ? `${analytics.avg_execution_time.toFixed(2)}s`
        : "N/A",
      icon: Clock,
      description: "Average query time",
    },
    {
      title: "Cache Hit Rate",
      value: analytics?.cache_hit_rate
        ? `${(analytics.cache_hit_rate * 100).toFixed(1)}%`
        : "N/A",
      icon: Zap,
      description: "Query cache efficiency",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
            <p className="text-xs text-muted-foreground">{stat.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

