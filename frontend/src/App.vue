<template>
  <div class="app-shell">
    <div class="ambient-bg" aria-hidden="true">
      <div class="orb orb-1" />
      <div class="orb orb-2" />
      <div class="orb orb-3" />
    </div>
    <div class="app-content">
      <router-view />
    </div>
  </div>
</template>

<style scoped>
.app-content {
  position: relative;
  z-index: 1;
  min-height: 100%;
}
</style>
