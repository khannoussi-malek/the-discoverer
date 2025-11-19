import { useState, useEffect, Suspense, lazy, useRef } from "react"
import { useExecuteQuery } from "@/hooks/useQuery"
import { useQueryWebSocket } from "@/hooks/useQueryWebSocket"
import { useNotifications } from "@/hooks/useNotifications"
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts"
import type { QueryResponse } from "@/types/query"
import { extractErrorMessage } from "@/lib/errorHandler"
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from "@/lib/messages"
import { QueryInput } from "./QueryInput"
import { DatabaseSelector } from "./DatabaseSelector"
import { QueryResults } from "./QueryResults"
import { QueryInfo } from "./QueryInfo"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/use-toast"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"
import { Kbd, KbdGroup } from "@/components/ui/kbd"

// Lazy load ChartControls since it includes heavy Recharts library
const ChartControls = lazy(() => import("@/components/visualization/ChartControls").then(module => ({ default: module.ChartControls })))

export function QueryPage() {
  const [query, setQuery] = useState("")
  const [selectedDatabases, setSelectedDatabases] = useState<string[]>([])
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null)
  const [currentQueryId, setCurrentQueryId] = useState<string | null>(null)
  const { toast } = useToast()
  const { sendNotification } = useNotifications()
  const formRef = useRef<HTMLFormElement>(null)

  const executeMutation = useExecuteQuery()

  // Keyboard shortcut: Ctrl+Enter to execute query
  useKeyboardShortcuts(
    [
      {
        key: 'Enter',
        ctrl: true,
        action: () => {
          if (query.trim() && formRef.current) {
            formRef.current.requestSubmit()
          }
        },
        description: 'Execute query',
        preventDefault: true,
      },
    ],
    true
  )

  // WebSocket connection for real-time query updates
  const { lastMessage, connectionState, isConnected } = useQueryWebSocket({
    queryId: currentQueryId,
    enabled: !!currentQueryId,
    onMessage: (message) => {
      if (message.type === 'query_update') {
        // Handle query update notifications
        toast({
          title: "Query Update",
          description: `Query status: ${message.data?.status || 'updated'}`,
        })
        
        // Send push notification
        sendNotification({
          title: "Query Update",
          body: `Query ${message.data?.status || 'updated'}: ${message.data?.total_rows ? `${message.data.total_rows} rows` : 'Processing...'}`,
          tag: `query-${currentQueryId}`,
          url: `/query`,
          data: { queryId: currentQueryId },
        })
      }
    },
  })

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage?.type === 'query_update' && queryResult) {
      // Update query result if needed based on WebSocket message
      // This could be used for real-time progress updates
    }
  }, [lastMessage, queryResult])

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
          // Set query ID for WebSocket subscription
          if (data.query_id) {
            setCurrentQueryId(data.query_id)
          }
          toast({
            title: SUCCESS_MESSAGES.QUERY_EXECUTED,
            description: `Retrieved ${data.total_rows} rows in ${data.execution_time.toFixed(2)}s`,
          })
          
          // Send push notification for query completion
          sendNotification({
            title: "Query Completed",
            body: `Retrieved ${data.total_rows} rows in ${data.execution_time.toFixed(2)}s`,
            tag: `query-${data.query_id}`,
            url: `/query`,
            data: { queryId: data.query_id },
          })
        },
        onError: (error: unknown) => {
          const errorMsg = extractErrorMessage(error) || ERROR_MESSAGES.QUERY_EXECUTION_FAILED
          toast({
            title: "Query failed",
            description: errorMsg,
            variant: "destructive",
          })
          
          // Send push notification for query failure
          sendNotification({
            title: "Query Failed",
            body: errorMsg,
            tag: `query-error`,
            url: `/query`,
            requireInteraction: true,
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
        <form ref={formRef} onSubmit={handleSubmit} className="space-y-4">
          <DatabaseSelector
            selected={selectedDatabases}
            onChange={setSelectedDatabases}
          />
          <QueryInput value={query} onChange={setQuery} />
          <div className="flex items-center gap-4">
            <Button type="submit" disabled={executeMutation.isPending}>
              {executeMutation.isPending ? "Executing..." : "Execute Query"}
            </Button>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>or press</span>
              <KbdGroup>
                <Kbd>{navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}</Kbd>
                <Kbd>Enter</Kbd>
              </KbdGroup>
            </div>
            {currentQueryId && (
              <Badge variant={isConnected ? "default" : "secondary"}>
                {connectionState === 'connected' ? 'Live Updates' : connectionState}
              </Badge>
            )}
          </div>
        </form>
      </Card>

      {queryResult && (
        <>
          <QueryInfo result={queryResult} />
          <QueryResults data={queryResult.data || queryResult.results || []} queryId={queryResult.query_id} />
          <Suspense fallback={
            <Card className="p-6">
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner />
              </div>
            </Card>
          }>
            <ChartControls
              queryId={queryResult.query_id}
              data={queryResult.data || queryResult.results || []}
            />
          </Suspense>
        </>
      )}
    </div>
  )
}

