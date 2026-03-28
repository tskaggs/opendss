<script setup lang="ts">
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
  type ChartData,
  type ChartOptions
} from 'chart.js'
import { Line } from 'vue-chartjs'
import type { AnalyzeResponse } from '~/types/analyze'
import { celsiusToFahrenheit } from '~/utils/measurements'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

const props = defineProps<{
  data: AnalyzeResponse | null
}>()

const { temperatureUnit } = useMeasurementPreferences()

const moistureChart = computed<ChartData<'line'>>(() => {
  const s = props.data?.soil_moisture.series_7d ?? []
  return {
    labels: s.map((p) => p.date.slice(5)),
    datasets: [
      {
        label: 'Soil moisture %',
        data: s.map((p) => p.value_percent),
        borderColor: '#16a34a',
        backgroundColor: 'rgba(22,163,74,0.15)',
        tension: 0.25,
        fill: true
      }
    ]
  }
})

const moistureOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' }
  },
  scales: {
    y: { beginAtZero: false }
  }
}))

const tempChart = computed<ChartData<'line'>>(() => {
  const s = props.data?.soil_temperature.series_7d ?? []
  const unit = temperatureUnit.value
  const values =
    unit === 'celsius'
      ? s.map((p) => p.value_c)
      : s.map((p) => celsiusToFahrenheit(p.value_c))
  const label = unit === 'celsius' ? 'Soil temp °C' : 'Soil temp °F'
  return {
    labels: s.map((p) => p.date.slice(5)),
    datasets: [
      {
        label,
        data: values,
        borderColor: '#ca8a04',
        backgroundColor: 'rgba(202,138,4,0.12)',
        tension: 0.25,
        fill: true
      }
    ]
  }
})

const tempOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' }
  },
  scales: {
    y: {
      beginAtZero: false,
      title: {
        display: true,
        text: temperatureUnit.value === 'fahrenheit' ? '°F' : '°C'
      }
    }
  }
}))
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="h-56">
      <Line v-if="data" :data="moistureChart" :options="moistureOptions" />
      <div
        v-else
        class="text-muted flex h-full items-center justify-center rounded-lg border border-dashed border-default text-sm"
      >
        Moisture trend (7-day) appears after analysis
      </div>
    </div>
    <div class="h-56">
      <Line v-if="data" :data="tempChart" :options="tempOptions" />
      <div
        v-else
        class="text-muted flex h-full items-center justify-center rounded-lg border border-dashed border-default text-sm"
      >
        Temperature trend (7-day) appears after analysis
      </div>
    </div>
  </div>
</template>
