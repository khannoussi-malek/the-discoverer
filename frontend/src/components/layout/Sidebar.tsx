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
import { Kbd, KbdGroup } from "@/components/ui/kbd"

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard, shortcut: "1" },
  { name: "Databases", href: "/databases", icon: Database, shortcut: "2" },
  { name: "Query", href: "/query", icon: Search, shortcut: "3" },
  { name: "Dashboards", href: "/dashboards", icon: Layout, shortcut: "4" },
  { name: "Templates", href: "/templates", icon: FileText, shortcut: "5" },
  { name: "Scheduler", href: "/scheduler", icon: Calendar, shortcut: "6" },
  { name: "Analytics", href: "/analytics", icon: TrendingUp, shortcut: "7" },
  { name: "Webhooks", href: "/webhooks", icon: Webhook, shortcut: "8" },
]

interface SidebarContentProps {
  onNavigate?: () => void
}

function SidebarContent({ onNavigate }: SidebarContentProps) {
  const location = useLocation()

  return (
    <>
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold">Navo</h1>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center justify-between gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors group",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <div className="flex items-center gap-3">
                <item.icon className="h-5 w-5" />
                {item.name}
              </div>
              {item.shortcut && (
                <KbdGroup className="hidden md:flex opacity-0 group-hover:opacity-100 transition-opacity">
                  <Kbd className="text-xs">
                    {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}
                  </Kbd>
                  <Kbd className="text-xs">{item.shortcut}</Kbd>
                </KbdGroup>
              )}
            </Link>
          )
        })}
      </nav>
    </>
  )
}

export function Sidebar() {
  return (
    <aside className="hidden md:flex h-full w-64 flex-col border-r bg-background">
      <SidebarContent />
    </aside>
  )
}

export { SidebarContent }

