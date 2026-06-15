<template>
  <div class="ui-home" v-loading="loading">
    <div class="ui-home-top">
      <div class="page-header-bar">
        <div>
          <h1>测试看板</h1>
          <p class="greeting">{{ greeting }}，{{ user?.username || 'Admin' }}，欢迎回来！</p>
        </div>
        <el-button round @click="ElMessage.info('自定义看板功能建设中')">
          <el-icon><Setting /></el-icon> 自定义看板
        </el-button>
      </div>

      <div class="glass-stat-grid ui-stat-grid">
        <div class="glass-stat" v-for="(s, i) in stats" :key="s.key">
          <div class="stat-icon" :style="{ background: iconBg[i] }">
            <el-icon :size="18"><component :is="iconList[i]" /></el-icon>
          </div>
          <div class="stat-body">
            <div class="stat-label">{{ s.label }}</div>
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-trend">
              {{ s.trendLabel }}
              <span :class="s.trendUp ? 'up' : 'down'">{{ s.trendText }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="ui-home-body">
      <div class="ui-row middle-row">
        <div class="page-card list-card">
          <div class="card-head">
            <div class="section-title">最近执行记录</div>
            <a class="link-more" @click="router.push('/ui-test/records')">查看更多</a>
          </div>
          <div class="table-wrap">
            <el-table :data="recentExecutions" style="width: 100%" size="small">
              <el-table-column prop="taskId" label="任务 ID" width="108" show-overflow-tooltip />
              <el-table-column prop="name" label="用例/任务" min-width="120" show-overflow-tooltip />
              <el-table-column prop="env" label="环境" width="88" />
              <el-table-column prop="executor" label="执行人" width="72" />
              <el-table-column prop="status" label="状态" width="72">
                <template #default="{ row }">
                  <el-tag :type="row.status === '成功' ? 'success' : 'danger'" size="small" effect="light" round>
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="startTime" label="开始时间" width="150" />
              <el-table-column prop="duration" label="时长" width="72" />
              <el-table-column label="操作" width="56" fixed="right">
                <template #default="{ row }">
                  <el-button text size="small" @click="router.push('/ui-test/records')">
                    <el-icon><View /></el-icon>
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <div class="page-card chart-card">
          <div class="card-head">
            <div class="section-title">执行趋势（最近 30 天）</div>
            <a class="link-more" @click="router.push('/ui-test/reports')">查看更多</a>
          </div>
          <div class="chart-box"><BaseChart :option="trendOption" /></div>
        </div>
      </div>

      <div class="ui-row bottom-row">
        <div class="page-card quick-card">
          <div class="section-title">快速操作</div>
          <div class="ui-quick-grid">
            <div class="ui-quick-item" v-for="q in quickItems" :key="q.title" @click="onQuick(q)">
              <div class="ui-quick-icon" :style="{ background: q.bg }">
                <el-icon :size="18" :color="q.color"><component :is="q.icon" /></el-icon>
              </div>
              <div class="ui-quick-text">
                <div class="ui-quick-title" :title="q.title">{{ q.title }}</div>
                <div class="ui-quick-desc" :title="q.desc">{{ q.desc }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="page-card chart-card">
          <div class="card-head">
            <div class="section-title">用例分布</div>
          </div>
          <div class="chart-box distribution-chart"><BaseChart :option="distributionOption" /></div>
        </div>

        <div class="page-card fail-card">
          <div class="card-head">
            <div class="section-title">失败用例 TOP5</div>
          </div>
          <ul class="fail-list">
            <li v-for="(item, index) in failTop5" :key="item.name" class="fail-item">
              <span class="fail-rank" :class="{ top: index < 3 }">{{ index + 1 }}</span>
              <span class="fail-name">{{ item.name }}</span>
              <el-tag type="danger" size="small" effect="light" round>失败 {{ item.count }} 次</el-tag>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Setting, View, Folder, VideoPlay, Document, List,
  CircleCheck, DataLine, Warning, Timer, Cpu,
} from '@element-plus/icons-vue'
import BaseChart from '@/components/BaseChart.vue'
import { caseApi, uiExecutionApi } from '@/api'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.user)
const loading = ref(false)
const uiCases = ref([])

const iconList = [Folder, List, CircleCheck, Warning, Timer]
const iconBg = [
  'rgba(0,122,255,0.12)',
  'rgba(52,199,89,0.12)',
  'rgba(88,86,214,0.12)',
  'rgba(255,59,48,0.1)',
  'rgba(0,122,255,0.1)',
]

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '上午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const totalCases = computed(() => uiCases.value.length)
const failedCases = computed(() => uiCases.value.filter((c) => c.status === '失败').length)
const passedCases = computed(() => uiCases.value.filter((c) => c.status === '已通过').length)
const successRate = computed(() => {
  const total = uiCases.value.length
  if (!total) return '98.42'
  return ((passedCases.value / total) * 100).toFixed(2)
})

const stats = computed(() => [
  {
    key: 'cases',
    label: '用例总数',
    value: totalCases.value,
    trendLabel: '较上周',
    trendText: '+12',
    trendUp: true,
  },
  {
    key: 'runs',
    label: '执行总数',
    value: '1,268',
    trendLabel: '较上周',
    trendText: '+18.3%',
    trendUp: true,
  },
  {
    key: 'rate',
    label: '成功率',
    value: `${successRate.value}%`,
    trendLabel: '较上周',
    trendText: '+2.1%',
    trendUp: true,
  },
  {
    key: 'fail',
    label: '失败数',
    value: failedCases.value || 20,
    trendLabel: '较上周',
    trendText: '-5',
    trendUp: false,
  },
  {
    key: 'running',
    label: '执行中任务',
    value: 3,
    trendLabel: '较上周',
    trendText: '-2',
    trendUp: false,
  },
])

const recentExecutions = ref([])

const formatDuration = (seconds) => {
  if (!seconds) return '—'
  if (seconds < 60) return `${seconds}s`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return s ? `${m}m ${s}s` : `${m}m`
}

const formatRecordTime = (val) => {
  if (!val) return '—'
  const d = new Date(val)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

const loadRecentExecutions = async () => {
  try {
    const data = await uiExecutionApi.list({ page: 1, page_size: 5 })
    recentExecutions.value = (data.items || []).map((r) => ({
      taskId: r.task_id,
      name: r.name,
      env: r.env,
      executor: r.creator,
      status: r.status,
      startTime: formatRecordTime(r.start_time),
      duration: formatDuration(r.duration_seconds),
    }))
  } catch {
    recentExecutions.value = []
  }
}

const trendDates = Array.from({ length: 30 }, (_, i) => {
  const d = new Date()
  d.setDate(d.getDate() - (29 - i))
  return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
})

const chartAxis = { color: 'rgba(51,65,85,0.45)', lineStyle: { color: 'rgba(255,255,255,0.5)' } }
const chartSplit = { lineStyle: { color: 'rgba(255,255,255,0.45)' } }

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: {
    data: ['成功率', '失败率'],
    top: 0,
    icon: 'circle',
    textStyle: { color: '#64748b', fontSize: 11 },
  },
  grid: { left: 36, right: 16, top: 36, bottom: 24 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: trendDates,
    axisLine: chartAxis,
    axisLabel: { ...chartAxis, fontSize: 10, interval: 4 },
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: { formatter: '{value}%', ...chartAxis, fontSize: 10 },
    splitLine: chartSplit,
  },
  series: [
    {
      name: '成功率',
      type: 'line',
      smooth: true,
      data: trendDates.map((_, i) => 94 + Math.sin(i / 4) * 3 + (i % 5)),
      itemStyle: { color: '#007aff' },
      areaStyle: { color: 'rgba(0,122,255,0.08)' },
    },
    {
      name: '失败率',
      type: 'line',
      smooth: true,
      data: trendDates.map((_, i) => Math.max(1, 6 - Math.sin(i / 3) * 2 - (i % 3) * 0.3)),
      itemStyle: { color: '#ff3b30' },
      areaStyle: { color: 'rgba(255,59,48,0.06)' },
    },
  ],
}))

const moduleDistribution = computed(() => {
  const groups = {}
  uiCases.value.forEach((c) => {
    groups[c.module] = (groups[c.module] || 0) + 1
  })
  const entries = Object.entries(groups)
  if (!entries.length) {
    return [
      { name: '登录模块', value: 68 },
      { name: '支付模块', value: 32 },
      { name: '下单模块', value: 54 },
      { name: '商品模块', value: 92 },
      { name: '其他', value: 74 },
    ]
  }
  return entries.map(([name, value]) => ({ name, value }))
})

const distributionOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: {
    orient: 'vertical',
    right: 0,
    top: 'middle',
    icon: 'circle',
    textStyle: { color: '#64748b', fontSize: 10 },
    formatter: (name) => {
      const item = moduleDistribution.value.find((d) => d.name === name)
      const total = moduleDistribution.value.reduce((s, d) => s + d.value, 0)
      const pct = item ? ((item.value / total) * 100).toFixed(1) : 0
      return `${name}  ${item?.value || 0}  ${pct}%`
    },
  },
  series: [{
    type: 'pie',
    radius: ['46%', '66%'],
    center: ['32%', '50%'],
    label: {
      show: true,
      position: 'center',
      formatter: `{a|${totalCases.value}}\n{b|总用例}`,
      rich: {
        a: { fontSize: 22, fontWeight: 'bold', color: '#1d1d1f', lineHeight: 28 },
        b: { fontSize: 11, color: '#64748b', lineHeight: 18 },
      },
    },
    labelLine: { show: false },
    data: moduleDistribution.value,
    color: ['#007aff', '#5856d6', '#34c759', '#ff9500', '#94a3b8'],
  }],
}))

const failTop5 = computed(() => {
  const failed = uiCases.value.filter((c) => c.status === '失败')
  if (!failed.length) {
    return [
      { name: '下单-提交订单', count: 5 },
      { name: '登录-手机号登录', count: 4 },
      { name: '支付-余额支付', count: 3 },
      { name: '购物车结算流程', count: 2 },
      { name: '商品详情页展示', count: 2 },
    ]
  }
  return failed.slice(0, 5).map((c, i) => ({ name: c.name, count: 5 - i }))
})

const quickItems = [
  { title: '用例管理', desc: '维护 UI 自动化用例', icon: Folder, color: '#007aff', bg: 'rgba(0,122,255,0.1)', to: '/ui-test/cases' },
  { title: '测试执行', desc: '运行选中用例', icon: VideoPlay, color: '#34c759', bg: 'rgba(52,199,89,0.1)', to: '/ui-test/run' },
  { title: '执行记录', desc: '查看历史执行', icon: DataLine, color: '#5856d6', bg: 'rgba(88,86,214,0.1)', to: '/ui-test/records' },
  { title: '测试报告', desc: '生成与下载报告', icon: Document, color: '#ff9500', bg: 'rgba(255,149,0,0.1)', to: '/ui-test/reports' },
  { title: '环境配置', desc: '管理测试环境', icon: Setting, color: '#007aff', bg: 'rgba(0,122,255,0.08)', to: '/environments' },
  { title: '执行机管理', desc: '节点与浏览器池', icon: Cpu, color: '#5856d6', bg: 'rgba(88,86,214,0.08)', to: '/system' },
]

const onQuick = (q) => {
  if (q.to) router.push(q.to)
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([caseApi.uiCases().then((data) => { uiCases.value = data }), loadRecentExecutions()])
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.ui-home {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  gap: clamp(10px, 1.2vh, 14px);
  overflow: hidden;
  box-sizing: border-box;
}

.ui-home-top {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.2vh, 12px);
}

.page-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 4px 2px 0;

  h1 {
    margin: 0;
    font-size: clamp(18px, 1.6vw, 22px);
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-main);
  }

  .greeting {
    margin: 6px 0 0;
    font-size: 13px;
    color: var(--text-secondary);
  }
}

.ui-stat-grid {
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: clamp(8px, 0.8vw, 12px);

  .glass-stat {
    padding: clamp(10px, 1.2vh, 14px);
    min-width: 0;

    .stat-icon {
      width: clamp(36px, 3.5vw, 42px);
      height: clamp(36px, 3.5vw, 42px);
      border-radius: 11px;
    }

    .stat-label {
      font-size: 11px;
    }

    .stat-value {
      font-size: clamp(16px, 1.5vw, 20px);
    }

    .stat-trend {
      font-size: 10px;

      .up { color: #34c759; }
      .down { color: #ff3b30; }
    }
  }
}

.ui-home-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.2vh, 14px);
}

.ui-row {
  flex: 1;
  min-height: 0;
  display: grid;
  gap: clamp(10px, 1.2vh, 14px);
}

.middle-row {
  grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr);
}

.bottom-row {
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.95fr) minmax(0, 0.85fr);
  min-height: 240px;
}

.chart-card,
.list-card,
.quick-card,
.fail-card {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 12px 14px;
  overflow: hidden;
}

.quick-card {
  min-height: 240px;

  .section-title {
    flex-shrink: 0;
    margin-bottom: 8px;
  }
}

.card-head {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.link-more {
  font-size: 12px;
  color: var(--brand-primary);
  cursor: pointer;
  text-decoration: none;

  &:hover {
    opacity: 0.75;
  }
}

.table-wrap {
  flex: 1;
  min-height: 0;
  overflow: hidden;

  :deep(.el-table) {
    --el-table-bg-color: transparent;
    --el-table-tr-bg-color: transparent;
    --el-table-header-bg-color: rgba(255, 255, 255, 0.35);
    font-size: 12px;
  }
}

.chart-box {
  flex: 1;
  min-height: 0;
  position: relative;
}

.distribution-chart {
  :deep(.base-chart) {
    min-height: 180px;
  }
}

.ui-quick-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-auto-rows: minmax(92px, auto);
  gap: 10px;
  align-content: start;
  overflow-y: auto;
  padding-right: 2px;
}

.ui-quick-item {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 8px;
  min-height: 92px;
  height: auto;
  overflow: visible;
  border-radius: var(--glass-radius-sm);
  background: rgba(255, 255, 255, 0.42);
  border: 1px solid rgba(255, 255, 255, 0.65);
  cursor: pointer;
  text-align: center;
  transition: background 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.62);
    box-shadow: 0 6px 18px rgba(0, 122, 255, 0.08);
    transform: translateY(-1px);
  }
}

.ui-quick-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ui-quick-text {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  padding: 0 2px;
}

.ui-quick-title {
  font-size: clamp(12px, 1vw, 13px);
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.35;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ui-quick-desc {
  margin-top: 4px;
  font-size: clamp(10px, 0.9vw, 11px);
  color: var(--text-secondary);
  line-height: 1.35;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fail-list {
  list-style: none;
  margin: 0;
  padding: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

.fail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--glass-radius-sm);
  background: rgba(255, 255, 255, 0.38);
  border: 1px solid rgba(255, 255, 255, 0.55);
}

.fail-rank {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.55);
  flex-shrink: 0;

  &.top {
    color: #fff;
    background: linear-gradient(135deg, #007aff, #5856d6);
  }
}

.fail-name {
  flex: 1;
  font-size: 12px;
  color: var(--text-main);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 1280px) {
  .ui-stat-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .middle-row,
  .bottom-row {
    grid-template-columns: 1fr;
  }

  .bottom-row {
    min-height: auto;
  }

  .quick-card {
    min-height: 320px;
  }

  .ui-quick-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    grid-auto-rows: minmax(88px, auto);
  }

  .ui-home {
    overflow-y: auto;
  }
}

@media (max-width: 768px) {
  .ui-quick-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
