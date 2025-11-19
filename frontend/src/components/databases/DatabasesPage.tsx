import { useState } from "react"
import { useDatabases, useSyncDatabase } from "@/hooks/useDatabases"
import { DatabaseList } from "./DatabaseList"
import { DatabaseForm } from "./DatabaseForm"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"
import { ErrorMessage } from "@/components/shared/ErrorMessage"

export function DatabasesPage() {
  const [showForm, setShowForm] = useState(false)
  const { toast } = useToast()

  const { data: databases, isLoading, error } = useDatabases()

  const syncMutation = useSyncDatabase()

  const handleSync = (id: string) => {
    syncMutation.mutate(id, {
      onSuccess: () => {
        toast({
          title: "Success",
          description: "Database schema synced successfully",
        })
      },
      onError: (error: unknown) => {
        const errorMessage = error instanceof Error
          ? error.message
          : (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed to sync database"
        toast({
          title: "Error",
          description: errorMessage,
          variant: "destructive",
        })
      },
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return <ErrorMessage message="Failed to load databases" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Databases</h1>
          <p className="text-muted-foreground">
            Manage your database connections
          </p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="mr-2 h-4 w-4" />
          {showForm ? "Cancel" : "Add Database"}
        </Button>
      </div>

      {showForm && (
        <DatabaseForm
          onSuccess={() => {
            setShowForm(false)
          }}
          onCancel={() => setShowForm(false)}
        />
      )}

      <DatabaseList
        databases={databases || []}
        onSync={handleSync}
        isSyncing={syncMutation.isPending}
      />
    </div>
  )
}

