<template>
  <div class="ui-records-page page-shell" v-loading="loading">
    <el-breadcrumb separator="/" class="page-crumb">
      <el-breadcrumb-item :to="{ path: '/ui-test' }">UI 测试</el-breadcrumb-item>
      <el-breadcrumb-item>执行记录</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="page-intro">
      <h1>执行记录</h1>
      <p>查看所有测试执行记录，支持查看执行详情、日志和报告。</p>
    </div>

    <div class="glass-stat-grid records-stat-grid">
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

    <div class="records-panel glass-inner">
      <div class="toolbar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索任务ID、名称或创建人"
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
        <el-button round @click="exportRecords">
          <el-icon><Download /></el-icon> 导出记录
        </el-button>
      </div>

      <div class="table-wrap">
        <el-table :data="rows" style="width: 100%">
          <el-table-column label="任务ID" width="168" fixed="left">
            <template #default="{ row }">
              <a class="task-link" @click="openDetail(row)">{{ row.task_id }}</a>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="任务名称" min-width="140" show-overflow-tooltip />
          <el-table-column prop="env" label="测试环境" width="96" />
          <el-table-column prop="total_cases" label="用例总数" width="88" align="center" />
          <el-table-column label="成功" width="72" align="center">
            <template #default="{ row }">
              <span class="num-success">{{ row.success_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="失败" width="72" align="center">
            <template #default="{ row }">
              <span class="num-fail">{{ row.fail_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="跳过" width="72" align="center">
            <template #default="{ row }">
              <span class="num-skip">{{ row.skip_count }}</span>
            </template>
          </el-table-column>
          <el-table-column label="成功率" width="88" align="center">
            <template #default="{ row }">
              <span :class="rateClass(row.success_rate)">{{ row.success_rate }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="执行时长" width="96">
            <template #default="{ row }">{{ formatDuration(row.duration_seconds) }}</template>
          </el-table-column>
          <el-table-column prop="machine" label="执行方式" width="132" show-overflow-tooltip />
          <el-table-column prop="creator" label="创建人" width="88" />
          <el-table-column label="开始时间" width="168">
            <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="80" fixed="right">
            <template #default="{ row }">
              <el-tag
                :type="row.status === '成功' ? 'success' : 'danger'"
                size="small"
                effect="light"
                round
              >
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button text size="small" title="查看详情" @click="openDetail(row)">
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button text size="small" title="下载报告" @click="downloadReport(row)">
                  <el-icon><Download /></el-icon>
                </el-button>
                <el-button text size="small" title="删除" @click="removeRecord(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
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
          @current-change="loadRecords"
          @size-change="onPageSizeChange"
        />
      </div>
    </div>

    <el-drawer v-model="detailVisible" title="执行详情" size="480px" destroy-on-close>
      <template v-if="currentRow">
        <div class="drawer-meta">
          <div><span>任务ID</span>{{ currentRow.task_id }}</div>
          <div><span>任务名称</span>{{ currentRow.name }}</div>
          <div><span>测试环境</span>{{ currentRow.env }}</div>
          <div><span>执行方式</span>{{ currentRow.machine }}</div>
          <div><span>创建人</span>{{ currentRow.creator }}</div>
          <div><span>开始时间</span>{{ formatTime(currentRow.start_time) }}</div>
          <div><span>结束时间</span>{{ formatTime(currentRow.end_time) }}</div>
          <div><span>执行时长</span>{{ formatDuration(currentRow.duration_seconds) }}</div>
        </div>
        <div class="drawer-stats">
          <div class="stat-chip">总数 {{ currentRow.total_cases }}</div>
          <div class="stat-chip success">成功 {{ currentRow.success_count }}</div>
          <div class="stat-chip fail">失败 {{ currentRow.fail_count }}</div>
          <div class="stat-chip skip">跳过 {{ currentRow.skip_count }}</div>
          <div class="stat-chip">成功率 {{ currentRow.success_rate }}%</div>
        </div>
        <div class="drawer-section-title">执行日志</div>
        <pre class="run-logs">{{ currentRow.logs || '暂无日志' }}</pre>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, RefreshRight, Download, View, Delete,
  Folder, CircleCheck, CircleClose, PieChart, Timer,
} from '@element-plus/icons-vue'
import { uiExecutionApi } from '@/api'

const loading = ref(false)
const rows = ref([])
const total = ref(0)
const statCards = ref([])
const detailVisible = ref(false)
const currentRow = ref(null)

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

const loadRecords = async () => {
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
    await Promise.all([loadStats(), loadRecords()])
  } finally {
    loading.value = false
  }
}

const onSearch = () => {
  pagination.page = 1
  loadRecords()
}

const onPageSizeChange = () => {
  pagination.page = 1
  loadRecords()
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

const openDetail = async (row) => {
  try {
    currentRow.value = await uiExecutionApi.detail(row.id)
    detailVisible.value = true
  } catch {
    ElMessage.error('加载详情失败')
  }
}

const downloadReport = (row) => {
  const text = row.logs || `[INFO] 任务 ${row.task_id} 执行完成\n[INFO] 成功 ${row.success_count} · 失败 ${row.fail_count}`
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${row.task_id}-report.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const exportRecords = () => {
  if (!rows.value.length) {
    ElMessage.warning('当前页暂无数据可导出')
    return
  }
  const header = ['任务ID', '任务名称', '测试环境', '用例总数', '成功', '失败', '跳过', '成功率', '执行时长', '执行方式', '创建人', '开始时间', '状态']
  const lines = rows.value.map((r) => [
    r.task_id,
    r.name,
    r.env,
    r.total_cases,
    r.success_count,
    r.fail_count,
    r.skip_count,
    `${r.success_rate}%`,
    formatDuration(r.duration_seconds),
    r.machine,
    r.creator,
    formatTime(r.start_time),
    r.status,
  ].join(','))
  const csv = `\uFEFF${header.join(',')}\n${lines.join('\n')}`
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ui-execution-records-${Date.now()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

const removeRecord = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除任务 ${row.task_id} 吗？`, '删除确认', { type: 'warning' })
    await uiExecutionApi.remove(row.id)
    ElMessage.success('删除成功')
    if (rows.value.length === 1 && pagination.page > 1) pagination.page -= 1
    await loadAll()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(loadAll)
</script>

<style scoped lang="scss">
.ui-records-page {
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

.records-stat-grid {
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

.records-panel {
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

.toolbar-search {
  width: 240px;
}

.toolbar-date {
  width: 260px;
}

.toolbar-filter {
  width: 120px;
}

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

.task-link {
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 500;

  &:hover {
    text-decoration: underline;
  }
}

.num-success { color: #34c759; font-weight: 600; }
.num-fail { color: #ff3b30; font-weight: 600; }
.num-skip { color: #94a3b8; font-weight: 500; }

.rate-full { color: #34c759; font-weight: 600; }
.rate-good { color: #007aff; font-weight: 600; }
.rate-bad { color: #ff9500; font-weight: 600; }

.row-actions {
  display: flex;
  align-items: center;
  gap: 2px;

  .el-button {
    padding: 4px;
    color: var(--text-secondary);

    &:hover {
      color: var(--brand-primary);
    }
  }
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

.drawer-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--text-main);

  span {
    display: inline-block;
    width: 64px;
    color: var(--text-secondary);
  }
}

.drawer-stats {
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

.drawer-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 10px;
}

.run-logs {
  padding: 12px;
  border-radius: var(--glass-radius-sm);
  background: rgba(15, 23, 42, 0.88);
  color: rgba(255, 255, 255, 0.82);
  font-family: 'SF Mono', Consolas, monospace;
  font-size: 12px;
  line-height: 1.7;
  max-height: 280px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

@media (max-width: 1400px) {
  .records-stat-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .records-stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
