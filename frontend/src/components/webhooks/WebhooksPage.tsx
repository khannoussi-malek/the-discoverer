import { useState } from "react"
import { useWebhooks, useDeleteWebhook, useTestWebhook } from "@/hooks/useWebhooks"
import { WebhookForm } from "./WebhookForm"
import { WebhookStats } from "./WebhookStats"
import { Button } from "@/components/ui/button"
import { Plus, Trash2, Play, BarChart3 } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"
import { ErrorMessage } from "@/components/shared/ErrorMessage"
import { EmptyState } from "@/components/shared/EmptyState"
import { Webhook as WebhookIcon } from "lucide-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { extractErrorMessage } from "@/lib/errorHandler"
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from "@/lib/messages"
import type { Webhook as WebhookType } from "@/types/webhooks"

export function WebhooksPage() {
  const [showForm, setShowForm] = useState(false)
  const [editingWebhook, setEditingWebhook] = useState<WebhookType | null>(null)
  const [selectedWebhookId, setSelectedWebhookId] = useState<string | null>(null)
  const [showStats, setShowStats] = useState(false)
  const [eventFilter, setEventFilter] = useState<string | undefined>()
  const [activeOnly, setActiveOnly] = useState(false)
  const { toast } = useToast()

  const { data: webhooks, isLoading, error } = useWebhooks({
    event: eventFilter,
    active_only: activeOnly,
  })

  const deleteMutation = useDeleteWebhook()
  const testMutation = useTestWebhook()

  const handleDelete = (id: string) => {
    if (window.confirm("Are you sure you want to delete this webhook?")) {
      deleteMutation.mutate(id, {
        onSuccess: () => {
          toast({
            title: "Success",
            description: "Webhook deleted successfully",
          })
        },
        onError: (error: unknown) => {
          toast({
            title: "Error",
            description: extractErrorMessage(error) || "Failed to delete webhook",
            variant: "destructive",
          })
        },
      })
    }
  }

  const handleTest = (id: string) => {
    testMutation.mutate(
      { id, payload: { test: true, message: "Test webhook" } },
      {
        onSuccess: () => {
          toast({
            title: "Success",
            description: "Webhook test triggered successfully",
          })
        },
        onError: (error: unknown) => {
          toast({
            title: "Error",
            description: extractErrorMessage(error) || "Failed to test webhook",
            variant: "destructive",
          })
        },
      }
    )
  }

  const handleEdit = (webhook: WebhookType) => {
    setEditingWebhook(webhook)
    setShowForm(true)
  }

  const handleCreate = () => {
    setEditingWebhook(null)
    setShowForm(true)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return <ErrorMessage message="Failed to load webhooks" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Webhooks</h1>
          <p className="text-muted-foreground">
            Manage webhook endpoints for event notifications
          </p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="mr-2 h-4 w-4" />
          Create Webhook
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 items-center">
        <select
          className="px-3 py-2 border rounded-md"
          value={eventFilter || ""}
          onChange={(e) => setEventFilter(e.target.value || undefined)}
        >
          <option value="">All Events</option>
          <option value="query.completed">Query Completed</option>
          <option value="query.failed">Query Failed</option>
          <option value="database.registered">Database Registered</option>
          <option value="database.synced">Database Synced</option>
          <option value="schema.changed">Schema Changed</option>
          <option value="dashboard.created">Dashboard Created</option>
          <option value="dashboard.updated">Dashboard Updated</option>
          <option value="export.completed">Export Completed</option>
        </select>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm">Active only</span>
        </label>
      </div>

      {showForm && (
        <WebhookForm
          webhook={editingWebhook || undefined}
          onSuccess={() => {
            setShowForm(false)
            setEditingWebhook(null)
          }}
          onCancel={() => {
            setShowForm(false)
            setEditingWebhook(null)
          }}
        />
      )}

      {!webhooks || webhooks.length === 0 ? (
        <EmptyState
          title="No webhooks"
          description="Create your first webhook to receive event notifications"
          icon={<WebhookIcon className="h-12 w-12" />}
        />
      ) : (
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>URL</TableHead>
                <TableHead>Events</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Stats</TableHead>
                <TableHead>Last Triggered</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {webhooks.map((webhook) => (
                <TableRow key={webhook.id}>
                  <TableCell className="font-mono text-sm max-w-xs truncate">
                    {webhook.url}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {webhook.events.map((event) => (
                        <Badge key={event} variant="outline" className="text-xs">
                          {event}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={webhook.active ? "default" : "secondary"}>
                      {webhook.active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="text-green-600">
                        ✓ {webhook.success_count || 0}
                      </div>
                      <div className="text-red-600">
                        ✗ {webhook.failure_count || 0}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {webhook.last_triggered
                      ? new Date(webhook.last_triggered).toLocaleString()
                      : "Never"}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedWebhookId(webhook.id)
                          setShowStats(true)
                        }}
                      >
                        <BarChart3 className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleTest(webhook.id)}
                        disabled={testMutation.isPending}
                      >
                        <Play className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEdit(webhook)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(webhook.id)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      <Dialog open={showStats} onOpenChange={setShowStats}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Webhook Statistics</DialogTitle>
            <DialogDescription>
              View detailed statistics for this webhook
            </DialogDescription>
          </DialogHeader>
          {selectedWebhookId && (
            <WebhookStats webhookId={selectedWebhookId} />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

