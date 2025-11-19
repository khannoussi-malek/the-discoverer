/**
 * Breadcrumb component that displays the current route path
 */

import { useLocation, Link } from "react-router-dom"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
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

const routeMap: Record<string, { label: string; icon?: React.ComponentType<{ className?: string }> }> = {
  "/": { label: "Dashboard", icon: LayoutDashboard },
  "/databases": { label: "Databases", icon: Database },
  "/query": { label: "Query", icon: Search },
  "/dashboards": { label: "Dashboards", icon: Layout },
  "/templates": { label: "Templates", icon: FileText },
  "/scheduler": { label: "Scheduler", icon: Calendar },
  "/analytics": { label: "Analytics", icon: TrendingUp },
  "/webhooks": { label: "Webhooks", icon: Webhook },
}

export function AppBreadcrumb() {
  const location = useLocation()
  const pathnames = location.pathname.split("/").filter((x) => x)

  const getRouteInfo = (path: string) => {
    // Try exact match first
    if (routeMap[path]) {
      return routeMap[path]
    }
    // Try with leading slash
    if (routeMap[`/${path}`]) {
      return routeMap[`/${path}`]
    }
    // Default: capitalize and format
    return { label: path.charAt(0).toUpperCase() + path.slice(1).replace(/-/g, " ") }
  }

  // If we're on the home page, just show Home as the current page
  if (pathnames.length === 0) {
    const homeInfo = routeMap["/"]
    return (
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbPage className="flex items-center gap-2">
              {homeInfo.icon && (
                <homeInfo.icon className="hidden sm:block h-4 w-4" />
              )}
              <span className="text-sm sm:text-base">{homeInfo.label}</span>
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
    )
  }

  return (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink asChild>
            <Link to="/">Home</Link>
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        {pathnames.map((value, index) => {
          const to = `/${pathnames.slice(0, index + 1).join("/")}`
          const isLast = index === pathnames.length - 1
          const routeInfo = getRouteInfo(value)

          return (
            <BreadcrumbItem key={to}>
              {isLast ? (
                <BreadcrumbPage className="flex items-center gap-2">
                  {routeInfo.icon && (
                    <routeInfo.icon className="hidden sm:block h-4 w-4" />
                  )}
                  <span className="text-sm sm:text-base">{routeInfo.label}</span>
                </BreadcrumbPage>
              ) : (
                <>
                  <BreadcrumbLink asChild>
                    <Link to={to} className="flex items-center gap-2">
                      {routeInfo.icon && (
                        <routeInfo.icon className="hidden sm:block h-4 w-4" />
                      )}
                      <span className="text-sm sm:text-base">{routeInfo.label}</span>
                    </Link>
                  </BreadcrumbLink>
                  <BreadcrumbSeparator />
                </>
              )}
            </BreadcrumbItem>
          )
        })}
      </BreadcrumbList>
    </Breadcrumb>
  )
}

