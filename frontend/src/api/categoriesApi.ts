//────────────────────────────────────────
// frontend/src/api/categoriesApi.ts
// API-клиент для работы с категориями через backend.
//────────────────────────────────────────

import type { Category, CategoryCreatePayload } from "@/types/category"

const API_BASE_URL = "http://localhost:8000/api/v1"

export async function getCategories(): Promise<Category[]> {
  const response = await fetch(`${API_BASE_URL}/categories`)

  if (!response.ok) {
    throw new Error("Не удалось загрузить категории")
  }

  return response.json()
}

export async function createCategory(
  payload: CategoryCreatePayload,
): Promise<Category> {
  const response = await fetch(`${API_BASE_URL}/categories`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error("Не удалось создать категорию")
  }

  return response.json()
}