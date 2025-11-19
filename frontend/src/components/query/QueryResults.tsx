import { useState } from "react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { exportService, type ExportFormat } from "@/api/services/export"
import { extractErrorMessage } from "@/lib/errorHandler"
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from "@/lib/messages"
import { Download } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { EXPORT_FORMATS } from "@/lib/constants"

interface QueryResultsProps {
  data: Record<string, unknown>[]
  queryId: string
}

export function QueryResults({ data, queryId }: QueryResultsProps) {
  const [exporting, setExporting] = useState<string | null>(null)
  const { toast } = useToast()

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-muted-foreground">No results to display</div>
        </CardContent>
      </Card>
    )
  }

  const columns = Object.keys(data[0])

  const handleExport = async (format: string) => {
    setExporting(format)
    try {
      const blob = await exportService.exportQuery(queryId, format as ExportFormat)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.setAttribute("download", `query_result.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      toast({
        title: SUCCESS_MESSAGES.EXPORT_SUCCESS,
        description: `Query results exported as ${format.toUpperCase()}`,
      })
    } catch (error: unknown) {
      toast({
        title: "Export failed",
        description: extractErrorMessage(error) || ERROR_MESSAGES.EXPORT_FAILED,
        variant: "destructive",
      })
    } finally {
      setExporting(null)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Query Results ({data.length} rows)</CardTitle>
          <div className="flex gap-2">
            {EXPORT_FORMATS.map((format) => (
              <Button
                key={format.value}
                variant="outline"
                size="sm"
                onClick={() => handleExport(format.value)}
                disabled={exporting !== null}
              >
                <Download className="mr-2 h-4 w-4" />
                {exporting === format.value ? "Exporting..." : format.label}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <div className="max-h-[600px] overflow-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {columns.map((col) => (
                    <TableHead key={col}>{col}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.slice(0, 100).map((row, idx) => (
                  <TableRow key={idx}>
                    {columns.map((col) => (
                      <TableCell key={col}>
                        {String(row[col] ?? "")}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          {data.length > 100 && (
            <div className="p-4 text-sm text-muted-foreground text-center">
              Showing first 100 rows of {data.length} total
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

