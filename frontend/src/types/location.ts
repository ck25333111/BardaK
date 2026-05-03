//────────────────────────────────────────
// frontend/src/types/location.ts
// Типы данных Location, которые frontend получает от backend.
//────────────────────────────────────────

export type Location = {
  id: number
  name: string
  location_type: string
  parent_id: number | null
  width_mm: number | null
  depth_mm: number | null
  height_mm: number | null
  description: string | null
  created_at: string
  updated_at: string
}

export type LocationCreatePayload = {
  name: string
  location_type: string
  parent_id: number | null
  width_mm: number | null
  depth_mm: number | null
  height_mm: number | null
  description: string | null
}