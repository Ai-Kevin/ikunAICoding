<template>
  <div class="page-shell empty-state">
    <div class="empty-icon">
      <el-icon :size="44"><component :is="icon" /></el-icon>
    </div>
    <h2>{{ title }}</h2>
    <p>该模块正在建设中，敬请期待。</p>
    <el-button type="primary" round @click="$router.push('/dashboard')">返回首页</el-button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title || '功能模块')
const icon = computed(() => route.meta.icon || 'Box')
</script>
