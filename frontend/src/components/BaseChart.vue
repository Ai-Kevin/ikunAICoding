<template>
  <div ref="chartEl" class="base-chart"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  option: { type: Object, required: true },
})

const chartEl = ref()
let chart = null

const render = () => {
  if (!chart) return
  chart.setOption(props.option, true)
}

const resize = () => chart && chart.resize()

onMounted(async () => {
  await nextTick()
  chart = echarts.init(chartEl.value)
  render()
  window.addEventListener('resize', resize)
})

watch(() => props.option, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart && chart.dispose()
})
</script>

<style scoped>
.base-chart {
  width: 100%;
  height: 100%;
  min-height: 0;
}
</style>
