import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useRegisterDatabase } from "@/hooks/useDatabases"
import type { DatabaseConfig } from "@/types/database"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DATABASE_TYPES } from "@/lib/constants"
import { useToast } from "@/components/ui/use-toast"

const databaseSchema = z.object({
  id: z.string().min(1, "ID is required"),
  type: z.string().min(1, "Type is required"),
  name: z.string().optional(),
  host: z.string().min(1, "Host is required"),
  port: z.number().min(1).max(65535),
  database: z.string().min(1, "Database name is required"),
  user: z.string().optional(),
  password: z.string().optional(),
})

interface DatabaseFormProps {
  onSuccess: () => void
  onCancel: () => void
}

export function DatabaseForm({ onSuccess, onCancel }: DatabaseFormProps) {
  const { toast } = useToast()

  const form = useForm<DatabaseConfig>({
    resolver: zodResolver(databaseSchema),
    defaultValues: {
      id: "",
      type: "postgresql",
      name: "",
      host: "",
      port: 5432,
      database: "",
      user: "",
      password: "",
    },
  })

  const mutation = useRegisterDatabase()

  const onSubmit = (data: DatabaseConfig) => {
    mutation.mutate(data, {
      onSuccess: () => {
        toast({
          title: "Success",
          description: SUCCESS_MESSAGES.DATABASE_REGISTERED,
        })
        onSuccess()
      },
      onError: (error: unknown) => {
        toast({
          title: "Error",
          description: extractErrorMessage(error) || ERROR_MESSAGES.DATABASE_REGISTER_FAILED,
          variant: "destructive",
        })
      },
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Register Database</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <FormField
                control={form.control}
                name="id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Database ID</FormLabel>
                    <FormControl>
                      <Input placeholder="my_database" {...field} />
                    </FormControl>
                    <FormDescription>
                      Unique identifier for this database
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Database Type</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {DATABASE_TYPES.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
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
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="My Database" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="host"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Host</FormLabel>
                    <FormControl>
                      <Input placeholder="localhost" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="port"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Port</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="database"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Database Name</FormLabel>
                    <FormControl>
                      <Input placeholder="mydb" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="user"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Username (Optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="user" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password (Optional)</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="password" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? "Registering..." : "Register Database"}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}

