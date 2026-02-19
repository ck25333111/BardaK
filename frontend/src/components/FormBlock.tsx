//────────────────────────────────────────
// frontend/src/components/FormBlock.tsx
// Держит значения 3 полей и отправляет их на backend
//────────────────────────────────────────

import { useState } from "react"
import { InputRow } from "@/components/InputRow"

type ThreeFieldsPayload = {
  first: string
  second: string
  third: string
}

export function FormBlock() {
  const [first, setFirst] = useState("")
  const [second, setSecond] = useState("")
  const [third, setThird] = useState("")
  const [lastResponse, setLastResponse] = useState<string>("")

  const clearAll = () => {
    setFirst("")
    setSecond("")
    setThird("")
  }

  const sendToBackend = async (payload: ThreeFieldsPayload) => {
    const res = await fetch("http://localhost:8000/api/v1/dev/echo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })

    const data = await res.json()
    setLastResponse(JSON.stringify(data, null, 2))
  }

  return (
    <div className="space-y-4">
      <InputRow
        placeholder="Первое поле"
        value={first}
        onChange={setFirst}
        onSubmit={() => {
          console.log("Первое:", first)
        }}
      />

      <InputRow
        placeholder="Второе поле"
        value={second}
        onChange={setSecond}
        onSubmit={() => {
          console.log("Второе:", second)
        }}
      />

      <InputRow
        placeholder="Третье поле"
        value={third}
        onChange={setThird}
        onSubmit={() => {
          console.log("Третье:", third)
        }}
      />

      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={() => sendToBackend({ first, second, third })}
          className="rounded bg-emerald-600 px-4 py-2 text-white transition hover:bg-emerald-700"
        >
          Отправить на backend
        </button>

        <button
          type="button"
          onClick={clearAll}
          className="rounded bg-gray-200 px-4 py-2 text-gray-900 transition hover:bg-gray-300"
        >
          Очистить всё
        </button>
      </div>

      {lastResponse && (
        <pre className="rounded bg-gray-50 p-3 text-xs text-gray-900 overflow-auto">
          {lastResponse}
        </pre>
      )}
    </div>
  )
}
