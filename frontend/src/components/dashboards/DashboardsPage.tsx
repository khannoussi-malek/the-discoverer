import { useState } from "react"
import { useDashboards } from "@/hooks/useDashboards"
import { DashboardForm } from "./DashboardForm"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { EmptyState } from "@/components/shared/EmptyState"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"
import { Layout } from "lucide-react"

export function DashboardsPage() {
  const [showForm, setShowForm] = useState(false)
  const { data: dashboards, isLoading } = useDashboards()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboards</h1>
          <p className="text-muted-foreground">
            Create and manage custom dashboards
          </p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="mr-2 h-4 w-4" />
          {showForm ? "Cancel" : "Create Dashboard"}
        </Button>
      </div>

      {showForm && (
        <DashboardForm
          onSuccess={() => {
            setShowForm(false)
          }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {!dashboards || dashboards.length === 0 ? (
        <EmptyState
          title="No dashboards"
          description="Create your first dashboard to visualize your data"
          icon={<Layout className="h-12 w-12" />}
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {dashboards.map((dashboard) => (
            <Card key={dashboard.id}>
              <CardHeader>
                <CardTitle>{dashboard.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {dashboard.description || "No description"}
                </p>
                <div className="mt-4 text-xs text-muted-foreground">
                  {dashboard.widgets?.length || 0} widgets
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

