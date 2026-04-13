//────────────────────────────────────────
// frontend/src/components/Button.tsx
// Переиспользуемая кнопка (пока не используется в UI).
//────────────────────────────────────────

type ButtonProps = {
  title: string
  onClick?: () => void
}

export function Button({ title, onClick }: ButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="mt-4 rounded bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
    >
      {title}
    </button>
  )
}
