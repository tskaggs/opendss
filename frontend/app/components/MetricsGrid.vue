<script setup lang="ts">
import type { AnalyzeResponse, PrecipRisk } from '~/types/analyze'
import { celsiusToFahrenheit, kmhToMph, mmToInches } from '~/utils/measurements'

defineProps<{
  data: AnalyzeResponse | null
}>()

const { measurementSystem, temperatureUnit } = useMeasurementPreferences()

function riskLabel(r: PrecipRisk) {
  return r === 'low' ? 'Low' : r === 'medium' ? 'Medium' : 'High'
}

function formatSoilTemp(c: number) {
  if (temperatureUnit.value === 'fahrenheit') {
    return `${celsiusToFahrenheit(c).toFixed(1)}°F`
  }
  return `${c.toFixed(1)}°C`
}

function formatWind(kmh: number) {
  if (measurementSystem.value === 'imperial') {
    return `${kmhToMph(kmh).toFixed(1)} mph`
  }
  return `${kmh.toFixed(1)} km/h`
}

function formatPrecip(mm: number) {
  if (measurementSystem.value === 'imperial') {
    return `${mmToInches(mm).toFixed(2)} in`
  }
  return `${mm.toFixed(2)} mm`
}
</script>

<template>
  <div class="grid gap-4 sm:grid-cols-2">
    <UCard>
      <template #header>
        <div class="flex items-center gap-2 text-sm font-medium">
          <UIcon name="i-lucide-thermometer" class="size-4" />
          Current soil temp
        </div>
      </template>
      <p class="text-3xl font-semibold tabular-nums">
        {{ data ? formatSoilTemp(data.soil_temperature.value_c) : '—' }}
      </p>
      <p class="text-muted mt-1 text-xs">From NASA POWER / proxy series</p>
    </UCard>

    <UCard>
      <template #header>
        <div class="flex items-center gap-2 text-sm font-medium">
          <UIcon name="i-lucide-cloud-rain" class="size-4" />
          Precipitation risk
        </div>
      </template>
      <p class="text-3xl font-semibold">
        {{ data ? riskLabel(data.weather.precip_risk) : '—' }}
      </p>
      <p class="text-muted mt-1 text-xs">
        Next 6h:
        {{ data ? formatPrecip(data.weather.next_6h_precip_mm) : '—' }}
      </p>
    </UCard>

    <UCard>
      <template #header>
        <div class="flex items-center gap-2 text-sm font-medium">
          <UIcon name="i-lucide-wind" class="size-4" />
          Wind speed
        </div>
      </template>
      <p class="text-3xl font-semibold tabular-nums">
        {{ data ? formatWind(data.weather.wind_speed_kmh) : '—' }}
      </p>
      <p class="text-muted mt-1 text-xs">10 m, from POWER daily tail</p>
    </UCard>

    <UCard>
      <template #header>
        <div class="flex items-center gap-2 text-sm font-medium">
          <UIcon name="i-lucide-droplets" class="size-4" />
          Soil moisture
        </div>
      </template>
      <p class="text-3xl font-semibold tabular-nums">
        {{ data ? `${data.soil_moisture.value_percent.toFixed(0)}%` : '—' }}
      </p>
      <p class="text-muted mt-1 text-xs">
        Source: {{ data?.soil_moisture.source ?? '—' }}
      </p>
    </UCard>
  </div>
</template>
