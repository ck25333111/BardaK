//────────────────────────────────────────
// frontend/src/api/locationsApi.ts
// API-клиент для работы с локациями через backend.
//────────────────────────────────────────

import type { Location, LocationCreatePayload } from "@/types/location"

const API_BASE_URL = "http://localhost:8000/api/v1"

export async function getLocations(): Promise<Location[]> {
  const response = await fetch(`${API_BASE_URL}/locations`)

  if (!response.ok) {
    throw new Error("Не удалось загрузить локации")
  }

  return response.json()
}

export async function createLocation(
  payload: LocationCreatePayload,
): Promise<Location> {
  const response = await fetch(`${API_BASE_URL}/locations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error("Не удалось создать локацию")
  }

  return response.json()
}