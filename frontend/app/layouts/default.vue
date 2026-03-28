<script setup lang="ts">
const links = [
  { label: 'Field dashboard', to: '/field-dashboard', icon: 'i-lucide-map' }
]
</script>

<template>
  <div class="flex min-h-screen bg-background">
    <aside
      class="flex w-64 flex-col border-r border-default bg-elevated/50 p-4"
    >
      <div class="mb-6 flex items-center gap-2 px-2">
        <UIcon name="i-lucide-sprout" class="size-6 text-primary" />
        <span class="font-semibold tracking-tight">OpenDSS</span>
      </div>
      <UNavigationMenu
        :items="[links]"
        orientation="vertical"
        class="flex-1"
      />
    </aside>
    <div class="flex min-h-screen min-w-0 flex-1 flex-col">
      <slot />
    </div>
  </div>
</template>
