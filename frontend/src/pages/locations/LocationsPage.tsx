//────────────────────────────────────────
// frontend/src/pages/locations/LocationsPage.tsx
// Страница локаций: загрузка списка и создание новой локации.
//────────────────────────────────────────

import { useEffect, useState } from "react"

import { createLocation, getLocations } from "@/api/locationsApi"
import { Button, Card, Page, Select, Textarea, TextInput } from "@/components/ui"
import type { Location } from "@/types/location"

export function LocationsPage() {
  const [locations, setLocations] = useState<Location[]>([])
  const [name, setName] = useState("")
  const [locationType, setLocationType] = useState("room")
  const [description, setDescription] = useState("")
  const [errorMessage, setErrorMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const loadLocations = async () => {
    setIsLoading(true)
    setErrorMessage("")

    try {
      const loadedLocations = await getLocations()
      setLocations(loadedLocations)
    } catch {
      setErrorMessage("Не удалось загрузить локации")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateLocation = async () => {
    const trimmedName = name.trim()
    const trimmedType = locationType.trim()
    const trimmedDescription = description.trim()

    if (!trimmedName) {
      setErrorMessage("Название локации обязательно")
      return
    }

    if (!trimmedType) {
      setErrorMessage("Тип локации обязателен")
      return
    }

    try {
      const createdLocation = await createLocation({
        name: trimmedName,
        location_type: trimmedType,
        parent_id: null,
        width_mm: null,
        depth_mm: null,
        height_mm: null,
        description: trimmedDescription || null,
      })

      setLocations((currentLocations) => [
        ...currentLocations,
        createdLocation,
      ])

      setName("")
      setLocationType("room")
      setDescription("")
      setErrorMessage("")
    } catch {
      setErrorMessage("Не удалось создать локацию")
    }
  }

  useEffect(() => {
    void loadLocations()
  }, [])

  return (
    <Page>
      <header>
        <h1 className="text-3xl font-bold">Локации</h1>
        <p className="mt-2 text-slate-400">
          Места хранения: комнаты, шкафы, полки, коробки и прочий домашний хаос.
        </p>
      </header>

      <Card>
        <h2 className="mb-4 text-xl font-semibold">Новая локация</h2>

        <div className="space-y-3">
          <TextInput
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Название, например: Кладовка"
          />

          <Select
            value={locationType}
            onChange={(event) => setLocationType(event.target.value)}
          >
            <option value="room">Комната</option>
            <option value="wardrobe">Шкаф</option>
            <option value="shelf">Полка</option>
            <option value="box">Коробка</option>
            <option value="drawer">Ящик</option>
            <option value="cell">Ячейка</option>
          </Select>

          <Textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Описание"
          />

          <Button onClick={handleCreateLocation}>Создать</Button>
        </div>
      </Card>

      {errorMessage && (
        <div className="rounded-lg border border-red-800 bg-red-950 p-4 text-red-200">
          {errorMessage}
        </div>
      )}

      <Card>
        <h2 className="mb-4 text-xl font-semibold">Список локаций</h2>

        {isLoading && <p className="text-slate-400">Загрузка...</p>}

        {!isLoading && locations.length === 0 && (
          <p className="text-slate-400">Локаций пока нет.</p>
        )}

        <ul className="space-y-3">
          {locations.map((location) => (
            <li
              key={location.id}
              className="rounded-lg border border-slate-800 bg-slate-950 p-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold">{location.name}</h3>

                  {location.description && (
                    <p className="mt-1 text-sm text-slate-400">
                      {location.description}
                    </p>
                  )}
                </div>

                <span className="rounded-full border border-emerald-800 bg-emerald-950 px-3 py-1 text-xs text-emerald-300">
                  {location.location_type}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </Card>
    </Page>
  )
}