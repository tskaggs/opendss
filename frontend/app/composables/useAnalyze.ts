import type { AnalyzeResponse } from '~/types/analyze'

export function useAnalyze() {
  const config = useRuntimeConfig()

  async function analyzeField(lat: number, lng: number) {
    const base = config.public.apiBase as string
    return await $fetch<AnalyzeResponse>(`${base.replace(/\/$/, '')}/analyze`, {
      method: 'POST',
      body: { lat, lng }
    })
  }

  return { analyzeField }
}
