//────────────────────────────────────────
// frontend/src/pages/categories/CategoriesPage.tsx
// Страница категорий: загрузка списка и создание новой категории.
//────────────────────────────────────────

import { useEffect, useState } from "react"

import { createCategory, getCategories } from "@/api/categoriesApi"
import { Button, Card, Page, Textarea, TextInput } from "@/components/ui"
import type { Category } from "@/types/category"

export function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [errorMessage, setErrorMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const loadCategories = async () => {
    setIsLoading(true)
    setErrorMessage("")

    try {
      const loadedCategories = await getCategories()
      setCategories(loadedCategories)
    } catch {
      setErrorMessage("Не удалось загрузить категории")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateCategory = async () => {
    const trimmedName = name.trim()
    const trimmedDescription = description.trim()

    if (!trimmedName) {
      setErrorMessage("Название категории обязательно")
      return
    }

    try {
      const createdCategory = await createCategory({
        name: trimmedName,
        description: trimmedDescription || null,
      })

      setCategories((currentCategories) => [
        ...currentCategories,
        createdCategory,
      ])

      setName("")
      setDescription("")
      setErrorMessage("")
    } catch {
      setErrorMessage("Не удалось создать категорию")
    }
  }

  useEffect(() => {
    void loadCategories()
  }, [])

  return (
    <Page>
      <header>
        <h1 className="text-3xl font-bold">Категории</h1>
        <p className="mt-2 text-slate-400">
          Первый реальный экран BardaK, подключённый к backend.
        </p>
      </header>

      <Card>
        <h2 className="mb-4 text-xl font-semibold">Новая категория</h2>

        <div className="space-y-3">
          <TextInput
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Название"
          />

          <Textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Описание"
          />

          <Button onClick={handleCreateCategory}>Создать</Button>
        </div>
      </Card>

      {errorMessage && (
        <div className="rounded-lg border border-red-800 bg-red-950 p-4 text-red-200">
          {errorMessage}
        </div>
      )}

      <Card>
        <h2 className="mb-4 text-xl font-semibold">Список категорий</h2>

        {isLoading && <p className="text-slate-400">Загрузка...</p>}

        {!isLoading && categories.length === 0 && (
          <p className="text-slate-400">Категорий пока нет.</p>
        )}

        <ul className="space-y-3">
          {categories.map((category) => (
            <li
              key={category.id}
              className="rounded-lg border border-slate-800 bg-slate-950 p-4"
            >
              <h3 className="font-semibold">{category.name}</h3>

              {category.description && (
                <p className="mt-1 text-sm text-slate-400">
                  {category.description}
                </p>
              )}
            </li>
          ))}
        </ul>
      </Card>
    </Page>
  )
}