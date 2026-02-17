//────────────────────────────────────────
// frontend/src/components/InputRow.tsx
// Одна строка ввода: текстовое поле + кнопка “✓”, вызывает onSubmit.
//────────────────────────────────────────

import { useState } from "react"

type InputRowProps = {
  placeholder: string
  onSubmit: (value: string) => void
}

export function InputRow({ placeholder, onSubmit }: InputRowProps) {
  const [value, setValue] = useState("")

  const handleClick = () => {
    if (!value.trim()) return
    onSubmit(value)
    setValue("")
  }

  return (
    <div className="flex items-center gap-3">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="flex-1 rounded border border-gray-300 px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500"
      />

      <button
        type="button"
        onClick={handleClick}
        className="h-10 w-10 rounded bg-blue-600 text-white transition hover:bg-blue-700"
      >
        ✓
      </button>
    </div>
  )
}
