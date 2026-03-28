/**
 * Rewrite backend agronomic strings (metric) for display in the selected units.
 * Backend messages use °C, km/h, and mm; we convert patterns in display order.
 */

import { celsiusToFahrenheit, kmhToMph, mmToInches } from '~/utils/measurements'

export type MeasurementSystem = 'metric' | 'imperial'
export type TemperatureUnit = 'celsius' | 'fahrenheit'

export function localizeAgronomicText(
  text: string,
  temperatureUnit: TemperatureUnit,
  measurementSystem: MeasurementSystem
): string {
  let s = text

  if (measurementSystem === 'imperial') {
    s = s.replace(
      /(\d+\.?\d*)\s*[–-]\s*(\d+\.?\d*)\s*km\/h/g,
      (_, a: string, b: string) =>
        `${kmhToMph(Number(a)).toFixed(0)}–${kmhToMph(Number(b)).toFixed(0)} mph`
    )
    s = s.replace(/(\d+\.?\d*)\s*km\/h/g, (_, n: string) => `${kmhToMph(Number(n)).toFixed(1)} mph`)
    s = s.replace(/(\d+\.?\d*)\s*mm/g, (_, n: string) => `${mmToInches(Number(n)).toFixed(2)} in`)
  }

  if (temperatureUnit === 'fahrenheit') {
    s = s.replace(/(\d+\.?\d*)\s*°C/g, (_, n: string) => `${celsiusToFahrenheit(Number(n)).toFixed(1)}°F`)
    s = s.replace(/(\d+\.?\d*)°C/g, (_, n: string) => `${celsiusToFahrenheit(Number(n)).toFixed(1)}°F`)
  }

  return s
}
