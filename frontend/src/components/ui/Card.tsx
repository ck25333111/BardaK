//────────────────────────────────────────
// frontend/src/components/ui/Card.tsx
// Общая карточка интерфейса BardaK.
//────────────────────────────────────────

import type { ReactNode } from "react"

type CardProps = {
  children: ReactNode
  className?: string
}

export function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={[
        "rounded-xl border border-slate-800 bg-slate-900 p-5",
        className,
      ].join(" ")}
    >
      {children}
    </div>
  )
}