import { useEffect } from "react"
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
  host: z.string().optional(),
  port: z.number().optional(),
  database: z.string().min(1, "Database name or path is required"),
  user: z.string().optional(),
  password: z.string().optional(),
}).refine((data) => {
  // For SQLite, host and port are optional
  if (data.type === "sqlite") {
    return true
  }
  // For other database types, host is required
  if (!data.host || data.host.trim() === "") {
    return false
  }
  return true
}, {
  message: "Host is required for this database type",
  path: ["host"],
}).refine((data) => {
  // For SQLite, port is optional
  if (data.type === "sqlite") {
    return true
  }
  // For other database types, port is required and must be valid
  if (data.port === undefined || data.port === null) {
    return false
  }
  if (data.port < 1 || data.port > 65535) {
    return false
  }
  return true
}, {
  message: "Port is required and must be between 1 and 65535",
  path: ["port"],
})

interface DatabaseFormProps {
  onSuccess: () => void
  onCancel: () => void
}

export function DatabaseForm({ onSuccess, onCancel }: DatabaseFormProps) {
  const { toast } = useToast()

  type DatabaseFormData = z.infer<typeof databaseSchema>

  const form = useForm<DatabaseFormData>({
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

  const selectedType = form.watch("type")
  const isSQLite = selectedType === "sqlite"

  // Reset host/port when switching to SQLite, or set defaults when switching away
  useEffect(() => {
    if (isSQLite) {
      form.setValue("host", "")
      // For SQLite, we don't need port, but zod schema allows optional
      // We'll handle undefined in onSubmit
    } else {
      // Set default port based on database type
      const defaultPorts: Record<string, number> = {
        postgresql: 5432,
        mysql: 3306,
        mssql: 1433,
        oracle: 1521,
      }
      const currentPort = form.getValues("port")
      if (currentPort === undefined || currentPort === null) {
        form.setValue("port", defaultPorts[selectedType] || 5432)
      }
      const currentHost = form.getValues("host")
      if (!currentHost || currentHost.trim() === "") {
        form.setValue("host", "localhost")
      }
    }
  }, [selectedType, isSQLite, form])

  const mutation = useRegisterDatabase()

  const onSubmit = (data: DatabaseFormData) => {
    // Clean up data: remove undefined port/host for SQLite
    const submitData: DatabaseConfig = {
      ...data,
      ...(isSQLite && {
        host: undefined,
        port: undefined,
      }),
    }
    
    mutation.mutate(submitData, {
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

              {!isSQLite && (
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
              )}

              {!isSQLite && (
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
                          onChange={(e) => {
                            const value = e.target.value
                            field.onChange(value === "" ? undefined : parseInt(value))
                          }}
                          value={field.value ?? ""}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}

              <FormField
                control={form.control}
                name="database"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      {isSQLite ? "Database Path" : "Database Name"}
                    </FormLabel>
                    <FormControl>
                      <Input 
                        placeholder={isSQLite ? "/path/to/database.sqlite" : "mydb"} 
                        {...field} 
                      />
                    </FormControl>
                    <FormDescription>
                      {isSQLite 
                        ? "Full path to the SQLite database file (e.g., /tmp/test_db.sqlite)"
                        : "Name of the database"}
                    </FormDescription>
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

