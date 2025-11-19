import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useState } from "react"
import { useCreateWebhook, useUpdateWebhook } from "@/hooks/useWebhooks"
import type { Webhook, WebhookEvent } from "@/types/webhooks"
import { extractErrorMessage } from "@/lib/errorHandler"
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from "@/lib/messages"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import { Copy, Check } from "lucide-react"

const webhookEvents: { value: WebhookEvent; label: string }[] = [
  { value: 'query.completed', label: 'Query Completed' },
  { value: 'query.failed', label: 'Query Failed' },
  { value: 'database.registered', label: 'Database Registered' },
  { value: 'database.synced', label: 'Database Synced' },
  { value: 'schema.changed', label: 'Schema Changed' },
  { value: 'dashboard.created', label: 'Dashboard Created' },
  { value: 'dashboard.updated', label: 'Dashboard Updated' },
  { value: 'export.completed', label: 'Export Completed' },
]

const webhookSchema = z.object({
  url: z.string().url("Must be a valid URL"),
  events: z.array(z.string()).min(1, "At least one event must be selected"),
  active: z.boolean().default(true),
  timeout: z.number().min(1).max(300).default(30),
  headers: z.record(z.string()).optional(),
})

interface WebhookFormProps {
  webhook?: Webhook
  onSuccess: () => void
  onCancel: () => void
}

export function WebhookForm({ webhook, onSuccess, onCancel }: WebhookFormProps) {
  const { toast } = useToast()
  const [secret, setSecret] = useState<string | undefined>(webhook?.secret)
  const [copied, setCopied] = useState(false)

  const isEditing = !!webhook

  const form = useForm<z.infer<typeof webhookSchema>>({
    resolver: zodResolver(webhookSchema),
    defaultValues: {
      url: webhook?.url || "",
      events: webhook?.events || [],
      active: webhook?.active ?? true,
      timeout: webhook?.timeout || 30,
      headers: webhook?.headers || {},
    },
  })

  const createMutation = useCreateWebhook()
  const updateMutation = useUpdateWebhook()

  const onSubmit = (data: z.infer<typeof webhookSchema>) => {
    if (isEditing) {
      updateMutation.mutate(
        {
          id: webhook.id,
          webhook: {
            url: data.url,
            events: data.events as WebhookEvent[],
            active: data.active,
            timeout: data.timeout,
            headers: data.headers,
          },
        },
        {
          onSuccess: () => {
            toast({
              title: "Success",
              description: SUCCESS_MESSAGES.DATABASE_REGISTERED, // Reuse message constant
            })
            onSuccess()
          },
          onError: (error: unknown) => {
            toast({
              title: "Error",
              description: extractErrorMessage(error) || "Failed to update webhook",
              variant: "destructive",
            })
          },
        }
      )
    } else {
      createMutation.mutate(
        {
          url: data.url,
          events: data.events as WebhookEvent[],
          active: data.active,
          timeout: data.timeout,
          headers: data.headers,
        },
        {
          onSuccess: (createdWebhook) => {
            if (createdWebhook.secret) {
              setSecret(createdWebhook.secret)
            }
            toast({
              title: "Success",
              description: "Webhook created successfully",
            })
            // Don't close form immediately if secret is shown
            if (!createdWebhook.secret) {
              onSuccess()
            }
          },
          onError: (error: unknown) => {
            toast({
              title: "Error",
              description: extractErrorMessage(error) || "Failed to create webhook",
              variant: "destructive",
            })
          },
        }
      )
    }
  }

  const handleCopySecret = () => {
    if (secret) {
      navigator.clipboard.writeText(secret)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
      toast({
        title: "Copied",
        description: "Webhook secret copied to clipboard",
      })
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{isEditing ? "Edit Webhook" : "Create Webhook"}</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Webhook URL</FormLabel>
                  <FormControl>
                    <Input placeholder="https://example.com/webhook" {...field} />
                  </FormControl>
                  <FormDescription>
                    The URL where webhook events will be sent
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="events"
              render={() => (
                <FormItem>
                  <div className="mb-4">
                    <FormLabel className="text-base">Events</FormLabel>
                    <FormDescription>
                      Select the events that should trigger this webhook
                    </FormDescription>
                  </div>
                  {webhookEvents.map((event) => (
                    <FormField
                      key={event.value}
                      control={form.control}
                      name="events"
                      render={({ field }) => {
                        return (
                          <FormItem
                            key={event.value}
                            className="flex flex-row items-start space-x-3 space-y-0"
                          >
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(event.value)}
                                onCheckedChange={(checked) => {
                                  return checked
                                    ? field.onChange([...field.value, event.value])
                                    : field.onChange(
                                        field.value?.filter(
                                          (value) => value !== event.value
                                        )
                                      )
                                }}
                              />
                            </FormControl>
                            <FormLabel className="font-normal">
                              {event.label}
                            </FormLabel>
                          </FormItem>
                        )
                      }}
                    />
                  ))}
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="active"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Active</FormLabel>
                    <FormDescription>
                      Enable or disable this webhook
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="timeout"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Timeout (seconds)</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={1}
                      max={300}
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 30)}
                    />
                  </FormControl>
                  <FormDescription>
                    Request timeout in seconds (1-300)
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {secret && (
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <FormLabel>Webhook Secret</FormLabel>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleCopySecret}
                  >
                    {copied ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground font-mono break-all">
                  {secret}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  Save this secret securely. It will not be shown again.
                </p>
              </div>
            )}

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
              >
                {createMutation.isPending || updateMutation.isPending
                  ? "Saving..."
                  : isEditing
                  ? "Update Webhook"
                  : "Create Webhook"}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}

