<script setup lang="ts">
import type { AgronomyData, SprayStatus } from '~/types/analyze'
import { localizeAgronomicText } from '~/utils/localizeAgronomic'

const props = defineProps<{
  agronomy: AgronomyData | null
}>()

const { measurementSystem, temperatureUnit } = useMeasurementPreferences()

const localizedPlantReason = computed(() => {
  if (!props.agronomy) return ''
  return localizeAgronomicText(
    props.agronomy.ready_to_plant_reason,
    temperatureUnit.value,
    measurementSystem.value
  )
})

const localizedSprayReasons = computed(() => {
  if (!props.agronomy) return []
  return props.agronomy.spray.reasons.map((r) =>
    localizeAgronomicText(r, temperatureUnit.value, measurementSystem.value)
  )
})

function sprayColor(s: SprayStatus) {
  if (s === 'safe') return 'success' as const
  if (s === 'caution') return 'warning' as const
  return 'error' as const
}

function sprayTitle(s: SprayStatus) {
  if (s === 'safe') return 'Spray window: favorable'
  if (s === 'caution') return 'Spray window: caution'
  return 'Spray window: hold'
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <UAlert
      v-if="agronomy"
      :color="agronomy.ready_to_plant ? 'success' : 'warning'"
      variant="subtle"
      :title="agronomy.ready_to_plant ? 'Ready to plant' : 'Not ready to plant'"
      :description="localizedPlantReason"
    />

    <UAlert
      v-if="agronomy"
      :color="sprayColor(agronomy.spray.status)"
      variant="subtle"
      :title="sprayTitle(agronomy.spray.status)"
    >
      <ul class="list-inside list-disc text-sm">
        <li v-for="(r, i) in localizedSprayReasons" :key="i">
          {{ r }}
        </li>
      </ul>
    </UAlert>

    <UAlert
      v-if="!agronomy"
      color="neutral"
      variant="subtle"
      title="Run analysis"
      description="Choose coordinates and press Analyze to evaluate spray and planting conditions."
    />
  </div>
</template>
