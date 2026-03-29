<script setup lang="ts">
import type { AnalyzeResponse } from '~/types/analyze'
import { isValidLatLng, parseLatLngQuery } from '~/utils/coordinates'

definePageMeta({
  layout: 'default'
})

/** Degrees — if current pin differs from last analysis by more than this, metrics are stale. */
const COORD_EPSILON = 1e-4
const AUTO_ANALYZE_DEBOUNCE_MS = 600

const DEFAULT_LAT = 40.7128
const DEFAULT_LNG = -74.006

const { analyzeField } = useAnalyze()

const lat = ref(DEFAULT_LAT)
const lng = ref(DEFAULT_LNG)
const query = ref(`${DEFAULT_LAT}, ${DEFAULT_LNG}`)

const loading = ref(false)
const errorMsg = ref<string | null>(null)
/** Large JSON payload: shallow ref avoids deep reactivity cost. */
const result = shallowRef<AnalyzeResponse | null>(null)

/** Suppress debounced auto-analyze when coordinates change from manual Analyze (search/button). */
const skipAutoAnalyze = ref(false)

const sidebarOpen = useState('sidebar-open', () => true)

const analysisStale = computed(() => {
  const r = result.value
  if (!r) return false
  return (
    Math.abs(lat.value - r.location.lat) > COORD_EPSILON ||
    Math.abs(lng.value - r.location.lng) > COORD_EPSILON
  )
})

function formatAnalyzedLocation(loc: { lat: number; lng: number }) {
  return `${loc.lat.toFixed(5)}, ${loc.lng.toFixed(5)}`
}

function syncQueryFromCoords() {
  query.value = `${lat.value.toFixed(5)}, ${lng.value.toFixed(5)}`
}

function applyQueryToCoords(): boolean {
  const parsed = parseLatLngQuery(query.value)
  if (!parsed) return false
  lat.value = parsed.lat
  lng.value = parsed.lng
  syncQueryFromCoords()
  return true
}

function onCoords(coords: { lat: number; lng: number }) {
  if (!isValidLatLng(coords.lat, coords.lng)) return
  lat.value = coords.lat
  lng.value = coords.lng
  syncQueryFromCoords()
}

async function runAnalyzeCore() {
  loading.value = true
  errorMsg.value = null
  try {
    result.value = await analyzeField(lat.value, lng.value)
  } catch (e: unknown) {
    if (import.meta.dev) {
      console.error(e)
    }
    errorMsg.value =
      'Unable to analyze this location. Check that the API is running and try again.'
    result.value = null
  } finally {
    loading.value = false
  }
}

async function runAnalyze() {
  clearPendingAutoAnalyzeTimer()
  skipAutoAnalyze.value = true
  try {
    if (!applyQueryToCoords()) {
      errorMsg.value =
        'Enter a valid latitude and longitude (e.g. 40.71, -74.00). Latitude must be between -90 and 90, longitude between -180 and 180.'
      result.value = null
      return
    }
    await runAnalyzeCore()
  } finally {
    nextTick(() => {
      skipAutoAnalyze.value = false
    })
  }
}

let autoAnalyzeTimer: ReturnType<typeof setTimeout> | null = null

function clearPendingAutoAnalyzeTimer() {
  if (autoAnalyzeTimer) {
    clearTimeout(autoAnalyzeTimer)
    autoAnalyzeTimer = null
  }
}

watch([lat, lng], () => {
  if (skipAutoAnalyze.value || !isValidLatLng(lat.value, lng.value)) return
  clearPendingAutoAnalyzeTimer()
  autoAnalyzeTimer = setTimeout(() => {
    autoAnalyzeTimer = null
    if (skipAutoAnalyze.value) return
    void runAnalyzeCore()
  }, AUTO_ANALYZE_DEBOUNCE_MS)
})

onBeforeUnmount(() => {
  clearPendingAutoAnalyzeTimer()
})
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <header
      class="border-b border-default bg-background/80 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
      <div
        class="mx-auto flex max-w-[1600px] flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"
      >
        <div class="flex min-w-0 flex-1 flex-wrap items-center gap-2">
          <UButton
            icon="i-lucide-panel-left"
            color="neutral"
            variant="ghost"
            square
            class="shrink-0"
            aria-label="Toggle sidebar"
            @click="sidebarOpen = !sidebarOpen"
          />
          <UInput
            v-model="query"
            icon="i-lucide-search"
            class="min-w-0 flex-1 sm:min-w-[220px]"
            placeholder="lat, lng (e.g. 40.71, -74.00)"
            autocomplete="off"
            @keyup.enter="runAnalyze"
          />
          <UButton
            color="primary"
            :loading="loading"
            :disabled="loading"
            @click="runAnalyze"
          >
            Analyze field
          </UButton>
        </div>
        <div class="flex shrink-0 flex-col gap-3 lg:flex-row lg:items-start lg:justify-end">
          <MeasurementPreferences />
        </div>
      </div>
      <UAlert
        v-if="errorMsg"
        class="mt-3"
        color="error"
        variant="subtle"
        :title="errorMsg"
      />
    </header>

    <main class="mx-auto w-full max-w-[1600px] flex-1 p-4">
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-3 lg:items-start">
        <section class="min-h-[320px] lg:col-span-1">
          <UCard class="h-full">
            <template #header>
              <div class="flex items-center gap-2 font-medium">
                <UIcon name="i-lucide-map-pin" />
                Field map
              </div>
            </template>
            <ClientOnly>
              <FieldMap :lat="lat" :lng="lng" @update:coords="onCoords" />
              <template #fallback>
                <div class="text-muted py-16 text-center text-sm">Loading map…</div>
              </template>
            </ClientOnly>
          </UCard>
        </section>

        <section class="flex flex-col gap-4 lg:col-span-1">
          <div v-if="result" class="space-y-2">
            <p class="text-muted text-sm">
              Analyzed:
              <span class="text-default font-medium tabular-nums">{{
                formatAnalyzedLocation(result.location)
              }}</span>
            </p>
            <UAlert
              v-if="analysisStale"
              color="warning"
              variant="subtle"
              title="Map location changed"
              description="Click Analyze field to refresh metrics for the current pin."
            />
          </div>
          <MetricsGrid :data="result" />
          <AlmanacCard v-if="result" :analyze="result" />
          <UCard>
            <template #header>
              <span class="font-medium">Agronomic signals</span>
            </template>
            <AgronomicAlerts :agronomy="result?.agronomy ?? null" />
          </UCard>
        </section>

        <section class="lg:col-span-1">
          <UCard class="h-full">
            <template #header>
              <span class="font-medium">7-day soil trends</span>
            </template>
            <ClientOnly>
              <SoilCharts :data="result" />
              <template #fallback>
                <div class="text-muted py-10 text-center text-sm">Loading charts…</div>
              </template>
            </ClientOnly>
          </UCard>
        </section>
      </div>
    </main>
  </div>
</template>
