import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  RadialBarChart,
  RadialBar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts"
import type { ChartType } from "@/types/visualization"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { ChartConfig } from "@/components/ui/chart"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from "@/components/ui/chart"

interface ChartViewerProps {
  data: Record<string, unknown>[]
  chartType: ChartType
  xAxis: string
  yAxis: string
  title?: string
}

export function ChartViewer({
  data,
  chartType,
  xAxis,
  yAxis,
  title,
}: ChartViewerProps) {
  const chartData = data.map((row) => ({
    [xAxis]: row[xAxis],
    [yAxis]: row[yAxis],
  }))

  // Use a fixed key for CSS variable compatibility, but set label to yAxis for tooltips
  const chartConfig = {
    data: {
      label: yAxis,
      color: "hsl(var(--chart-1))",
    },
  } satisfies ChartConfig

  const colorVar = "var(--color-data)"

  const renderChart = () => {
    switch (chartType) {
      case "bar":
        return (
          <ChartContainer config={chartConfig} className="min-h-[400px] w-full">
            <BarChart
              accessibilityLayer
              data={chartData}
              margin={{
                left: 12,
                right: 12,
              }}
            >
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey={xAxis}
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis tickLine={false} axisLine={false} tickMargin={8} />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent />}
              />
              <ChartLegend content={<ChartLegendContent />} />
              <Bar
                dataKey={yAxis}
                fill={colorVar}
                radius={4}
              />
            </BarChart>
          </ChartContainer>
        )
      case "line":
        return (
          <ChartContainer config={chartConfig} className="min-h-[400px] w-full">
            <LineChart
              accessibilityLayer
              data={chartData}
              margin={{
                left: 12,
                right: 12,
              }}
            >
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey={xAxis}
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis tickLine={false} axisLine={false} tickMargin={8} />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent hideLabel />}
              />
              <ChartLegend content={<ChartLegendContent />} />
              <Line
                dataKey={yAxis}
                type="natural"
                stroke={colorVar}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ChartContainer>
        )
      case "pie": {
        const pieChartConfig = {
          data: {
            label: yAxis,
          },
        } satisfies ChartConfig

        const pieData = chartData.map((entry, index) => ({
          ...entry,
          fill: `hsl(var(--chart-${(index % 5) + 1}))`,
        }))

        return (
          <ChartContainer
            config={pieChartConfig}
            className="mx-auto aspect-square max-h-[400px]"
          >
            <PieChart>
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent hideLabel />}
              />
              <ChartLegend content={<ChartLegendContent />} />
              <Pie
                data={pieData}
                dataKey={yAxis}
                nameKey={xAxis}
                cx="50%"
                cy="50%"
                outerRadius={120}
              />
            </PieChart>
          </ChartContainer>
        )
      }
      case "area":
        return (
          <ChartContainer config={chartConfig} className="min-h-[400px] w-full">
            <AreaChart
              accessibilityLayer
              data={chartData}
              margin={{
                left: 12,
                right: 12,
              }}
            >
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey={xAxis}
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis tickLine={false} axisLine={false} tickMargin={8} />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent indicator="line" />}
              />
              <ChartLegend content={<ChartLegendContent />} />
              <Area
                dataKey={yAxis}
                type="natural"
                fill={colorVar}
                fillOpacity={0.4}
                stroke={colorVar}
              />
            </AreaChart>
          </ChartContainer>
        )
      case "scatter": {
        return (
          <ChartContainer config={chartConfig} className="min-h-[400px] w-full">
            <ScatterChart
              accessibilityLayer
              data={chartData}
              margin={{
                left: 12,
                right: 12,
              }}
            >
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey={xAxis}
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis tickLine={false} axisLine={false} tickMargin={8} />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent />}
              />
              <ChartLegend content={<ChartLegendContent />} />
              <Scatter
                dataKey={yAxis}
                fill={colorVar}
              />
            </ScatterChart>
          </ChartContainer>
        )
      }
      case "radar": {
        return (
          <ChartContainer
            config={chartConfig}
            className="mx-auto aspect-square max-h-[400px]"
          >
            <RadarChart data={chartData}>
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent />}
              />
              <PolarAngleAxis dataKey={xAxis} />
              <PolarGrid />
              <Radar
                dataKey={yAxis}
                fill={colorVar}
                fillOpacity={0.6}
              />
            </RadarChart>
          </ChartContainer>
        )
      }
      case "gauge": {
        // Radial bar chart for gauge-like visualization
        const radialData = chartData.map((entry, index) => ({
          ...entry,
          fill: `hsl(var(--chart-${(index % 5) + 1}))`,
        }))

        const radialConfig = {
          data: {
            label: yAxis,
          },
        } satisfies ChartConfig

        return (
          <ChartContainer
            config={radialConfig}
            className="mx-auto aspect-square max-h-[400px]"
          >
            <RadialBarChart
              data={radialData}
              innerRadius={60}
              outerRadius={120}
              startAngle={90}
              endAngle={-270}
            >
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent hideLabel />}
              />
              <RadialBar dataKey={yAxis} background />
            </RadialBarChart>
          </ChartContainer>
        )
      }
      default:
        return <div>Unsupported chart type</div>
    }
  }

  return (
    <Card>
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent>
        {renderChart()}
      </CardContent>
    </Card>
  )
}

