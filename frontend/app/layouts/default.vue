<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const sidebarOpen = useState('sidebar-open', () => true)

const links: NavigationMenuItem[] = [
  { label: 'Field dashboard', to: '/field-dashboard', icon: 'i-lucide-map' }
]
</script>

<template>
  <div
    class="flex min-h-screen flex-1 bg-neutral-50 dark:bg-neutral-950"
  >
    <USidebar
      v-model:open="sidebarOpen"
      collapsible="icon"
      rail
      variant="inset"
      title="OpenDSS"
      :ui="{
        container: 'h-full',
        inner: 'bg-elevated/25 divide-transparent',
        body: 'py-0'
      }"
    >
      <template #header>
        <div class="flex min-w-0 items-center gap-2 overflow-hidden px-1">
          <UIcon name="i-lucide-sprout" class="size-6 shrink-0 text-primary" />
          <span class="truncate font-semibold tracking-tight">OpenDSS</span>
        </div>
      </template>

      <UNavigationMenu
        :items="[links]"
        orientation="vertical"
        :ui="{ link: 'p-1.5 overflow-hidden' }"
      />
    </USidebar>

    <div
      class="bg-default peer-data-[variant=inset]:m-4 flex min-h-0 flex-1 flex-col overflow-hidden peer-data-[variant=inset]:rounded-xl peer-data-[variant=inset]:shadow-sm peer-data-[variant=inset]:ring peer-data-[variant=inset]:ring-default lg:peer-data-[variant=floating]:my-4 lg:peer-data-[variant=inset]:not-peer-data-[collapsible=offcanvas]:ms-0"
    >
      <slot />
    </div>
  </div>
</template>
