import { useState } from "react"
import { useExecuteQuery } from "@/hooks/useQuery"
import type { QueryResponse } from "@/types/query"
import { extractErrorMessage } from "@/lib/errorHandler"
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from "@/lib/messages"
import { QueryInput } from "./QueryInput"
import { DatabaseSelector } from "./DatabaseSelector"
import { QueryResults } from "./QueryResults"
import { QueryInfo } from "./QueryInfo"
import { ChartControls } from "@/components/visualization/ChartControls"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/use-toast"
import { Card } from "@/components/ui/card"

export function QueryPage() {
  const [query, setQuery] = useState("")
  const [selectedDatabases, setSelectedDatabases] = useState<string[]>([])
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null)
  const { toast } = useToast()

  const executeMutation = useExecuteQuery()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) {
      toast({
        title: "Error",
        description: ERROR_MESSAGES.QUERY_REQUIRED,
        variant: "destructive",
      })
      return
    }

    executeMutation.mutate(
      {
        query: query.trim(),
        database_ids: selectedDatabases.length > 0 ? selectedDatabases : undefined,
      },
      {
        onSuccess: (data) => {
          setQueryResult(data)
          toast({
            title: SUCCESS_MESSAGES.QUERY_EXECUTED,
            description: `Retrieved ${data.total_rows} rows in ${data.execution_time.toFixed(2)}s`,
          })
        },
        onError: (error: unknown) => {
          toast({
            title: "Query failed",
            description: extractErrorMessage(error) || ERROR_MESSAGES.QUERY_EXECUTION_FAILED,
            variant: "destructive",
          })
        },
      }
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Query</h1>
        <p className="text-muted-foreground">
          Execute natural language queries on your databases
        </p>
      </div>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <DatabaseSelector
            selected={selectedDatabases}
            onChange={setSelectedDatabases}
          />
          <QueryInput value={query} onChange={setQuery} />
          <Button type="submit" disabled={executeMutation.isPending}>
            {executeMutation.isPending ? "Executing..." : "Execute Query"}
          </Button>
        </form>
      </Card>

      {queryResult && (
        <>
          <QueryInfo result={queryResult} />
          <QueryResults data={queryResult.data || queryResult.results || []} queryId={queryResult.query_id} />
          <ChartControls
            queryId={queryResult.query_id}
            data={queryResult.data || queryResult.results || []}
          />
        </>
      )}
    </div>
  )
}

