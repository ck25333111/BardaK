//────────────────────────────────────────
// frontend/src/App.tsx
// Корневой компонент приложения. Рендерит базовую страницу и форму.
//────────────────────────────────────────

import { FormBlock } from "./components/FormBlock"

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-10">
      <div className="mx-auto max-w-xl rounded bg-white p-6 shadow">
        <h1 className="mb-6 text-2xl font-bold">Три горизонтальных поля</h1>
        <FormBlock />
      </div>
    </div>
  )
}

export default App
