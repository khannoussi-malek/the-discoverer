import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Database,
  Search,
  Layout,
  FileText,
  Calendar,
  TrendingUp,
  Webhook,
} from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Databases", href: "/databases", icon: Database },
  { name: "Query", href: "/query", icon: Search },
  { name: "Dashboards", href: "/dashboards", icon: Layout },
  { name: "Templates", href: "/templates", icon: FileText },
  { name: "Scheduler", href: "/scheduler", icon: Calendar },
  { name: "Analytics", href: "/analytics", icon: TrendingUp },
  { name: "Webhooks", href: "/webhooks", icon: Webhook },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <div className="flex h-full w-64 flex-col border-r bg-background">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold">The Discoverer</h1>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

