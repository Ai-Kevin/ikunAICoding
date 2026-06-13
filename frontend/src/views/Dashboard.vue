<template>
  <div class="dashboard" v-loading="loading">
    <!-- Top: welcome + stats (fixed proportion) -->
    <div class="dashboard-top">
      <div class="welcome-banner">
        <div>
          <h1>欢迎回来，{{ user?.username || 'Admin' }}</h1>
          <p>今天是 {{ today }}，祝您工作顺利！</p>
        </div>
        <div class="welcome-actions">
          <el-button round :icon="RefreshRight" @click="router.push('/executions')">最近执行</el-button>
          <el-button type="primary" round :icon="Plus" @click="openPlanDialog">新建测试计划</el-button>
        </div>
      </div>

      <div class="glass-stat-grid dashboard-stats">
        <div class="glass-stat" v-for="(s, i) in stats" :key="s.key">
          <div class="stat-icon" :style="{ background: iconBg[i % iconBg.length] }">
            <el-icon :size="18"><component :is="iconList[i % iconList.length]" /></el-icon>
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
    </div>

    <!-- Main: charts + bottom (fills remaining viewport) -->
    <div class="dashboard-body">
      <div class="dashboard-row charts-row">
        <div class="page-card chart-card">
          <div class="card-head">
            <div class="section-title">最近 7 天执行趋势</div>
            <el-radio-group v-model="trendRange" size="small">
              <el-radio-button label="近 7 天" />
            </el-radio-group>
          </div>
          <div class="chart-box"><BaseChart :option="trendOption" /></div>
        </div>
        <div class="page-card chart-card">
          <div class="card-head">
            <div class="section-title">各模块通过率</div>
            <a class="link-more" @click="router.push('/projects')">更多 ></a>
          </div>
          <div class="chart-box"><BaseChart :option="moduleOption" /></div>
        </div>
        <div class="page-card chart-card">
          <div class="card-head">
            <div class="section-title">失败原因分布</div>
            <a class="link-more" @click="router.push('/reports')">更多 ></a>
          </div>
          <div class="chart-box"><BaseChart :option="failOption" /></div>
        </div>
      </div>

      <div class="dashboard-row bottom-row">
        <div class="page-card list-card">
          <div class="card-head">
            <div class="section-title">最近执行记录</div>
            <a class="link-more" @click="router.push('/executions')">更多 ></a>
          </div>
          <div class="table-wrap">
            <el-table :data="recentExecutions" style="width: 100%" size="small">
              <el-table-column prop="exec_id" label="执行ID" width="120" show-overflow-tooltip>
                <template #default="{ row }">
                  <a class="link-primary" @click="router.push('/executions')">{{ row.exec_id }}</a>
                </template>
              </el-table-column>
              <el-table-column prop="plan_name" label="计划名称" min-width="100" show-overflow-tooltip />
              <el-table-column prop="type" label="类型" width="64" />
              <el-table-column prop="env" label="环境" width="80" show-overflow-tooltip />
              <el-table-column prop="start_time" label="开始时间" width="100" />
              <el-table-column prop="status" label="状态" width="64">
                <template #default="{ row }">
                  <el-tag :type="row.status === '成功' ? 'success' : 'danger'" size="small" effect="light">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="success_rate" label="成功率" width="72">
                <template #default="{ row }">{{ row.success_rate }}%</template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        <div class="page-card chart-card">
          <div class="card-head">
            <div class="section-title">性能响应时间趋势</div>
            <a class="link-more" @click="router.push('/performance')">更多 ></a>
          </div>
          <div class="chart-box"><BaseChart :option="perfOption" /></div>
        </div>
        <div class="page-card quick-card">
          <div class="section-title">快捷入口</div>
          <div class="quick-grid dashboard-quick">
            <div class="quick-item" v-for="q in quickItems" :key="q.title" @click="onQuick(q)">
              <el-icon :size="20" :color="q.color"><component :is="q.icon" /></el-icon>
              <span>{{ q.title }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

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
        <el-button round @click="planDialog = false">取消</el-button>
        <el-button type="primary" round :loading="savingPlan" @click="createPlan">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus, RefreshRight, Connection, Monitor, Files, VideoCamera,
  CircleCheck, EditPen, Document, Setting, Box, Calendar,
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
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
})

const iconList = [Connection, Monitor, Files, VideoCamera, CircleCheck, EditPen]
const iconBg = [
  'rgba(0,122,255,0.1)', 'rgba(52,199,89,0.1)', 'rgba(88,86,214,0.1)',
  'rgba(255,149,0,0.1)', 'rgba(0,122,255,0.08)', 'rgba(255,59,48,0.08)',
]

const quickItems = [
  { title: '新建 API 用例', icon: Connection, color: '#007aff', to: '/api-test' },
  { title: '新建 UI 用例', icon: Monitor, color: '#34c759', to: '/ui-test' },
  { title: '新建性能任务', icon: Setting, color: '#5856d6', to: '/performance' },
  { title: '创建测试计划', icon: Calendar, color: '#ff9500', action: 'plan' },
  { title: '查看测试报告', icon: Document, color: '#007aff', to: '/reports' },
  { title: '配置环境', icon: Box, color: '#5856d6', to: '/environments' },
]

const onQuick = (q) => {
  if (q.action === 'plan') openPlanDialog()
  else if (q.to) router.push(q.to)
}

const planDialog = ref(false)
const savingPlan = ref(false)
const planForm = reactive({ name: '', type: 'API / UI', env: '测试环境', description: '' })
const openPlanDialog = () => {
  Object.assign(planForm, { name: '', type: 'API / UI', env: '测试环境', description: '' })
  planDialog.value = true
}
const createPlan = async () => {
  if (!planForm.name.trim()) { ElMessage.warning('请输入计划名称'); return }
  savingPlan.value = true
  try {
    await planApi.create({ ...planForm, status: '待执行' })
    ElMessage.success('测试计划已创建')
    planDialog.value = false
    router.push('/plans')
  } finally { savingPlan.value = false }
}

const chartAxis = { color: 'rgba(51,65,85,0.45)', lineStyle: { color: 'rgba(255,255,255,0.5)' } }
const chartSplit = { lineStyle: { color: 'rgba(255,255,255,0.45)' } }

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['通过', '失败', '跳过'], top: 0, icon: 'circle', textStyle: { color: '#64748b', fontSize: 11 } },
  grid: { left: 30, right: 12, top: 36, bottom: 20 },
  xAxis: {
    type: 'category', boundaryGap: false,
    data: execTrend.value.map((d) => d.date),
    axisLine: chartAxis, axisLabel: { ...chartAxis, fontSize: 10 },
  },
  yAxis: { type: 'value', splitLine: chartSplit, axisLabel: { ...chartAxis, fontSize: 10 } },
  series: [
    { name: '通过', type: 'line', smooth: true, data: execTrend.value.map((d) => d.passed), itemStyle: { color: '#34c759' }, areaStyle: { color: 'rgba(52,199,89,0.1)' } },
    { name: '失败', type: 'line', smooth: true, data: execTrend.value.map((d) => d.failed), itemStyle: { color: '#ff3b30' } },
    { name: '跳过', type: 'line', smooth: true, data: execTrend.value.map((d) => d.skipped), itemStyle: { color: '#007aff' } },
  ],
}))

const moduleOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 64, right: 36, top: 8, bottom: 12 },
  xAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%', ...chartAxis, fontSize: 10 }, splitLine: chartSplit },
  yAxis: {
    type: 'category', inverse: true,
    data: modulePassRate.value.map((d) => d.name),
    axisLabel: { color: '#334155', fontSize: 10 }, axisLine: { show: false }, axisTick: { show: false },
  },
  series: [{
    type: 'bar', barWidth: 10,
    data: modulePassRate.value.map((d) => d.rate),
    label: { show: true, position: 'right', formatter: '{c}%', color: '#334155', fontSize: 10 },
    itemStyle: {
      borderRadius: 5,
      color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [
        { offset: 0, color: '#007aff' }, { offset: 1, color: '#34c759' },
      ]},
    },
  }],
}))

const failOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', right: 0, top: 'center', icon: 'circle', textStyle: { color: '#64748b', fontSize: 10 } },
  series: [{
    type: 'pie', radius: ['48%', '68%'], center: ['38%', '50%'],
    label: { show: true, position: 'center', formatter: '总计\n{c|57}', rich: { c: { fontSize: 18, fontWeight: 'bold', color: '#1d1d1f' } } },
    labelLine: { show: false },
    data: failReasons.value.map((d) => ({ name: d.name, value: d.value })),
    color: ['#ff3b30', '#ff9500', '#fbbf24', '#007aff', '#94a3b8'],
  }],
}))

const perfOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['平均响应时间(ms)', 'P95 (ms)', 'P99 (ms)'], top: 0, icon: 'circle', textStyle: { color: '#64748b', fontSize: 10 } },
  grid: { left: 36, right: 12, top: 36, bottom: 20 },
  xAxis: { type: 'category', data: perfTrend.value.map((d) => d.date), axisLine: chartAxis, axisLabel: { ...chartAxis, fontSize: 10 } },
  yAxis: { type: 'value', splitLine: chartSplit, axisLabel: { ...chartAxis, fontSize: 10 } },
  series: [
    { name: '平均响应时间(ms)', type: 'line', smooth: true, data: perfTrend.value.map((d) => d.avg), itemStyle: { color: '#007aff' } },
    { name: 'P95 (ms)', type: 'line', smooth: true, data: perfTrend.value.map((d) => d.p95), itemStyle: { color: '#34c759' } },
    { name: 'P99 (ms)', type: 'line', smooth: true, data: perfTrend.value.map((d) => d.p99), itemStyle: { color: '#ff9500' } },
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
  } finally { loading.value = false }
})
</script>

<style scoped lang="scss">
.dashboard {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  gap: clamp(10px, 1.2vh, 14px);
  overflow: hidden;
  box-sizing: border-box;
}

.dashboard-top {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.2vh, 12px);
}

.welcome-banner {
  padding: 14px 18px;

  h1 {
    font-size: clamp(16px, 1.4vw, 20px);
  }

  p {
    font-size: 12px;
  }
}

.dashboard-stats {
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: clamp(8px, 0.8vw, 12px);

  .glass-stat {
    padding: clamp(10px, 1.2vh, 14px);
    min-width: 0;

    .stat-icon {
      width: clamp(36px, 3.5vw, 42px);
      height: clamp(36px, 3.5vw, 42px);
      border-radius: 11px;
    }

    .stat-body {
      min-width: 0;
      overflow: hidden;
    }

    .stat-label {
      font-size: 11px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .stat-value {
      font-size: clamp(16px, 1.5vw, 20px);
    }

    .stat-trend {
      font-size: 10px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

.dashboard-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.2vh, 14px);
}

.dashboard-row {
  flex: 1;
  min-height: 0;
  display: grid;
  gap: clamp(10px, 1.2vh, 14px);
}

.charts-row {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.bottom-row {
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 1.15fr) minmax(0, 0.85fr);
}

.chart-card,
.list-card,
.quick-card {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 12px 14px;
  overflow: hidden;
}

.card-head {
  flex-shrink: 0;
  margin-bottom: 8px;
}

.chart-box {
  flex: 1;
  min-height: 0;
  position: relative;

  :deep(.base-chart) {
    min-height: 0;
    height: 100%;
  }
}

.table-wrap {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.quick-card {
  .section-title {
    flex-shrink: 0;
  }
}

.dashboard-quick {
  flex: 1;
  min-height: 0;
  margin-top: 8px;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: clamp(6px, 0.8vh, 10px);

  .quick-item {
    height: auto;
    min-height: 0;
    padding: 6px 4px;
    font-size: 11px;
    gap: 4px;

    .el-icon {
      font-size: 18px !important;
    }

    span {
      text-align: center;
      line-height: 1.25;
    }
  }
}

/* ── Responsive: medium screens ── */
@media (max-width: 1400px) {
  .dashboard-stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .bottom-row {
    grid-template-columns: 1fr 1fr;
  }

  .bottom-row .quick-card {
    grid-column: span 2;
  }

  .dashboard-quick {
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(2, 1fr);
  }
}

/* ── Small height: allow scroll instead of crush ── */
@media (max-height: 720px) {
  .dashboard {
    overflow-y: auto;
  }

  .dashboard-body {
    flex: none;
    min-height: 480px;
  }

  .chart-box :deep(.base-chart) {
    min-height: 140px;
  }
}

/* ── Narrow width ── */
@media (max-width: 900px) {
  .welcome-banner {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .charts-row,
  .bottom-row {
    grid-template-columns: 1fr;
  }

  .bottom-row .quick-card {
    grid-column: auto;
  }

  .dashboard-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
