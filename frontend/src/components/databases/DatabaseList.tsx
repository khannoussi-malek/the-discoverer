import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { Database } from "@/types/database"
import { RefreshCw, Database as DatabaseIcon } from "lucide-react"
import { EmptyState } from "@/components/shared/EmptyState"

interface DatabaseListProps {
  databases: Database[]
  onSync: (id: string) => void
  isSyncing: boolean
}

export function DatabaseList({ databases, onSync, isSyncing }: DatabaseListProps) {
  if (databases.length === 0) {
    return (
      <EmptyState
        title="No databases registered"
        description="Get started by adding your first database connection"
        icon={<DatabaseIcon className="h-12 w-12" />}
      />
    )
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Host</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Last Synced</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {databases.map((db) => (
            <TableRow key={db.id}>
              <TableCell className="font-medium">{db.id}</TableCell>
              <TableCell>{db.name}</TableCell>
              <TableCell>
                <Badge variant="outline">{db.type}</Badge>
              </TableCell>
              <TableCell>
                {db.host}:{db.port}
              </TableCell>
              <TableCell>
                <Badge variant={db.is_active ? "default" : "secondary"}>
                  {db.is_active ? "Active" : "Inactive"}
                </Badge>
              </TableCell>
              <TableCell>
                {db.last_synced
                  ? new Date(db.last_synced).toLocaleDateString()
                  : "Never"}
              </TableCell>
              <TableCell className="text-right">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onSync(db.id)}
                  disabled={isSyncing}
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Sync Schema
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

