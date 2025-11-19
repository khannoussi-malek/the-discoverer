import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useCreateSchedule } from "@/hooks/useScheduler"
import type { ScheduledQuery } from "@/api/services/scheduler"
import { extractErrorMessage } from "@/lib/errorHandler"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"
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
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { useDatabases } from "@/hooks/useDatabases"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const scheduleSchema = z.object({
  name: z.string().min(1, "Name is required"),
  query: z.string().min(1, "Query is required"),
  description: z.string().optional(),
  schedule: z.string().min(1, "Schedule is required"),
  frequency: z.string().min(1, "Frequency is required"),
  database_ids: z.array(z.string()).optional(),
})

const FREQUENCY_OPTIONS = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
  { value: "hourly", label: "Hourly" },
  { value: "custom", label: "Custom (Cron)" },
]

interface ScheduleFormProps {
  schedule?: ScheduledQuery
  onSuccess: () => void
  onCancel: () => void
}

export function ScheduleForm({ schedule, onSuccess, onCancel }: ScheduleFormProps) {
  const { toast } = useToast()
  const isEditing = !!schedule
  const { data: databases } = useDatabases()

  const form = useForm<z.infer<typeof scheduleSchema>>({
    resolver: zodResolver(scheduleSchema),
    defaultValues: {
      name: schedule?.name || "",
      query: schedule?.query || "",
      description: schedule?.description || "",
      schedule: schedule?.schedule || "0 0 * * *", // Default: daily at midnight
      frequency: schedule?.frequency || "daily",
      database_ids: schedule?.database_ids || [],
    },
  })

  const selectedFrequency = form.watch("frequency")

  const createMutation = useCreateSchedule()

  const isPending = createMutation.isPending

  const onSubmit = (data: z.infer<typeof scheduleSchema>) => {
    // Generate cron expression based on frequency if not custom
    let cronExpression = data.schedule
    if (data.frequency !== "custom") {
      switch (data.frequency) {
        case "hourly":
          cronExpression = "0 * * * *"
          break
        case "daily":
          cronExpression = "0 0 * * *"
          break
        case "weekly":
          cronExpression = "0 0 * * 0"
          break
        case "monthly":
          cronExpression = "0 0 1 * *"
          break
        default:
          cronExpression = data.schedule
      }
    }

    createMutation.mutate(
      {
        name: data.name,
        query: data.query,
        description: data.description,
        schedule: cronExpression,
        frequency: data.frequency,
        database_ids: data.database_ids && data.database_ids.length > 0 ? data.database_ids : undefined,
      },
      {
        onSuccess: () => {
          toast({
            title: "Success",
            description: "Schedule created successfully",
          })
          onSuccess()
        },
        onError: (error: unknown) => {
          toast({
            title: "Error",
            description: extractErrorMessage(error) || "Failed to create schedule",
            variant: "destructive",
          })
        },
      }
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{isEditing ? "Edit Schedule" : "Create Schedule"}</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Schedule Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Daily User Report" {...field} />
                  </FormControl>
                  <FormDescription>
                    A descriptive name for this scheduled query
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="query"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Query</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Show me all users where age > 25"
                      className="min-h-[100px] font-mono text-sm"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    The natural language query to execute
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe what this schedule does..."
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid gap-4 md:grid-cols-2">
              <FormField
                control={form.control}
                name="frequency"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Frequency</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select frequency" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {FREQUENCY_OPTIONS.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="schedule"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      {selectedFrequency === "custom" ? "Cron Expression" : "Schedule"}
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder={selectedFrequency === "custom" ? "0 0 * * *" : "Auto-generated"}
                        {...field}
                        disabled={selectedFrequency !== "custom"}
                      />
                    </FormControl>
                    <FormDescription>
                      {selectedFrequency === "custom"
                        ? "Cron expression (e.g., 0 0 * * * for daily at midnight)"
                        : "Cron expression will be auto-generated based on frequency"}
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {databases && databases.length > 0 && (
              <FormField
                control={form.control}
                name="database_ids"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Databases (Optional)</FormLabel>
                    <Select
                      value={field.value?.[0] || ""}
                      onValueChange={(value) => {
                        field.onChange(value ? [value] : [])
                      }}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a database (optional)" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="">None (All databases)</SelectItem>
                        {databases.map((db) => (
                          <SelectItem key={db.id} value={db.id}>
                            {db.name || db.id}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Limit this schedule to specific databases (optional)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <div className="flex justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isPending}
                className="min-w-[140px]"
              >
                {isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : isEditing ? (
                  "Update Schedule"
                ) : (
                  "Create Schedule"
                )}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}

