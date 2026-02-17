//────────────────────────────────────────
// frontend/src/components/FormBlock.tsx
// Блок из трёх InputRow. Пока просто логирует отправку в консоль.
//────────────────────────────────────────

import { InputRow } from "./InputRow"

export function FormBlock() {
  const handleSubmit = (value: string) => {
    console.log("Отправлено:", value)
  }

  return (
    <div className="space-y-4">
      <InputRow placeholder="Первое поле" onSubmit={handleSubmit} />
      <InputRow placeholder="Второе поле" onSubmit={handleSubmit} />
      <InputRow placeholder="Третье поле" onSubmit={handleSubmit} />
    </div>
  )
}
