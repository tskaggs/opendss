<script setup lang="ts">
const { measurementSystem, temperatureUnit } = useMeasurementPreferences()

const systemItems = [
  { label: 'Metric', value: 'metric' as const },
  { label: 'Standard', value: 'imperial' as const }
]

const tempItems = [
  { label: 'Celsius', value: 'celsius' as const },
  { label: 'Fahrenheit', value: 'fahrenheit' as const }
]
</script>

<template>
  <div
    class="flex flex-wrap items-end gap-3 border-default border-t pt-3 lg:border-t-0 lg:pt-0 lg:pl-4 lg:border-l"
  >
    <UFormField label="Measurements" class="min-w-[150px]">
      <USelect
        v-model="measurementSystem"
        :items="systemItems"
        value-key="value"
        label-key="label"
        size="sm"
        class="w-full"
      />
    </UFormField>
    <UFormField label="Temperature" class="min-w-[150px]">
      <USelect
        v-model="temperatureUnit"
        :items="tempItems"
        value-key="value"
        label-key="label"
        size="sm"
        class="w-full"
      />
    </UFormField>
  </div>
</template>
