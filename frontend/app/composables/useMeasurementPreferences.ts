import type { MeasurementSystem, TemperatureUnit } from '~/utils/localizeAgronomic'

const MS_KEY = 'opendss-measurement-system'
const TU_KEY = 'opendss-temperature-unit'

export function useMeasurementPreferences() {
  const measurementSystem = useState<MeasurementSystem>('opendss-measurement-system', () => 'metric')
  const temperatureUnit = useState<TemperatureUnit>('opendss-temperature-unit', () => 'celsius')

  if (import.meta.client) {
    onMounted(() => {
      const ms = localStorage.getItem(MS_KEY)
      const tu = localStorage.getItem(TU_KEY)
      if (ms === 'metric' || ms === 'imperial') measurementSystem.value = ms
      if (tu === 'celsius' || tu === 'fahrenheit') temperatureUnit.value = tu
    })

    watch(measurementSystem, (v) => {
      localStorage.setItem(MS_KEY, v)
    })
    watch(temperatureUnit, (v) => {
      localStorage.setItem(TU_KEY, v)
    })
  }

  return { measurementSystem, temperatureUnit }
}
