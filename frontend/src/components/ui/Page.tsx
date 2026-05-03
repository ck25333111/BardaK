//────────────────────────────────────────
// frontend/src/components/ui/Page.tsx
// Общая обёртка страницы интерфейса BardaK.
//────────────────────────────────────────

import type { ReactNode } from "react"

type PageProps = {
  children: ReactNode
}

export function Page({ children }: PageProps) {
  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <section className="mx-auto max-w-3xl space-y-6">{children}</section>
    </main>
  )
}