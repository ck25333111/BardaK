//────────────────────────────────────────
// frontend/src/types/category.ts
// Типы данных Category, которые frontend получает от backend.
//────────────────────────────────────────

export type Category = {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

export type CategoryCreatePayload = {
  name: string
  description: string | null
}