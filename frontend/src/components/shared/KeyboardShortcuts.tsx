/**
 * Component to display keyboard shortcuts help
 */

import { useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Kbd, KbdGroup } from "@/components/ui/kbd"
import { Keyboard } from "lucide-react"
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts"

interface Shortcut {
  keys: {
    key: string
    ctrl?: boolean
    shift?: boolean
    alt?: boolean
    meta?: boolean
  }
  description: string
}

const shortcuts: Shortcut[] = [
  {
    keys: { key: 'k', ctrl: true },
    description: 'Open command palette',
  },
  {
    keys: { key: 'Enter', ctrl: true },
    description: 'Execute query',
  },
  {
    keys: { key: '1', ctrl: true },
    description: 'Go to Dashboard',
  },
  {
    keys: { key: '2', ctrl: true },
    description: 'Go to Databases',
  },
  {
    keys: { key: '3', ctrl: true },
    description: 'Go to Query',
  },
  {
    keys: { key: '4', ctrl: true },
    description: 'Go to Dashboards',
  },
  {
    keys: { key: '5', ctrl: true },
    description: 'Go to Templates',
  },
  {
    keys: { key: '6', ctrl: true },
    description: 'Go to Scheduler',
  },
  {
    keys: { key: '7', ctrl: true },
    description: 'Go to Analytics',
  },
  {
    keys: { key: '8', ctrl: true },
    description: 'Go to Webhooks',
  },
  {
    keys: { key: '/', ctrl: true },
    description: 'Show keyboard shortcuts',
  },
  {
    keys: { key: 'Escape' },
    description: 'Close dialogs / Cancel',
  },
]

export function KeyboardShortcuts() {
  const [open, setOpen] = useState(false)

  // Keyboard shortcut to open this dialog
  useKeyboardShortcuts(
    [
      {
        key: '/',
        ctrl: true,
        action: () => setOpen(true),
        description: 'Show keyboard shortcuts',
      },
    ],
    true
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" title="Keyboard shortcuts (Ctrl+/)">
          <Keyboard className="h-5 w-5" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Keyboard className="h-5 w-5" />
            Keyboard Shortcuts
          </DialogTitle>
          <DialogDescription>
            Use these keyboard shortcuts to navigate and interact with the application faster.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 mt-4">
          <div className="grid gap-4">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 rounded-lg border bg-card"
              >
                <span className="text-sm text-muted-foreground">
                  {shortcut.description}
                </span>
                <KbdGroup>
                  {shortcut.keys.ctrl && (
                    <Kbd>{navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}</Kbd>
                  )}
                  {shortcut.keys.alt && <Kbd>Alt</Kbd>}
                  {shortcut.keys.shift && <Kbd>Shift</Kbd>}
                  <Kbd>{shortcut.keys.key}</Kbd>
                </KbdGroup>
              </div>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

