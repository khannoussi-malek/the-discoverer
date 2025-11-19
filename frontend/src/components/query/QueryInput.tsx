import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

interface QueryInputProps {
  value: string
  onChange: (value: string) => void
}

export function QueryInput({ value, onChange }: QueryInputProps) {
  return (
    <div className="space-y-2">
      <Label htmlFor="query">Enter your query in natural language</Label>
      <Textarea
        id="query"
        placeholder="e.g., Show me all customers from the last month"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={6}
        className="font-mono"
      />
    </div>
  )
}

