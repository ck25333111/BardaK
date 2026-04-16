//────────────────────────────────────────
// frontend/src/components/InputRow.tsx
// Строка ввода: controlled input + кнопка submit для строки
//────────────────────────────────────────

type InputRowProps = {
  placeholder: string
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
}

export function InputRow({ placeholder, value, onChange, onSubmit }: InputRowProps) {
  return (
    <div className="flex items-center gap-3">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="flex-1 rounded border border-gray-300 px-3 py-2 text-white-900 caret-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
      />

      <button
        type="button"
        onClick={onSubmit}
        className="h-10 w-10 rounded bg-blue-600 text-white transition hover:bg-blue-700"
      >
        ✓
      </button>
    </div>
  )
}
