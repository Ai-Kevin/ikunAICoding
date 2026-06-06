<template>
  <div class="dashboard" v-loading="loading">
    <!-- Welcome -->
    <div class="welcome">
      <div>
        <h1>欢迎回来，{{ user?.username || 'Admin' }} 👋</h1>
        <p>今天是 {{ today }}，祝您工作顺利！</p>
      </div>
      <div class="welcome-actions">
        <el-button :icon="RefreshRight" @click="router.push('/executions')">最近执行</el-button>
        <el-button type="primary" :icon="Plus" @click="openPlanDialog">新建测试计划</el-button>
      </div>
    </div>

    <!-- Stat cards -->
    <div class="stat-grid">
      <div class="stat-card" v-for="(s, i) in stats" :key="s.key">
        <div class="stat-icon" :style="{ background: iconBg[i % iconBg.length] }">
          <el-icon :size="22"><component :is="iconList[i % iconList.length]" /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-trend">
            {{ s.trend_label }}
            <span :class="s.trend >= 0 ? 'up' : 'down'">
              {{ s.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(s.trend) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Row 1: trend + module + fail -->
    <div class="row row-3">
      <div class="page-card chart-card">
        <div class="card-head">
          <div class="section-title">📈 最近 7 天执行趋势</div>
          <el-radio-group v-model="trendRange" size="small">
            <el-radio-button label="近 7 天" />
          </el-radio-group>
        </div>
        <BaseChart :option="trendOption" style="height: 260px" />
      </div>

      <div class="page-card chart-card">
        <div class="card-head">
          <div class="section-title">📊 各模块通过率</div>
          <a class="more" @click="router.push('/projects')">更多 ></a>
        </div>
        <BaseChart :option="moduleOption" style="height: 260px" />
      </div>

      <div class="page-card chart-card">
        <div class="card-head">
          <div class="section-title">🍩 失败原因分布</div>
          <a class="more" @click="router.push('/reports')">更多 ></a>
        </div>
        <BaseChart :option="failOption" style="height: 260px" />
      </div>
    </div>

    <!-- Row 2: executions + perf + quick -->
    <div class="row row-bottom">
      <div class="page-card list-card">
        <div class="card-head">
          <div class="section-title">📋 最近执行记录</div>
          <a class="more" @click="router.push('/executions')">更多 ></a>
        </div>
        <el-table :data="recentExecutions" style="width: 100%" size="small">
          <el-table-column prop="exec_id" label="执行ID" width="130">
            <template #default="{ row }">
              <a class="exec-link" @click="router.push('/executions')">{{ row.exec_id }}</a>
            </template>
          </el-table-column>
          <el-table-column prop="plan_name" label="计划名称" />
          <el-table-column prop="type" label="类型" width="80" />
          <el-table-column prop="env" label="环境" width="90" />
          <el-table-column prop="start_time" label="开始时间" width="110" />
          <el-table-column prop="status" label="状态" width="70">
            <template #default="{ row }">
              <el-tag
                :type="row.status === '成功' ? 'success' : 'danger'"
                size="small"
                effect="light"
              >
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="success_rate" label="成功率" width="80">
            <template #default="{ row }">{{ row.success_rate }}%</template>
          </el-table-column>
        </el-table>
      </div>

      <div class="page-card chart-card">
        <div class="card-head">
          <div class="section-title">📉 性能响应时间趋势</div>
          <a class="more" @click="router.push('/performance')">更多 ></a>
        </div>
        <BaseChart :option="perfOption" style="height: 240px" />
      </div>

      <div class="page-card quick-card">
        <div class="section-title">⚡ 快捷入口</div>
        <div class="quick-grid">
          <div class="quick-item" v-for="q in quickItems" :key="q.title" @click="onQuick(q)">
            <el-icon :size="22" :color="q.color"><component :is="q.icon" /></el-icon>
            <span>{{ q.title }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- New test plan dialog -->
    <el-dialog v-model="planDialog" title="新建测试计划" width="500px">
      <el-form :model="planForm" label-width="90px">
        <el-form-item label="计划名称"><el-input v-model="planForm.name" placeholder="如：每日回归测试" /></el-form-item>
        <el-form-item label="计划类型">
          <el-select v-model="planForm.type" style="width: 100%">
            <el-option label="API / UI" value="API / UI" />
            <el-option label="API" value="API" />
            <el-option label="UI" value="UI" />
            <el-option label="性能" value="性能" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行环境">
          <el-select v-model="planForm.env" style="width: 100%">
            <el-option label="测试环境" value="测试环境" />
            <el-option label="预发环境" value="预发环境" />
            <el-option label="生产环境" value="生产环境" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划描述"><el-input v-model="planForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialog = false">取消</el-button>
        <el-button type="primary" :loading="savingPlan" @click="createPlan">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus,
  RefreshRight,
  Connection,
  Monitor,
  Files,
  VideoCamera,
  CircleCheck,
  EditPen,
  Document,
  Setting,
  Box,
  Calendar,
} from '@element-plus/icons-vue'
import BaseChart from '@/components/BaseChart.vue'
import { dashboardApi, planApi } from '@/api'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.user)
const loading = ref(false)
const trendRange = ref('近 7 天')

const stats = ref([])
const execTrend = ref([])
const modulePassRate = ref([])
const failReasons = ref([])
const perfTrend = ref([])
const recentExecutions = ref([])

const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  weekday: 'long',
})

const iconList = [Connection, Monitor, Files, VideoCamera, CircleCheck, EditPen]
const iconBg = [
  '#eaf0ff',
  '#e7f8ee',
  '#f2ecff',
  '#fff3e6',
  '#e6f7f6',
  '#ffeaea',
]

const quickItems = [
  { title: '新建 API 用例', icon: Connection, color: '#2f6bff', to: '/api-test' },
  { title: '新建 UI 用例', icon: Monitor, color: '#18b566', to: '/ui-test' },
  { title: '新建性能任务', icon: Setting, color: '#8a5cff', to: '/performance' },
  { title: '创建测试计划', icon: Calendar, color: '#ff9f1c', action: 'plan' },
  { title: '查看测试报告', icon: Document, color: '#13b5b1', to: '/reports' },
  { title: '配置环境', icon: Box, color: '#5d6cff', to: '/environments' },
]

const onQuick = (q) => {
  if (q.action === 'plan') openPlanDialog()
  else if (q.to) router.push(q.to)
}

// ---- test plan dialog ----
const planDialog = ref(false)
const savingPlan = ref(false)
const planForm = reactive({
  name: '', type: 'API / UI', env: '测试环境', description: '',
})
const openPlanDialog = () => {
  Object.assign(planForm, { name: '', type: 'API / UI', env: '测试环境', description: '' })
  planDialog.value = true
}
const createPlan = async () => {
  if (!planForm.name.trim()) {
    ElMessage.warning('请输入计划名称')
    return
  }
  savingPlan.value = true
  try {
    await planApi.create({ ...planForm, status: '待执行' })
    ElMessage.success('测试计划已创建')
    planDialog.value = false
    router.push('/plans')
  } finally {
    savingPlan.value = false
  }
}

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['通过', '失败', '跳过'], top: 0, icon: 'circle' },
  grid: { left: 30, right: 16, top: 40, bottom: 24 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: execTrend.value.map((d) => d.date),
    axisLine: { lineStyle: { color: '#e6e9f0' } },
    axisLabel: { color: '#8a91a3' },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#f0f2f7' } },
    axisLabel: { color: '#8a91a3' },
  },
  series: [
    {
      name: '通过',
      type: 'line',
      smooth: true,
      data: execTrend.value.map((d) => d.passed),
      itemStyle: { color: '#18b566' },
      areaStyle: { color: 'rgba(24,181,102,0.12)' },
    },
    {
      name: '失败',
      type: 'line',
      smooth: true,
      data: execTrend.value.map((d) => d.failed),
      itemStyle: { color: '#f0494b' },
    },
    {
      name: '跳过',
      type: 'line',
      smooth: true,
      data: execTrend.value.map((d) => d.skipped),
      itemStyle: { color: '#2f6bff' },
    },
  ],
}))

const moduleOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 70, right: 40, top: 10, bottom: 20 },
  xAxis: {
    type: 'value',
    max: 100,
    axisLabel: { formatter: '{value}%', color: '#8a91a3' },
    splitLine: { lineStyle: { color: '#f0f2f7' } },
  },
  yAxis: {
    type: 'category',
    inverse: true,
    data: modulePassRate.value.map((d) => d.name),
    axisLabel: { color: '#4a5163' },
    axisLine: { show: false },
    axisTick: { show: false },
  },
  series: [
    {
      type: 'bar',
      barWidth: 12,
      data: modulePassRate.value.map((d) => d.rate),
      label: { show: true, position: 'right', formatter: '{c}%', color: '#4a5163' },
      itemStyle: {
        borderRadius: 6,
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#4f8bff' },
            { offset: 1, color: '#18b566' },
          ],
        },
      },
    },
  ],
}))

const failOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', right: 0, top: 'center', icon: 'circle' },
  series: [
    {
      type: 'pie',
      radius: ['52%', '74%'],
      center: ['36%', '50%'],
      avoidLabelOverlap: false,
      label: { show: true, position: 'center', formatter: '总计\n{c|57}', rich: { c: { fontSize: 22, fontWeight: 'bold', color: '#1f2533' } } },
      labelLine: { show: false },
      data: failReasons.value.map((d) => ({ name: d.name, value: d.value })),
      color: ['#f0494b', '#ff9f1c', '#fcd34d', '#2f6bff', '#c5cbd8'],
    },
  ],
}))

const perfOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: {
    data: ['平均响应时间(ms)', 'P95 (ms)', 'P99 (ms)'],
    top: 0,
    icon: 'circle',
  },
  grid: { left: 40, right: 16, top: 40, bottom: 24 },
  xAxis: {
    type: 'category',
    data: perfTrend.value.map((d) => d.date),
    axisLine: { lineStyle: { color: '#e6e9f0' } },
    axisLabel: { color: '#8a91a3' },
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#f0f2f7' } },
    axisLabel: { color: '#8a91a3' },
  },
  series: [
    { name: '平均响应时间(ms)', type: 'line', smooth: true, data: perfTrend.value.map((d) => d.avg), itemStyle: { color: '#2f6bff' } },
    { name: 'P95 (ms)', type: 'line', smooth: true, data: perfTrend.value.map((d) => d.p95), itemStyle: { color: '#18b566' } },
    { name: 'P99 (ms)', type: 'line', smooth: true, data: perfTrend.value.map((d) => d.p99), itemStyle: { color: '#ff9f1c' } },
  ],
}))

onMounted(async () => {
  loading.value = true
  try {
    const data = await dashboardApi.overview()
    stats.value = data.stats
    execTrend.value = data.exec_trend
    modulePassRate.value = data.module_pass_rate
    failReasons.value = data.fail_reasons
    perfTrend.value = data.perf_trend
    recentExecutions.value = data.recent_executions
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome {
  display: flex;
  justify-content: space-between;
  align-items: center;
  h1 {
    font-size: 22px;
    margin: 0 0 4px;
  }
  p {
    margin: 0;
    color: var(--text-secondary);
    font-size: 13px;
  }
  .welcome-actions {
    display: flex;
    gap: 12px;
  }
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
}

.stat-card {
  background: #fff;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
  .stat-icon {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--brand-primary);
    flex-shrink: 0;
  }
  .stat-label {
    font-size: 12px;
    color: var(--text-secondary);
  }
  .stat-value {
    font-size: 22px;
    font-weight: 800;
    margin: 2px 0;
  }
  .stat-trend {
    font-size: 11px;
    color: var(--text-secondary);
    .up {
      color: var(--success);
    }
    .down {
      color: var(--danger);
    }
  }
}

.row {
  display: grid;
  gap: 16px;
}
.row-3 {
  grid-template-columns: repeat(3, 1fr);
}
.row-bottom {
  grid-template-columns: 1.3fr 1.3fr 0.9fr;
}

.chart-card,
.list-card,
.quick-card {
  padding: 16px 18px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.more {
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
}

.exec-link {
  color: var(--brand-primary);
  cursor: pointer;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 14px;
  .quick-item {
    border: 1px solid var(--border-light);
    border-radius: 10px;
    height: 78px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-regular);
    cursor: pointer;
    transition: all 0.2s;
    &:hover {
      border-color: var(--brand-primary);
      background: #f7f9ff;
      transform: translateY(-2px);
    }
  }
}
</style>
