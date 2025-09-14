import React from 'react'
import { cn } from '@/lib/utils'

const ScrollArea = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "relative overflow-hidden",
      className
    )}
    {...props}
  >
    <div className="h-full w-full overflow-auto">
      {props.children}
    </div>
  </div>
))
ScrollArea.displayName = "ScrollArea"

export { ScrollArea }