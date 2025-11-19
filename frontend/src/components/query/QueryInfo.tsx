import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { QueryResponse } from "@/types/query"

interface QueryInfoProps {
  result: QueryResponse
}

export function QueryInfo({ result }: QueryInfoProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="grid gap-4 md:grid-cols-4">
          <div>
            <div className="text-sm text-muted-foreground">Query ID</div>
            <div className="text-sm font-medium">{result.query_id}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Execution Time</div>
            <div className="text-sm font-medium">
              {result.execution_time.toFixed(2)}s
            </div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Total Rows</div>
            <div className="text-sm font-medium">{result.total_rows}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Databases</div>
            <div className="flex gap-1 mt-1">
              {result.databases_queried?.map((db) => (
                <Badge key={db} variant="outline">
                  {db}
                </Badge>
              ))}
            </div>
          </div>
        </div>
        {result.cached && (
          <div className="mt-4">
            <Badge variant="secondary">Cached Result</Badge>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

