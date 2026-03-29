import type { AnalyzeResponse } from '~/types/analyze'
import { isValidLatLng } from '~/utils/coordinates'

const ANALYZE_TIMEOUT_MS = 60_000

/** Ensures runtime `apiBase` is a safe http(s) origin (no javascript:, file:, etc.). */
function assertHttpApiBase(base: string): string {
  const trimmed = base.trim().replace(/\/$/, '')
  let parsed: URL
  try {
    parsed = new URL(trimmed)
  } catch {
    throw new Error('Invalid API base URL')
  }
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    throw new Error('API base must use http or https')
  }
  return trimmed
}

export function useAnalyze() {
  const config = useRuntimeConfig()

  async function analyzeField(lat: number, lng: number) {
    if (!isValidLatLng(lat, lng)) {
      throw new Error('Invalid coordinates')
    }
    const base = assertHttpApiBase(config.public.apiBase as string)
    return await $fetch<AnalyzeResponse>(`${base}/analyze`, {
      method: 'POST',
      body: { lat, lng },
      timeout: ANALYZE_TIMEOUT_MS
    })
  }

  return { analyzeField }
}
