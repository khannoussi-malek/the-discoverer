import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useCreateTemplate, useUpdateTemplate } from "@/hooks/useTemplates"
import type { Template } from "@/api/services/templates"
import { extractErrorMessage } from "@/lib/errorHandler"
import { SUCCESS_MESSAGES } from "@/lib/messages"
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
import { useDatabases } from "@/hooks/useDatabases"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const templateSchema = z.object({
  name: z.string().min(1, "Name is required"),
  user_query: z.string().min(1, "Query is required"),
  description: z.string().optional(),
  database_ids: z.array(z.string()).optional(),
  is_public: z.boolean().default(false),
  tags: z.string().optional(), // Comma-separated tags
})

interface TemplateFormProps {
  template?: Template
  onSuccess: () => void
  onCancel: () => void
}

export function TemplateForm({ template, onSuccess, onCancel }: TemplateFormProps) {
  const { toast } = useToast()
  const isEditing = !!template
  const { data: databases } = useDatabases()

  const form = useForm<z.infer<typeof templateSchema>>({
    resolver: zodResolver(templateSchema),
    defaultValues: {
      name: template?.name || "",
      user_query: template?.user_query || "",
      description: template?.description || "",
      database_ids: template?.database_ids || [],
      is_public: false, // Templates don't have is_public in the type, but we'll handle it
      tags: template?.tags?.join(", ") || "",
    },
  })

  const createMutation = useCreateTemplate()
  const updateMutation = useUpdateTemplate()

  const isPending = createMutation.isPending || updateMutation.isPending

  const onSubmit = (data: z.infer<typeof templateSchema>) => {
    const tags = data.tags
      ? data.tags.split(",").map((tag) => tag.trim()).filter((tag) => tag.length > 0)
      : undefined

    if (isEditing && template) {
      updateMutation.mutate(
        {
          id: template.id,
          template: {
            name: data.name,
            user_query: data.user_query,
            description: data.description,
            database_ids: data.database_ids && data.database_ids.length > 0 ? data.database_ids : undefined,
            tags: tags,
          },
        },
        {
          onSuccess: () => {
            toast({
              title: "Success",
              description: "Template updated successfully",
            })
            onSuccess()
          },
          onError: (error: unknown) => {
            toast({
              title: "Error",
              description: extractErrorMessage(error) || "Failed to update template",
              variant: "destructive",
            })
          },
        }
      )
    } else {
      createMutation.mutate(
        {
          name: data.name,
          user_query: data.user_query,
          description: data.description,
          database_ids: data.database_ids && data.database_ids.length > 0 ? data.database_ids : undefined,
          tags: tags,
        },
        {
          onSuccess: () => {
            toast({
              title: "Success",
              description: "Template created successfully",
            })
            onSuccess()
          },
          onError: (error: unknown) => {
            toast({
              title: "Error",
              description: extractErrorMessage(error) || "Failed to create template",
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
        <CardTitle>{isEditing ? "Edit Template" : "Create Template"}</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Template Name</FormLabel>
                  <FormControl>
                    <Input placeholder="My Query Template" {...field} />
                  </FormControl>
                  <FormDescription>
                    A descriptive name for your template
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="user_query"
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
                    The natural language query for this template
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
                      placeholder="Describe what this template does..."
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

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
                      Limit this template to specific databases (optional)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <FormField
              control={form.control}
              name="tags"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tags (Optional)</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="analytics, reporting, users"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Comma-separated tags for organizing templates
                  </FormDescription>
                  <FormMessage />
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
                  "Update Template"
                ) : (
                  "Create Template"
                )}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}

