import type { AnalyzeResponse } from '~/types/analyze'
import { isValidLatLng } from '~/utils/coordinates'

const ANALYZE_TIMEOUT_MS = 60_000

export function useAnalyze() {
  const config = useRuntimeConfig()

  async function analyzeField(lat: number, lng: number) {
    if (!isValidLatLng(lat, lng)) {
      throw new Error('Invalid coordinates')
    }
    const base = config.public.apiBase as string
    return await $fetch<AnalyzeResponse>(`${base.replace(/\/$/, '')}/analyze`, {
      method: 'POST',
      body: { lat, lng },
      timeout: ANALYZE_TIMEOUT_MS
    })
  }

  return { analyzeField }
}
