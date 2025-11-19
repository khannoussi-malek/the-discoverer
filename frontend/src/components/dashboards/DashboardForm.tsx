import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useCreateDashboard, useUpdateDashboard } from "@/hooks/useDashboards"
import type { Dashboard } from "@/types/dashboard"
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
import { Switch } from "@/components/ui/switch"

const dashboardSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().optional(),
  is_public: z.boolean(),
  tags: z.array(z.string()).optional(),
})

interface DashboardFormProps {
  dashboard?: Dashboard
  onSuccess: () => void
  onCancel: () => void
}

export function DashboardForm({ dashboard, onSuccess, onCancel }: DashboardFormProps) {
  const { toast } = useToast()
  const isEditing = !!dashboard

  const form = useForm<z.infer<typeof dashboardSchema>>({
    resolver: zodResolver(dashboardSchema),
    defaultValues: {
      name: dashboard?.name || "",
      description: dashboard?.description || "",
      is_public: dashboard?.is_public ?? false,
      tags: dashboard?.tags || [],
    },
  })

  const createMutation = useCreateDashboard()
  const updateMutation = useUpdateDashboard()

  const isPending = createMutation.isPending || updateMutation.isPending

  const onSubmit = (data: z.infer<typeof dashboardSchema>) => {
    if (isEditing && dashboard) {
      updateMutation.mutate(
        {
          id: dashboard.id,
          dashboard: {
            name: data.name,
            description: data.description,
            is_public: data.is_public,
            tags: data.tags,
          },
        },
        {
          onSuccess: () => {
            toast({
              title: "Success",
              description: "Dashboard updated successfully",
            })
            onSuccess()
          },
          onError: (error: unknown) => {
            toast({
              title: "Error",
              description: extractErrorMessage(error) || "Failed to update dashboard",
              variant: "destructive",
            })
          },
        }
      )
    } else {
      createMutation.mutate(
        {
          name: data.name,
          description: data.description,
          is_public: data.is_public,
          tags: data.tags,
          widgets: [],
        },
        {
          onSuccess: () => {
            toast({
              title: "Success",
              description: "Dashboard created successfully",
            })
            onSuccess()
          },
          onError: (error: unknown) => {
            toast({
              title: "Error",
              description: extractErrorMessage(error) || "Failed to create dashboard",
              variant: "destructive",
            })
          },
        }
      )
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{isEditing ? "Edit Dashboard" : "Create Dashboard"}</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Dashboard Name</FormLabel>
                  <FormControl>
                    <Input placeholder="My Dashboard" {...field} />
                  </FormControl>
                  <FormDescription>
                    A descriptive name for your dashboard
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
                      placeholder="Describe what this dashboard shows..."
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="is_public"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">Public Dashboard</FormLabel>
                    <FormDescription>
                      Allow others to view this dashboard
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
                    {isEditing ? "Updating..." : "Creating..."}
                  </>
                ) : isEditing ? (
                  "Update Dashboard"
                ) : (
                  "Create Dashboard"
                )}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}

