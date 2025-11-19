import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ErrorBoundary } from "@/components/shared/ErrorBoundary"
import { AppLayout } from "@/components/layout/AppLayout"
import { Toaster } from "@/components/ui/toaster"
import { DashboardPage } from "@/components/dashboard/DashboardPage"
import { DatabasesPage } from "@/components/databases/DatabasesPage"
import { QueryPage } from "@/components/query/QueryPage"
import { DashboardsPage } from "@/components/dashboards/DashboardsPage"
import { TemplatesPage } from "@/components/templates/TemplatesPage"
import { SchedulerPage } from "@/components/scheduler/SchedulerPage"
import { AnalyticsPage } from "@/components/analytics/AnalyticsPage"
import { WebhooksPage } from "@/components/webhooks/WebhooksPage"

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<AppLayout />}>
              <Route index element={<DashboardPage />} />
              <Route path="databases" element={<DatabasesPage />} />
              <Route path="query" element={<QueryPage />} />
              <Route path="dashboards" element={<DashboardsPage />} />
              <Route path="templates" element={<TemplatesPage />} />
              <Route path="scheduler" element={<SchedulerPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="webhooks" element={<WebhooksPage />} />
            </Route>
          </Routes>
          <Toaster />
        </BrowserRouter>
        {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
