<template>
  <div class="placeholder page-card">
    <el-icon :size="56" color="#c5cbd8"><component :is="icon" /></el-icon>
    <h2>{{ title }}</h2>
    <p>该模块正在建设中，敬请期待。</p>
    <el-button type="primary" @click="$router.push('/dashboard')">返回首页</el-button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title || '功能模块')
const icon = computed(() => route.meta.icon || 'Box')
</script>

<style scoped>
.placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  color: var(--text-secondary);
}
.placeholder h2 {
  margin: 0;
  color: var(--text-main);
}
.placeholder p {
  margin: 0 0 10px;
}
</style>
