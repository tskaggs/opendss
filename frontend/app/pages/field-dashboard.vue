<script setup lang="ts">
import type { AnalyzeResponse } from '~/types/analyze'

definePageMeta({
  layout: 'default'
})

const { analyzeField } = useAnalyze()

const lat = ref(40.7128)
const lng = ref(-74.006)
const query = ref(`${lat.value}, ${lng.value}`)

const loading = ref(false)
const errorMsg = ref<string | null>(null)
const result = ref<AnalyzeResponse | null>(null)

function applyQuery() {
  const parts = query.value.split(/[,\s]+/).map((s) => s.trim()).filter(Boolean)
  if (parts.length >= 2) {
    const la = Number(parts[0])
    const ln = Number(parts[1])
    if (!Number.isNaN(la) && !Number.isNaN(ln)) {
      lat.value = la
      lng.value = ln
    }
  }
}

function onCoords(coords: { lat: number; lng: number }) {
  lat.value = coords.lat
  lng.value = coords.lng
  query.value = `${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}`
}

async function runAnalyze() {
  loading.value = true
  errorMsg.value = null
  try {
    applyQuery()
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
</script>

<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <header
      class="border-b border-default bg-background/80 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/60"
    >
      <div
        class="mx-auto flex max-w-[1600px] flex-col gap-3 lg:flex-row lg:items-center lg:justify-between"
      >
        <div class="flex flex-1 flex-wrap items-center gap-2">
          <UInput
            v-model="query"
            icon="i-lucide-search"
            class="min-w-[220px] flex-1"
            placeholder="lat, lng (e.g. 40.71, -74.00)"
            @keyup.enter="runAnalyze"
          />
          <UButton color="primary" :loading="loading" @click="runAnalyze">
            Analyze field
          </UButton>
        </div>
        <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-end">
          <MeasurementPreferences />
          <div class="text-muted shrink-0 text-sm tabular-nums lg:text-right">
            Selected: {{ lat.toFixed(5) }}, {{ lng.toFixed(5) }}
          </div>
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
          <MetricsGrid :data="result" />
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
