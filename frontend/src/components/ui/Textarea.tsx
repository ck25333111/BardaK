//────────────────────────────────────────
// frontend/src/components/ui/Textarea.tsx
// Общая textarea интерфейса BardaK.
//────────────────────────────────────────

import type { TextareaHTMLAttributes } from "react"

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement>

export function Textarea({ className = "", ...props }: TextareaProps) {
  return (
    <textarea
      className={[
        "min-h-24 w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2",
        "text-slate-100 outline-none transition placeholder:text-slate-500",
        "focus:border-emerald-500",
        className,
      ].join(" ")}
      {...props}
    />
  )
}