import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useNavigate } from "react-router-dom"
import { Database, Search, Layout } from "lucide-react"

export function QuickActions() {
  const navigate = useNavigate()

  const actions = [
    {
      title: "Add Database",
      description: "Register a new database connection",
      icon: Database,
      action: () => navigate("/databases"),
    },
    {
      title: "Execute Query",
      description: "Run a natural language query",
      icon: Search,
      action: () => navigate("/query"),
    },
    {
      title: "Create Dashboard",
      description: "Build a custom dashboard",
      icon: Layout,
      action: () => navigate("/dashboards"),
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-3">
          {actions.map((action) => (
            <Button
              key={action.title}
              variant="outline"
              className="h-auto flex-col items-start justify-start p-4"
              onClick={action.action}
            >
              <action.icon className="mb-2 h-6 w-6" />
              <div className="text-left">
                <div className="font-semibold">{action.title}</div>
                <div className="text-sm text-muted-foreground">
                  {action.description}
                </div>
              </div>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

