<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import 'leaflet/dist/leaflet.css'

const props = defineProps<{
  lat: number
  lng: number
}>()

const emit = defineEmits<{
  'update:coords': [{ lat: number; lng: number }]
}>()

const mapEl = ref<HTMLElement | null>(null)
let map: import('leaflet').Map | null = null
let marker: import('leaflet').Marker | null = null

async function initMap() {
  if (!mapEl.value || !import.meta.client) return
  const L = await import('leaflet')

  map = L.map(mapEl.value).setView([props.lat, props.lng], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
  }).addTo(map)

  marker = L.marker([props.lat, props.lng], { draggable: true }).addTo(map)
  marker.on('dragend', () => {
    const ll = marker!.getLatLng()
    emit('update:coords', { lat: ll.lat, lng: ll.lng })
  })

  map.on('click', (e: import('leaflet').LeafletMouseEvent) => {
    const { lat, lng } = e.latlng
    marker!.setLatLng([lat, lng])
    emit('update:coords', { lat, lng })
  })
}

onMounted(() => {
  void initMap()
})

watch(
  () => [props.lat, props.lng],
  ([la, ln]) => {
    if (map && marker) {
      marker.setLatLng([la, ln])
      map.setView([la, ln], map.getZoom())
    }
  }
)

onBeforeUnmount(() => {
  map?.remove()
  map = null
  marker = null
})
</script>

<template>
  <div class="flex h-full min-h-[280px] flex-col gap-2">
    <p class="text-muted text-sm">
      Click the map or drag the pin to set your field location. Boundary tools can plug in here later.
    </p>
    <div
      ref="mapEl"
      class="min-h-[260px] w-full flex-1 rounded-lg border border-default overflow-hidden"
    />
  </div>
</template>
