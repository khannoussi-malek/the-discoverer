import { useState } from "react"
import { useSchedules } from "@/hooks/useScheduler"
import { ScheduleForm } from "./ScheduleForm"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { EmptyState } from "@/components/shared/EmptyState"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"
import { Calendar } from "lucide-react"

export function SchedulerPage() {
  const [showForm, setShowForm] = useState(false)
  const { data: schedules, isLoading } = useSchedules()

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
          <h1 className="text-3xl font-bold tracking-tight">Scheduler</h1>
          <p className="text-muted-foreground">
            Manage scheduled queries
          </p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <Plus className="mr-2 h-4 w-4" />
          {showForm ? "Cancel" : "Create Schedule"}
        </Button>
      </div>

      {showForm && (
        <ScheduleForm
          onSuccess={() => {
            setShowForm(false)
          }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {!schedules || schedules.length === 0 ? (
        <EmptyState
          title="No scheduled queries"
          description="Schedule queries to run automatically"
          icon={<Calendar className="h-12 w-12" />}
        />
      ) : (
        <div className="space-y-4">
          {schedules.map((schedule) => (
            <Card key={schedule.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{schedule.name}</CardTitle>
                  <Badge variant={schedule.enabled ? "default" : "secondary"}>
                    {schedule.enabled ? "Enabled" : "Disabled"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-2">
                  {schedule.query}
                </p>
                <div className="text-xs text-muted-foreground">
                  Schedule: {schedule.schedule}
                </div>
                {schedule.next_run && (
                  <div className="text-xs text-muted-foreground mt-1">
                    Next run: {new Date(schedule.next_run).toLocaleString()}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

