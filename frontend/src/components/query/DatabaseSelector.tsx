import { useDatabases } from "@/hooks/useDatabases"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LoadingSpinner } from "@/components/shared/LoadingSpinner"

interface DatabaseSelectorProps {
  selected: string[]
  onChange: (selected: string[]) => void
}

export function DatabaseSelector({ selected, onChange }: DatabaseSelectorProps) {
  const { data: databases, isLoading } = useDatabases()

  const handleToggle = (id: string) => {
    if (selected.includes(id)) {
      onChange(selected.filter((dbId) => dbId !== id))
    } else {
      onChange([...selected, id])
    }
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!databases || databases.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">
        No databases available. Add a database first.
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Select Databases (Optional)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {databases.map((db) => (
            <div key={db.id} className="flex items-center space-x-2">
              <Checkbox
                id={db.id}
                checked={selected.includes(db.id)}
                onCheckedChange={() => handleToggle(db.id)}
              />
              <Label
                htmlFor={db.id}
                className="text-sm font-normal cursor-pointer"
              >
                {db.name} ({db.id})
              </Label>
            </div>
          ))}
        </div>
        {selected.length > 0 && (
          <p className="mt-2 text-xs text-muted-foreground">
            {selected.length} database(s) selected
          </p>
        )}
      </CardContent>
    </Card>
  )
}

