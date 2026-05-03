//────────────────────────────────────────
// frontend/src/components/ui/Select.tsx
// Общий select интерфейса BardaK.
//────────────────────────────────────────

import type { SelectHTMLAttributes } from "react"

type SelectProps = SelectHTMLAttributes<HTMLSelectElement>

export function Select({ className = "", ...props }: SelectProps) {
  return (
    <select
      className={[
        "w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2",
        "text-slate-100 outline-none transition",
        "focus:border-emerald-500",
        className,
      ].join(" ")}
      {...props}
    />
  )
}