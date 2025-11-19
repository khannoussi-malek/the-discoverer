import { useAnalyticsStats, useTopQueries } from "@/hooks/useAnalytics"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"
import { ErrorMessage } from "@/components/shared/ErrorMessage"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export function AnalyticsPage() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useAnalyticsStats(7)
  const { data: topQueries, isLoading: topQueriesLoading } = useTopQueries(10, 7)

  if (statsLoading || topQueriesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (statsError) {
    return <ErrorMessage message="Failed to load analytics" />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="text-muted-foreground">
          View usage statistics and insights
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Queries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_queries || 0}
            </div>
            <p className="text-xs text-muted-foreground">Last 7 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Avg Execution Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.avg_execution_time
                ? `${stats.avg_execution_time.toFixed(2)}s`
                : "N/A"}
            </div>
            <p className="text-xs text-muted-foreground">Last 7 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Cache Hit Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.cache_hit_rate
                ? `${(stats.cache_hit_rate * 100).toFixed(1)}%`
                : "N/A"}
            </div>
            <p className="text-xs text-muted-foreground">Efficiency</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top Queries</CardTitle>
        </CardHeader>
        <CardContent>
          {topQueries && topQueries.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Query</TableHead>
                  <TableHead>Count</TableHead>
                  <TableHead>Avg Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {topQueries.map((query, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-mono text-sm">
                      {query.query}
                    </TableCell>
                    <TableCell>{query.count}</TableCell>
                    <TableCell>
                      {query.avg_execution_time.toFixed(2)}s
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center text-muted-foreground py-8">
              No query data available
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

