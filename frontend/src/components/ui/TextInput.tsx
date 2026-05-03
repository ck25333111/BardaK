//────────────────────────────────────────
// frontend/src/components/ui/TextInput.tsx
// Общий текстовый input интерфейса BardaK.
//────────────────────────────────────────

import type { InputHTMLAttributes } from "react"

type TextInputProps = InputHTMLAttributes<HTMLInputElement>

export function TextInput({ className = "", ...props }: TextInputProps) {
  return (
    <input
      className={[
        "w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2",
        "text-slate-100 outline-none transition placeholder:text-slate-500",
        "focus:border-emerald-500",
        className,
      ].join(" ")}
      {...props}
    />
  )
}