//────────────────────────────────────────
// frontend/src/components/ui/Button.tsx
// Общая кнопка интерфейса BardaK.
//────────────────────────────────────────

import type { ButtonHTMLAttributes, ReactNode } from "react"

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode
}

export function Button({ children, className = "", ...props }: ButtonProps) {
  return (
    <button
      type="button"
      className={[
        "rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white",
        "transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60",
        className,
      ].join(" ")}
      {...props}
    >
      {children}
    </button>
  )
}