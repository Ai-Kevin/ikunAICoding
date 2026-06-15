<template>
  <div class="ui-reports-page page-shell" v-loading="loading">
    <el-breadcrumb separator="/" class="page-crumb">
      <el-breadcrumb-item :to="{ path: '/ui-test' }">UI 测试</el-breadcrumb-item>
      <el-breadcrumb-item>测试报告</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="page-header-bar">
      <div class="page-intro">
        <h1>测试报告</h1>
        <p>查看所有测试执行的报告总览，支持筛选和搜索。</p>
      </div>
      <el-button type="primary" round @click="exportReports">
        <el-icon><Download /></el-icon> 导出报告
      </el-button>
    </div>

    <div class="glass-stat-grid reports-stat-grid">
      <div class="glass-stat" v-for="(s, i) in statCards" :key="s.key">
        <div class="stat-icon" :style="{ background: statIconBg[i] }">
          <el-icon :size="18"><component :is="statIcons[i]" /></el-icon>
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

    <div class="reports-panel glass-inner">
      <div class="toolbar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索执行记录 ID"
          :prefix-icon="Search"
          clearable
          class="toolbar-search"
          @keyup.enter="onSearch"
        />
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          class="toolbar-date"
          @change="onSearch"
        />
        <el-select v-model="filters.status" placeholder="执行状态" clearable class="toolbar-filter" @change="onSearch">
          <el-option label="成功" value="成功" />
          <el-option label="失败" value="失败" />
        </el-select>
        <el-select v-model="filters.env" placeholder="测试环境" clearable class="toolbar-filter" @change="onSearch">
          <el-option v-for="e in envOptions" :key="e" :label="e" :value="e" />
        </el-select>
        <el-select v-model="filters.machine" placeholder="执行方式" clearable class="toolbar-filter" @change="onSearch">
          <el-option v-for="m in machineOptions" :key="m" :label="m" :value="m" />
        </el-select>
        <el-select v-model="filters.creator" placeholder="创建人" clearable class="toolbar-filter" @change="onSearch">
          <el-option v-for="c in creatorOptions" :key="c" :label="c" :value="c" />
        </el-select>
        <el-button round @click="resetFilters">
          <el-icon><RefreshRight /></el-icon> 重置
        </el-button>
      </div>

      <div class="table-wrap">
        <el-table :data="rows" class="reports-table" style="width: 100%">
          <el-table-column label="执行记录 ID" min-width="148" align="center" header-align="center" show-overflow-tooltip>
            <template #default="{ row }">
              <a class="task-link" @click="openReport(row)">{{ row.task_id }}</a>
            </template>
          </el-table-column>
          <el-table-column prop="env" label="测试环境" min-width="96" align="center" header-align="center" />
          <el-table-column prop="machine" label="执行方式" min-width="120" align="center" header-align="center" show-overflow-tooltip />
          <el-table-column prop="total_cases" label="用例总数" width="88" align="center" header-align="center" />
          <el-table-column label="成功" width="72" align="center" header-align="center">
            <template #default="{ row }">
              <span class="num-success">{{ row.success_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="失败" width="72" align="center" header-align="center">
            <template #default="{ row }">
              <span class="num-fail">{{ row.fail_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="跳过" width="72" align="center" header-align="center">
            <template #default="{ row }">
              <span class="num-skip">{{ row.skip_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="成功率" width="88" align="center" header-align="center">
            <template #default="{ row }">
              <span :class="rateClass(row.success_rate)">{{ row.success_rate }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="执行时长" min-width="100" align="center" header-align="center">
            <template #default="{ row }">{{ formatDuration(row.duration_seconds) }}</template>
          </el-table-column>
          <el-table-column prop="creator" label="创建人" min-width="88" align="center" header-align="center" />
          <el-table-column label="开始时间" min-width="148" align="center" header-align="center">
            <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="148" align="center" header-align="center" fixed="right">
            <template #default="{ row }">
              <div class="row-actions">
                <button type="button" class="glass-inline-btn primary" @click="openReport(row)">查看报告</button>
                <button type="button" class="glass-inline-btn icon-only primary" title="统计图表" @click="openChart(row)">
                  <el-icon :size="14"><Histogram /></el-icon>
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="table-foot">
        <span class="total-text">共 {{ total }} 条</span>
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="prev, pager, next, sizes, jumper"
          background
          @current-change="loadReports"
          @size-change="onPageSizeChange"
        />
      </div>
    </div>

    <el-dialog
      v-model="reportVisible"
      :title="`测试报告 · ${currentRow?.task_id || ''}`"
      width="560px"
      top="8vh"
      class="report-glass-dialog"
      destroy-on-close
      append-to-body
    >
      <template v-if="currentRow">
        <div class="report-capture">
        <div class="report-meta">
          <div><span>任务名称</span><span class="meta-value">{{ currentRow.name }}</span></div>
          <div><span>测试环境</span><span class="meta-value">{{ currentRow.env }}</span></div>
          <div><span>执行方式</span><span class="meta-value">{{ currentRow.machine }}</span></div>
          <div><span>创建人</span><span class="meta-value">{{ currentRow.creator }}</span></div>
          <div><span>开始时间</span><span class="meta-value">{{ formatTime(currentRow.start_time) }}</span></div>
          <div><span>结束时间</span><span class="meta-value">{{ formatTime(currentRow.end_time) }}</span></div>
          <div><span>执行时长</span><span class="meta-value">{{ formatDuration(currentRow.duration_seconds) }}</span></div>
          <div><span>执行状态</span>
            <span class="meta-value">
            <el-tag :type="currentRow.status === '成功' ? 'success' : 'danger'" size="small" effect="light" round>
              {{ currentRow.status }}
            </el-tag>
            </span>
          </div>
        </div>

        <div class="report-chart glass-inner">
          <BaseChart ref="reportChartRef" :option="reportChartOption" />
        </div>

        <div class="report-stats">
          <div class="stat-chip">总数 {{ currentRow.total_cases }}</div>
          <div class="stat-chip success">成功 {{ currentRow.success_count }}</div>
          <div class="stat-chip fail">失败 {{ currentRow.fail_count }}</div>
          <div class="stat-chip skip">跳过 {{ currentRow.skip_count }}</div>
          <div class="stat-chip">成功率 {{ currentRow.success_rate }}%</div>
        </div>

        <div class="report-section-title">执行摘要</div>
        <pre class="run-logs">{{ reportSummary }}</pre>
        </div>
      </template>

      <template #footer>
        <div class="report-dialog-foot">
          <el-button round @click="reportVisible = false">关闭</el-button>
          <el-button type="primary" round :disabled="!currentRow" :loading="downloadingImage" @click="downloadReportImage">
            <el-icon><Download /></el-icon> 下载报告
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import html2canvas from 'html2canvas'
import {
  Search, RefreshRight, Download, Histogram,
  Folder, CircleCheck, CircleClose, PieChart, Timer,
} from '@element-plus/icons-vue'
import BaseChart from '@/components/BaseChart.vue'
import { uiExecutionApi } from '@/api'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const statCards = ref([])
const reportVisible = ref(false)
const currentRow = ref(null)
const reportChartRef = ref(null)
const downloadingImage = ref(false)

const statIcons = [Folder, CircleCheck, CircleClose, PieChart, Timer]
const statIconBg = [
  'rgba(0,122,255,0.12)',
  'rgba(52,199,89,0.12)',
  'rgba(255,59,48,0.1)',
  'rgba(88,86,214,0.12)',
  'rgba(255,149,0,0.12)',
]

const envOptions = ['测试环境', '预发环境', '生产环境']
const machineOptions = ['Docker 执行机-01', 'Docker 执行机-02', '本地执行']
const creatorOptions = ['admin', 'test01', '张三', '李四', '王五', '赵六']

const filters = reactive({
  keyword: '',
  dateRange: null,
  status: '',
  env: '',
  machine: '',
  creator: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
})

const formatTime = (val) => {
  if (!val) return '—'
  const d = new Date(val)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

const formatDuration = (seconds) => {
  if (!seconds) return '0秒'
  if (seconds < 60) return `${seconds}秒`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return s ? `${m}分${s}秒` : `${m}分`
}

const rateClass = (rate) => {
  if (rate >= 100) return 'rate-full'
  if (rate >= 80) return 'rate-good'
  return 'rate-bad'
}

const reportSummary = computed(() => {
  const row = currentRow.value
  if (!row) return ''
  const lines = [
    `[报告] 执行记录 ${row.task_id}`,
    `[环境] ${row.env} · ${row.machine}`,
    `[结果] 成功 ${row.success_count} · 失败 ${row.fail_count} · 跳过 ${row.skip_count}`,
    `[成功率] ${row.success_rate}% · 耗时 ${formatDuration(row.duration_seconds)}`,
    '',
    row.logs || '暂无详细日志',
  ]
  return lines.join('\n')
})

const reportChartOption = computed(() => {
  const row = currentRow.value
  if (!row) return {}
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, icon: 'circle', textStyle: { color: '#64748b', fontSize: 11 } },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '45%'],
      label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
      data: [
        { name: '成功', value: row.success_count, itemStyle: { color: '#34c759' } },
        { name: '失败', value: row.fail_count, itemStyle: { color: '#ff3b30' } },
        { name: '跳过', value: row.skip_count, itemStyle: { color: '#94a3b8' } },
      ].filter((d) => d.value > 0),
    }],
  }
})

const buildParams = () => {
  const params = {
    page: pagination.page,
    page_size: pagination.pageSize,
  }
  if (filters.keyword) params.keyword = filters.keyword.trim()
  if (filters.status) params.status = filters.status
  if (filters.env) params.env = filters.env
  if (filters.machine) params.machine = filters.machine
  if (filters.creator) params.creator = filters.creator
  if (filters.dateRange?.length === 2) {
    params.start_date = filters.dateRange[0]
    params.end_date = filters.dateRange[1]
  }
  return params
}

const loadStats = async () => {
  const data = await uiExecutionApi.stats()
  statCards.value = data.stats || []
}

const loadReports = async () => {
  loading.value = true
  try {
    const data = await uiExecutionApi.list(buildParams())
    rows.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

const loadAll = async () => {
  loading.value = true
  try {
    await Promise.all([loadStats(), loadReports()])
  } finally {
    loading.value = false
  }
}

const onSearch = () => {
  pagination.page = 1
  loadReports()
}

const onPageSizeChange = () => {
  pagination.page = 1
  loadReports()
}

const resetFilters = () => {
  Object.assign(filters, {
    keyword: '',
    dateRange: null,
    status: '',
    env: '',
    machine: '',
    creator: '',
  })
  pagination.page = 1
  loadAll()
}

const openReport = async (row) => {
  try {
    currentRow.value = await uiExecutionApi.detail(row.id)
    reportVisible.value = true
  } catch {
    ElMessage.error('加载报告失败')
  }
}

const openChart = (row) => openReport(row)

const downloadReportImage = async () => {
  const row = currentRow.value
  if (!row) return

  downloadingImage.value = true
  try {
    await nextTick()
    await new Promise((resolve) => setTimeout(resolve, 320))

    const dialogEl = document.querySelector('.report-glass-dialog')
    if (!dialogEl) throw new Error('报告内容未就绪')

    const scale = Math.min(2, window.devicePixelRatio || 2)
    const canvas = await html2canvas(dialogEl, {
      scale,
      backgroundColor: '#ffffff',
      useCORS: true,
      logging: false,
      ignoreElements: (el) =>
        el.classList?.contains('el-dialog__footer')
        || el.classList?.contains('el-dialog__headerbtn'),
      onclone: (doc) => {
        const dialog = doc.querySelector('.report-glass-dialog')
        dialog?.classList.add('report-export-mode')

        const root = doc.querySelector('.report-capture')
        if (!root) return
        root.classList.add('report-capture-export')
        const logs = root.querySelector('.run-logs')
        if (logs) {
          logs.style.maxHeight = 'none'
          logs.style.overflow = 'visible'
        }
      },
    })

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'))
    if (!blob) throw new Error('生成图片失败')
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${row.task_id}-report.png`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('报告图片已下载')
  } catch {
    ElMessage.error('生成报告图片失败')
  } finally {
    downloadingImage.value = false
  }
}

const exportReports = () => {
  if (!rows.value.length) {
    ElMessage.warning('当前页暂无数据可导出')
    return
  }
  const header = ['执行记录ID', '测试环境', '执行方式', '用例总数', '成功', '失败', '跳过', '成功率', '执行时长', '创建人', '开始时间', '状态']
  const lines = rows.value.map((r) => [
    r.task_id,
    r.env,
    r.machine,
    r.total_cases,
    r.success_count,
    r.fail_count,
    r.skip_count,
    `${r.success_rate}%`,
    formatDuration(r.duration_seconds),
    r.creator,
    formatTime(r.start_time),
    r.status,
  ].join(','))
  const csv = `\uFEFF${header.join(',')}\n${lines.join('\n')}`
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ui-test-reports-${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

onMounted(loadAll)
</script>

<style scoped lang="scss">
.ui-reports-page {
  gap: 16px;
}

.page-header-bar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.page-intro {
  h1 {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-main);
  }

  p {
    margin: 8px 0 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
  }
}

.reports-stat-grid {
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;

  .glass-stat {
    padding: 14px 16px;

    .stat-trend {
      font-size: 10px;

      .up { color: #34c759; }
      .down { color: #ff3b30; }
    }
  }
}

.reports-panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 16px 0 12px;
  overflow: hidden;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 0 18px 14px;
}

.toolbar-search { width: 200px; }
.toolbar-date { width: 260px; }
.toolbar-filter { width: 120px; }

.table-wrap {
  flex: 1;
  min-height: 0;
  padding: 0 18px;
  overflow: auto;

  :deep(.el-table) {
    --el-table-bg-color: transparent;
    --el-table-tr-bg-color: transparent;
    --el-table-header-bg-color: rgba(255, 255, 255, 0.38);
    font-size: 13px;
  }
}

.reports-table {
  :deep(.el-table__header-wrapper table),
  :deep(.el-table__body-wrapper table) {
    width: 100% !important;
  }
}

.task-link {
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 500;

  &:hover { text-decoration: underline; }
}

.num-success { color: #34c759; font-weight: 600; }
.num-fail { color: #ff3b30; font-weight: 600; }
.num-skip { color: #94a3b8; font-weight: 500; }

.rate-full { color: #34c759; font-weight: 600; }
.rate-good { color: #007aff; font-weight: 600; }
.rate-bad { color: #ff9500; font-weight: 600; }

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
}

.glass-inline-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 24px;
  padding: 0 8px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(12px) saturate(170%);
  -webkit-backdrop-filter: blur(12px) saturate(170%);
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.92);
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;

  &.primary {
    color: #007aff;

    &:hover {
      background: rgba(0, 122, 255, 0.14);
      border-color: rgba(0, 122, 255, 0.38);
      color: #0066d6;
    }
  }

  &.icon-only {
    width: 24px;
    padding: 0;
  }

  &:active { transform: scale(0.97); }
}

.table-foot {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 18px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.45);
  margin-top: 8px;
}

.total-text {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.report-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 16px;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--text-main);

  > div {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    min-width: 0;
    line-height: 1.5;
  }

  span {
    flex-shrink: 0;
    width: 64px;
    color: var(--text-secondary);
  }

  .meta-value {
    flex: 1;
    min-width: 0;
    word-break: break-word;
  }
}

.report-capture-export .run-logs {
  max-height: none !important;
  overflow: visible !important;
}

.report-chart {
  height: 220px;
  margin-bottom: 16px;
  padding: 12px;
}

.report-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.stat-chip {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.45);
  color: var(--text-main);

  &.success { color: #248a3d; background: rgba(52, 199, 89, 0.14); }
  &.fail { color: #d70015; background: rgba(255, 59, 48, 0.1); }
  &.skip { color: #64748b; background: rgba(148, 163, 184, 0.16); }
}

.report-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 10px;
}

.report-dialog-foot {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  width: 100%;
}

.run-logs {
  padding: 12px;
  border-radius: var(--glass-radius-sm);
  background: rgba(15, 23, 42, 0.88);
  color: rgba(255, 255, 255, 0.82);
  font-family: 'SF Mono', Consolas, monospace;
  font-size: 12px;
  line-height: 1.7;
  max-height: 200px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 1400px) {
  .reports-stat-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 960px) {
  .reports-stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .page-header-bar { flex-direction: column; }
}
</style>

<style lang="scss">
.report-glass-dialog {
  .el-dialog__body {
    padding: 16px 24px 8px;
    max-height: calc(84vh - 140px);
    overflow-y: auto;
  }

  .el-dialog__footer {
    border-top: 1px solid rgba(255, 255, 255, 0.45);
    padding-top: 14px;
  }
}

/* html2canvas 对半透明文字 / CSS 变量支持差，导出时强制实色 */
.report-glass-dialog.report-export-mode {
  background: #ffffff !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  box-shadow: none !important;

  .el-dialog__header {
    border-bottom-color: #e2e8f0 !important;
  }

  .el-dialog__title {
    color: #1d1d1f !important;
  }

  .el-dialog__body {
    color: #1d1d1f !important;
  }

  .report-meta {
    color: #1d1d1f !important;

    span {
      color: #64748b !important;
    }

    .meta-value {
      color: #1d1d1f !important;
    }
  }

  .report-section-title {
    color: #1d1d1f !important;
  }

  .report-chart {
    background: #f8fafc !important;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
  }

  .stat-chip {
    color: #1d1d1f !important;
    background: #f1f5f9 !important;

    &.success {
      color: #248a3d !important;
      background: #dcfce7 !important;
    }

    &.fail {
      color: #d70015 !important;
      background: #fee2e2 !important;
    }

    &.skip {
      color: #64748b !important;
      background: #f1f5f9 !important;
    }
  }

  .run-logs {
    color: #f8fafc !important;
    background: #1e293b !important;
  }
}
</style>
