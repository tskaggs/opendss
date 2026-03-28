export type SprayStatus = 'safe' | 'caution' | 'danger'

export type PrecipRisk = 'low' | 'medium' | 'high'

export interface AnalyzeLocation {
  lat: number
  lng: number
}

export interface WeatherSeriesPoint {
  date: string
  temp_c?: number | null
  precip_mm?: number | null
  wind_kmh?: number | null
  rh_percent?: number | null
}

export interface WeatherData {
  wind_speed_kmh: number
  relative_humidity_percent: number
  next_6h_precip_mm: number
  precip_risk: PrecipRisk
  series_7d: WeatherSeriesPoint[]
}

export interface SoilMoistureSeriesPoint {
  date: string
  value_percent: number
}

export interface SoilMoistureData {
  value_percent: number
  source: 'mock'
  series_7d: SoilMoistureSeriesPoint[]
}

export interface SoilTempSeriesPoint {
  date: string
  value_c: number
}

export interface SoilTemperatureData {
  value_c: number
  series_7d: SoilTempSeriesPoint[]
}

export interface SoilProperties {
  sand_percent?: number | null
  silt_percent?: number | null
  clay_percent?: number | null
  bulk_density_kg_m3?: number | null
  organic_carbon_g_kg?: number | null
}

export interface SprayInfo {
  status: SprayStatus
  reasons: string[]
}

export interface AgronomyData {
  ready_to_plant: boolean
  ready_to_plant_reason: string
  spray: SprayInfo
}

export interface AnalyzeResponse {
  location: AnalyzeLocation
  weather: WeatherData
  soil_moisture: SoilMoistureData
  soil_temperature: SoilTemperatureData
  soil_properties: SoilProperties
  agronomy: AgronomyData
}
