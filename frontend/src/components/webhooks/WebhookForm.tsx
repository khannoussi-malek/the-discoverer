import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useState } from "react"
import { useCreateWebhook, useUpdateWebhook } from "@/hooks/useWebhooks"
import type { Webhook, WebhookEvent } from "@/types/webhooks"
import { extractErrorMessage } from "@/lib/errorHandler"
import { SUCCESS_MESSAGES } from "@/lib/messages"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormField,
} from "@/components/ui/form"
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
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
  active: z.boolean(),
  timeout: z.number().min(1).max(300),
  headers: z.record(z.string(), z.string()).optional(),
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

  type WebhookFormData = z.infer<typeof webhookSchema>

  const form = useForm<WebhookFormData>({
    resolver: zodResolver(webhookSchema),
    defaultValues: {
      url: webhook?.url || "",
      events: webhook?.events || [],
      active: webhook?.active ?? true,
      timeout: webhook?.timeout || 30,
      headers: webhook?.headers ? (webhook.headers as Record<string, string>) : {},
    },
  })

  const createMutation = useCreateWebhook()
  const updateMutation = useUpdateWebhook()

  const onSubmit = (data: WebhookFormData) => {
    if (isEditing) {
      updateMutation.mutate(
        {
          id: webhook.id,
          webhook: {
            url: data.url,
            events: data.events as WebhookEvent[],
            active: data.active,
            timeout: data.timeout,
            headers: data.headers as Record<string, string> | undefined,
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
          timeout: data.timeout,
          headers: data.headers as Record<string, string> | undefined,
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
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="url"
              render={({ field, fieldState }) => (
                <Field data-invalid={!!fieldState.error}>
                  <FieldLabel htmlFor="webhook-url">Webhook URL</FieldLabel>
                  <Input
                    id="webhook-url"
                    placeholder="https://example.com/webhook"
                    aria-invalid={!!fieldState.error}
                    {...field}
                  />
                  <FieldDescription>
                    The URL where webhook events will be sent
                  </FieldDescription>
                  {fieldState.error && (
                    <FieldError>{fieldState.error.message}</FieldError>
                  )}
                </Field>
              )}
            />

            <FormField
              control={form.control}
              name="events"
              render={({ fieldState }) => (
                <Field data-invalid={!!fieldState.error}>
                  <FieldLabel>Events</FieldLabel>
                  <FieldDescription>
                    Select the events that should trigger this webhook
                  </FieldDescription>
                  <FieldGroup className="mt-2">
                    {webhookEvents.map((event) => (
                      <FormField
                        key={event.value}
                        control={form.control}
                        name="events"
                        render={({ field }) => {
                          return (
                            <Field
                              key={event.value}
                              orientation="horizontal"
                            >
                              <Checkbox
                                id={`event-${event.value}`}
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
                              <FieldLabel
                                htmlFor={`event-${event.value}`}
                                className="font-normal cursor-pointer"
                              >
                                {event.label}
                              </FieldLabel>
                            </Field>
                          )
                        }}
                      />
                    ))}
                  </FieldGroup>
                  {fieldState.error && (
                    <FieldError>{fieldState.error.message}</FieldError>
                  )}
                </Field>
              )}
            />

            <FormField
              control={form.control}
              name="active"
              render={({ field }) => (
                <Field orientation="horizontal" className="rounded-lg border p-4">
                  <Switch
                    id="webhook-active"
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                  <FieldContent>
                    <FieldLabel htmlFor="webhook-active">Active</FieldLabel>
                    <FieldDescription>
                      Enable or disable this webhook
                    </FieldDescription>
                  </FieldContent>
                </Field>
              )}
            />

            <FormField
              control={form.control}
              name="timeout"
              render={({ field, fieldState }) => (
                <Field data-invalid={!!fieldState.error}>
                  <FieldLabel htmlFor="webhook-timeout">Timeout (seconds)</FieldLabel>
                  <Input
                    id="webhook-timeout"
                    type="number"
                    min={1}
                    max={300}
                    aria-invalid={!!fieldState.error}
                    {...field}
                    onChange={(e) => field.onChange(parseInt(e.target.value) || 30)}
                  />
                  <FieldDescription>
                    Request timeout in seconds (1-300)
                  </FieldDescription>
                  {fieldState.error && (
                    <FieldError>{fieldState.error.message}</FieldError>
                  )}
                </Field>
              )}
            />

            {secret && (
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <FieldLabel>Webhook Secret</FieldLabel>
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
                <FieldDescription className="mt-2">
                  Save this secret securely. It will not be shown again.
                </FieldDescription>
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

