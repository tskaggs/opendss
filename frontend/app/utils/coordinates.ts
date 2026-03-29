/** Parse and validate geographic coordinates for field analysis. */

export function isValidLatLng(lat: number, lng: number): boolean {
  return (
    Number.isFinite(lat) &&
    Number.isFinite(lng) &&
    lat >= -90 &&
    lat <= 90 &&
    lng >= -180 &&
    lng <= 180
  )
}

/**
 * Parse "lat, lng" or whitespace-separated numbers from a search string.
 * Returns null if the pair is missing or out of range.
 */
export function parseLatLngQuery(input: string): { lat: number; lng: number } | null {
  const parts = input.split(/[,\s]+/).map((s) => s.trim()).filter(Boolean)
  if (parts.length < 2) return null
  const lat = Number(parts[0])
  const lng = Number(parts[1])
  if (!isValidLatLng(lat, lng)) return null
  return { lat, lng }
}
