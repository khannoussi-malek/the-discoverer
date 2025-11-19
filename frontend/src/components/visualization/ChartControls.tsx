import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { visualizationService } from "@/api/services/visualization"
import type { VisualizationRequest } from "@/api/services/visualization"
import type { ChartResponse, ChartType } from "@/types/visualization"
import { extractErrorMessage } from "@/lib/errorHandler"
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from "@/lib/messages"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CHART_TYPES } from "@/lib/constants"
import { useToast } from "@/components/ui/use-toast"
import { ChartViewer } from "./ChartViewer"

interface ChartControlsProps {
  queryId: string
  data: Record<string, unknown>[]
}

export function ChartControls({ queryId, data }: ChartControlsProps) {
  const [chartType, setChartType] = useState<ChartType>("bar")
  const [xAxis, setXAxis] = useState("")
  const [yAxis, setYAxis] = useState("")
  const [title, setTitle] = useState("")
  const [chartData, setChartData] = useState<ChartResponse | null>(null)
  const { toast } = useToast()

  const columns = data.length > 0 ? Object.keys(data[0]) : []
  const numericColumns = columns.filter((col) =>
    data.some((row) => typeof row[col] === "number")
  )

  const generateMutation = useMutation({
    mutationFn: (request: VisualizationRequest) =>
      visualizationService.generateChart(request),
    onSuccess: (data) => {
      setChartData(data)
      toast({
        title: SUCCESS_MESSAGES.CHART_GENERATED,
        description: "Chart has been generated successfully",
      })
    },
    onError: (error: unknown) => {
      toast({
        title: "Error",
        description: extractErrorMessage(error) || ERROR_MESSAGES.CHART_GENERATION_FAILED,
        variant: "destructive",
      })
    },
  })

  const handleGenerate = () => {
    if (!xAxis || !yAxis) {
      toast({
        title: "Error",
        description: ERROR_MESSAGES.CHART_AXES_REQUIRED,
        variant: "destructive",
      })
      return
    }

    generateMutation.mutate({
      query_id: queryId,
      chart_type: chartType,
      x_axis: xAxis,
      y_axis: yAxis,
      title: title || undefined,
    })
  }

  if (data.length === 0) {
    return null
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Chart Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <Label>Chart Type</Label>
              <Select
                value={chartType}
                onValueChange={(value) => setChartType(value as ChartType)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CHART_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>X Axis</Label>
              <Select value={xAxis} onValueChange={setXAxis}>
                <SelectTrigger>
                  <SelectValue placeholder="Select X axis" />
                </SelectTrigger>
                <SelectContent>
                  {columns.map((col) => (
                    <SelectItem key={col} value={col}>
                      {col}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Y Axis</Label>
              <Select value={yAxis} onValueChange={setYAxis}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Y axis" />
                </SelectTrigger>
                <SelectContent>
                  {numericColumns.map((col) => (
                    <SelectItem key={col} value={col}>
                      {col}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <Label>Chart Title (Optional)</Label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter chart title"
            />
          </div>
          <Button onClick={handleGenerate} disabled={generateMutation.isPending}>
            {generateMutation.isPending ? "Generating..." : "Generate Chart"}
          </Button>
        </CardContent>
      </Card>

      {chartData && xAxis && yAxis && (
        <ChartViewer
          data={data}
          chartType={chartType}
          xAxis={xAxis}
          yAxis={yAxis}
          title={title || (typeof chartData.config?.title === 'string' ? chartData.config.title : undefined)}
        />
      )}
    </div>
  )
}

