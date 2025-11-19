import { Suspense, lazy } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { ErrorBoundary } from "@/components/shared/ErrorBoundary"
import { AppLayout } from "@/components/layout/AppLayout"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { LoginPage } from "@/components/auth/LoginPage"
import { Toaster } from "@/components/ui/toaster"
import { RouteLoading } from "@/components/shared/RouteLoading"

// Lazy load page components for code splitting
const DashboardPage = lazy(() => import("@/components/dashboard/DashboardPage").then(module => ({ default: module.DashboardPage })))
const DatabasesPage = lazy(() => import("@/components/databases/DatabasesPage").then(module => ({ default: module.DatabasesPage })))
const QueryPage = lazy(() => import("@/components/query/QueryPage").then(module => ({ default: module.QueryPage })))
const DashboardsPage = lazy(() => import("@/components/dashboards/DashboardsPage").then(module => ({ default: module.DashboardsPage })))
const TemplatesPage = lazy(() => import("@/components/templates/TemplatesPage").then(module => ({ default: module.TemplatesPage })))
const SchedulerPage = lazy(() => import("@/components/scheduler/SchedulerPage").then(module => ({ default: module.SchedulerPage })))
const AnalyticsPage = lazy(() => import("@/components/analytics/AnalyticsPage").then(module => ({ default: module.AnalyticsPage })))
const WebhooksPage = lazy(() => import("@/components/webhooks/WebhooksPage").then(module => ({ default: module.WebhooksPage })))

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
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route
                index
                element={
                  <Suspense fallback={<RouteLoading />}>
                    <DashboardPage />
                  </Suspense>
                }
              />
              <Route
                path="databases"
                element={
                  <Suspense fallback={<RouteLoading />}>
                    <DatabasesPage />
                  </Suspense>
                }
              />
              <Route
                path="query"
                element={
                  <Suspense fallback={<RouteLoading />}>
                    <QueryPage />
                  </Suspense>
                }
              />
              <Route
                path="dashboards"
                element={
                  <Suspense fallback={<RouteLoading />}>
                    <DashboardsPage />
                  </Suspense>
                }
              />
              <Route
                path="templates"
                element={
                  <Suspense fallback={<RouteLoading />}>
                    <TemplatesPage />
                  </Suspense>
                }
              />
              <Route
                path="scheduler"
                element={
                  <Suspense fallback={<RouteLoading />}>
                    <SchedulerPage />
                  </Suspense>
                }
              />
              <Route
                path="analytics"
                element={
                  <Suspense fallback={<RouteLoading />}>
                    <AnalyticsPage />
                  </Suspense>
                }
              />
              <Route
                path="webhooks"
                element={
                  <Suspense fallback={<RouteLoading />}>
                    <WebhooksPage />
                  </Suspense>
                }
              />
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
