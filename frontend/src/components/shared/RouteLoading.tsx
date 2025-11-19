/**
 * Loading component for route transitions
 */

import { LoadingSpinner } from "./LoadingSpinner"

export function RouteLoading() {
  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <div className="text-center space-y-4">
        <LoadingSpinner size="lg" />
        <p className="text-sm text-muted-foreground">Loading page...</p>
      </div>
    </div>
  )
}

