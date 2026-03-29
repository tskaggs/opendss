<script setup lang="ts">
import type { AnalyzeResponse } from '~/types/analyze'

/** Avoid prop name `data` — it does not resolve reliably in Vue templates. */
const props = defineProps<{
  analyze: AnalyzeResponse | null
}>()

/** traditional | compare | modern */
const viewMode = ref<'traditional' | 'compare' | 'modern'>('compare')

const almanac = computed(() => props.analyze?.almanac ?? null)

function moonClipStyle(illumination: number) {
  const pct = Math.round(Math.min(1, Math.max(0, illumination)) * 100)
  return {
    background: `linear-gradient(90deg, var(--ui-primary) ${pct}%, var(--ui-bg-elevated) ${pct}%)`
  }
}
</script>

<template>
  <UCard
    v-if="analyze"
    class="border-amber-500/35 bg-amber-50/40 ring-1 ring-amber-500/25 dark:border-amber-500/30 dark:bg-amber-950/25 dark:ring-amber-500/20"
    :ui="{ body: 'space-y-4' }"
  >
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center gap-2 font-medium">
          <UIcon name="i-lucide-moon" class="size-5 text-amber-600 dark:text-amber-400" />
          <span>Traditional almanac</span>
        </div>
        <div v-if="almanac" class="flex flex-wrap gap-1">
          <UButton
            size="xs"
            :variant="viewMode === 'traditional' ? 'solid' : 'ghost'"
            color="neutral"
            @click="viewMode = 'traditional'"
          >
            Folk
          </UButton>
          <UButton
            size="xs"
            :variant="viewMode === 'compare' ? 'solid' : 'ghost'"
            color="neutral"
            @click="viewMode = 'compare'"
          >
            Compare
          </UButton>
          <UButton
            size="xs"
            :variant="viewMode === 'modern' ? 'solid' : 'ghost'"
            color="neutral"
            @click="viewMode = 'modern'"
          >
            Satellite
          </UButton>
        </div>
      </div>
    </template>

    <UAlert
      v-if="!almanac"
      color="neutral"
      variant="subtle"
      title="Almanac not in API response"
      description="The backend you are calling does not return an almanac object. Use the OpenDSS API that includes POST /analyze → almanac (pip install -r backend/requirements.txt, then restart uvicorn). Check NUXT_PUBLIC_API_BASE in .env points at that server, then run Analyze field again."
      icon="i-lucide-info"
    />

    <template v-else>
      <UAlert
        v-if="almanac.modern_traditional_alignment === 'caution' && almanac.wise_council_tip && viewMode !== 'modern'"
        color="warning"
        variant="subtle"
        title="Wise council"
        :description="almanac.wise_council_tip"
        icon="i-lucide-sparkles"
      />

      <div v-if="viewMode !== 'modern'" class="flex flex-col gap-4 sm:flex-row sm:items-start">
        <div class="flex shrink-0 flex-col items-center gap-2">
          <div
            class="border-default size-20 shrink-0 rounded-full border-2 shadow-inner"
            :style="moonClipStyle(almanac.moon.illumination)"
            :title="`Illumination ${(almanac.moon.illumination * 100).toFixed(0)}%`"
          />
          <p class="text-muted text-center text-xs">
            {{ almanac.moon.phase_name }}
          </p>
        </div>
        <div class="min-w-0 flex-1 space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <UBadge color="warning" variant="subtle">
              {{ almanac.recommendation_badge_label }}
            </UBadge>
            <span class="text-muted text-xs">
              Moon in {{ almanac.moon.zodiac_sign }} ({{ almanac.moon.zodiac_element }})
            </span>
          </div>
          <div>
            <div class="text-muted mb-1 flex justify-between text-xs">
              <span>Lunar cycle</span>
              <span class="tabular-nums">{{ (almanac.moon.lunar_cycle_progress * 100).toFixed(0) }}%</span>
            </div>
            <UProgress :model-value="almanac.moon.lunar_cycle_progress * 100" size="sm" />
          </div>
          <ul class="text-muted space-y-1 text-xs">
            <li v-if="almanac.phenology.mouse_ear_oak_likely">
              Oak “mouse ear” stage likely (GDD₁₀ heuristic).
            </li>
            <li v-if="almanac.phenology.dandelion_spring_likely">Spring dandelion bloom window likely.</li>
            <li v-if="almanac.phenology.gdd_base10_cumulative_ytd != null">
              YTD GDD₁₀ (approx.):
              <span class="text-default font-medium tabular-nums">{{
                almanac.phenology.gdd_base10_cumulative_ytd.toFixed(0)
              }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div
        v-if="viewMode === 'compare' || viewMode === 'modern'"
        class="border-default space-y-2 rounded-lg border border-dashed bg-white/50 p-3 dark:bg-neutral-950/40"
      >
        <p class="text-muted text-xs font-medium uppercase tracking-wide">Satellite snapshot</p>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span class="text-muted">Precip risk</span>
            <p class="font-medium capitalize">{{ analyze.weather.precip_risk }}</p>
          </div>
          <div>
            <span class="text-muted">Soil moisture</span>
            <p class="font-medium tabular-nums">{{ analyze.soil_moisture.value_percent.toFixed(0) }}%</p>
          </div>
          <div>
            <span class="text-muted">Next 6h precip</span>
            <p class="font-medium tabular-nums">{{ analyze.weather.next_6h_precip_mm.toFixed(1) }} mm</p>
          </div>
          <div>
            <span class="text-muted">Humidity</span>
            <p class="font-medium tabular-nums">{{ analyze.weather.relative_humidity_percent.toFixed(0) }}%</p>
          </div>
        </div>
      </div>
    </template>
  </UCard>
</template>
