<template>
  <div class="ui-cases-page page-shell" v-loading="loading">
    <el-breadcrumb separator="/" class="page-crumb">
      <el-breadcrumb-item :to="{ path: '/ui-test' }">UI 测试</el-breadcrumb-item>
      <el-breadcrumb-item>用例管理</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="page-intro">
      <h1>用例管理</h1>
      <p>管理所有 UI 自动化测试用例，支持上传、编辑、执行和维护。</p>
    </div>

    <div class="glass-stat-grid cases-stat-grid">
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

    <div class="cases-panel glass-inner">
      <el-tabs v-model="activeTab" class="cases-tabs">
        <el-tab-pane label="用例列表" name="list" />
        <el-tab-pane :label="`回收站${trashedCases.length ? ` (${trashedCases.length})` : ''}`" name="trash" />
      </el-tabs>

      <div class="toolbar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索用例名称、文件名、标签"
          :prefix-icon="Search"
          clearable
          class="toolbar-search"
        />
        <el-select v-model="filters.module" placeholder="所有模块" clearable class="toolbar-filter">
          <el-option v-for="m in moduleOptions" :key="m" :label="m" :value="m" />
        </el-select>
        <el-select v-model="filters.tag" placeholder="所有标签" clearable class="toolbar-filter">
          <el-option v-for="t in tagOptions" :key="t" :label="t" :value="t" />
        </el-select>
        <el-select v-model="filters.enabled" placeholder="所有状态" clearable class="toolbar-filter">
          <el-option label="启用" value="enabled" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-select v-model="filters.creator" placeholder="创建人" clearable class="toolbar-filter">
          <el-option v-for="c in creatorOptions" :key="c" :label="c" :value="c" />
        </el-select>
        <el-button circle :icon="RefreshRight" @click="resetFilters" />
        <div class="toolbar-actions">
          <el-button type="primary" round @click="uploadDialog = true">
            <el-icon><Plus /></el-icon> 上传用例
          </el-button>
          <el-button round @click="importDialog = true">
            <el-icon><Upload /></el-icon> 导入用例
          </el-button>
        </div>
      </div>

      <div class="table-wrap">
        <el-table
          :data="pagedRows"
          style="width: 100%"
          @selection-change="onSelectionChange"
        >
          <el-table-column type="selection" width="44" />
          <el-table-column prop="name" label="用例名称" min-width="160" show-overflow-tooltip />
          <el-table-column prop="module" label="所属模块" width="110" show-overflow-tooltip />
          <el-table-column label="标签" min-width="160">
            <template #default="{ row }">
              <div class="tag-group">
                <span
                  v-for="tag in row.tagList"
                  :key="tag"
                  class="case-tag"
                  :class="tagClass(tag)"
                >{{ tag }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="filename" label="文件名" width="168" show-overflow-tooltip />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag
                :type="row.is_enabled ? 'success' : 'warning'"
                size="small"
                effect="light"
                round
              >
                {{ row.is_enabled ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="creator" label="创建人" width="88" />
          <el-table-column label="更新时间" width="168">
            <template #default="{ row }">{{ formatTime(row.updated_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="148" fixed="right">
            <template #default="{ row }">
              <div class="row-actions">
                <el-button text size="small" @click="openView(row)"><el-icon><View /></el-icon></el-button>
                <el-button text size="small" @click="openEdit(row)"><el-icon><EditPen /></el-icon></el-button>
                <el-button text size="small" @click="downloadCase(row)"><el-icon><Download /></el-icon></el-button>
                <el-dropdown trigger="click" @command="(cmd) => onRowMore(cmd, row)">
                  <el-button text size="small"><el-icon><MoreFilled /></el-icon></el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="run">运行用例</el-dropdown-item>
                      <el-dropdown-item command="toggle">{{ row.is_enabled ? '禁用' : '启用' }}</el-dropdown-item>
                      <el-dropdown-item command="copy">复制用例</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除用例</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="table-foot">
        <span class="total-text">共 {{ filteredRows.length }} 条</span>
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredRows.length"
          layout="prev, pager, next, sizes, jumper"
          background
          small
        />
      </div>
    </div>

    <!-- 查看 / 运行 -->
    <el-drawer v-model="viewDrawer" :title="viewCase?.name || '用例详情'" size="520px">
      <template v-if="viewCase">
        <div class="drawer-meta">
          <div><span>模块</span>{{ viewCase.module }}</div>
          <div><span>文件</span>{{ viewCase.filename }}</div>
          <div><span>创建人</span>{{ viewCase.creator }}</div>
          <div><span>浏览器</span>{{ viewCase.browser }}</div>
        </div>
        <div class="drawer-actions">
          <el-button type="primary" round :loading="running" @click="runCase(viewCase)">
            <el-icon><VideoPlay /></el-icon> 运行
          </el-button>
          <el-button round @click="openEdit(viewCase)">编辑</el-button>
        </div>
        <div class="drawer-section-title">测试步骤（{{ viewCase.steps?.length || 0 }}）</div>
        <el-table :data="viewCase.steps || []" size="small" max-height="360">
          <el-table-column type="index" label="#" width="44" />
          <el-table-column prop="action" label="操作" width="90" />
          <el-table-column prop="locator" label="定位" min-width="120" show-overflow-tooltip />
          <el-table-column prop="desc" label="说明" min-width="120" show-overflow-tooltip />
        </el-table>
        <div v-if="runLogs.length" class="run-logs">
          <div class="drawer-section-title">执行日志</div>
          <div v-for="(line, i) in runLogs" :key="i" class="log-line">{{ line }}</div>
        </div>
      </template>
    </el-drawer>

    <!-- 新建 / 编辑 -->
    <el-dialog v-model="caseDialog" :title="caseDialogTitle" width="520px">
      <el-form :model="caseForm" label-width="90px">
        <el-form-item label="用例名称"><el-input v-model="caseForm.name" /></el-form-item>
        <el-form-item label="所属模块"><el-input v-model="caseForm.module" /></el-form-item>
        <el-form-item label="文件名"><el-input v-model="caseForm.filename" placeholder="test_xxx.py" /></el-form-item>
        <el-form-item label="标签"><el-input v-model="caseForm.tags" placeholder="smoke,P0" /></el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="caseForm.priority" style="width: 100%">
            <el-option label="高 (P0)" value="高" />
            <el-option label="中 (P1)" value="中" />
            <el-option label="低 (P2)" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="浏览器">
          <el-select v-model="caseForm.browser" style="width: 100%">
            <el-option label="Chrome" value="Chrome" />
            <el-option label="Firefox" value="Firefox" />
            <el-option label="Edge" value="Edge" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="caseForm.is_enabled" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button round @click="caseDialog = false">取消</el-button>
        <el-button type="primary" round :loading="saving" @click="saveCase">保存</el-button>
      </template>
    </el-dialog>

    <!-- 上传用例 -->
    <UploadCaseDialog v-model="uploadDialog" @success="loadCases" />

    <!-- 导入 -->
    <el-dialog v-model="importDialog" title="导入用例（JSON）" width="520px">
      <el-input
        v-model="importText"
        type="textarea"
        :rows="10"
        placeholder='[{"name":"登录功能测试","module":"登录模块","filename":"test_login.py","tags":"smoke,P0","steps":[]}]'
      />
      <template #footer>
        <el-button round @click="importDialog = false">取消</el-button>
        <el-button type="primary" round @click="importCases">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, RefreshRight, Plus, Upload, View, EditPen, Download, MoreFilled, VideoPlay,
  Folder, CircleCheck, Warning, Grid,
} from '@element-plus/icons-vue'
import { caseApi } from '@/api'
import UploadCaseDialog from '@/components/UploadCaseDialog.vue'

const router = useRouter()

const loading = ref(false)
const uploadDialog = ref(false)
const saving = ref(false)
const running = ref(false)
const activeTab = ref('list')
const cases = ref([])
const trashedCases = ref([])
const selectedRows = ref([])
const page = ref(1)
const pageSize = ref(20)

const filters = reactive({
  keyword: '',
  module: '',
  tag: '',
  enabled: '',
  creator: '',
})

const statIcons = [Folder, CircleCheck, Warning, Grid]
const statIconBg = [
  'rgba(0,122,255,0.12)',
  'rgba(52,199,89,0.12)',
  'rgba(255,149,0,0.12)',
  'rgba(88,86,214,0.12)',
]

const priorityTagMap = { 高: 'P0', 中: 'P1', 低: 'P2' }

const normalizeCase = (item) => {
  const tags = item.tags || ''
  const tagList = tags
    ? tags.split(',').map((t) => t.trim()).filter(Boolean)
    : [priorityTagMap[item.priority] || 'P2']
  if (!tags.includes('smoke') && !tags.includes('regression') && item.module?.includes('登录')) {
    tagList.unshift('smoke')
  }
  return {
    ...item,
    is_enabled: Boolean(item.is_enabled),
    filename: item.filename || `test_case_${item.id}.py`,
    tagList: [...new Set(tagList)],
  }
}

const activeSource = computed(() => (activeTab.value === 'trash' ? trashedCases.value : cases.value))

const moduleOptions = computed(() =>
  [...new Set(activeSource.value.map((c) => c.module).filter(Boolean))].sort()
)

const tagOptions = computed(() => {
  const tags = new Set()
  activeSource.value.forEach((c) => c.tagList.forEach((t) => tags.add(t)))
  return [...tags].sort()
})

const creatorOptions = computed(() =>
  [...new Set(activeSource.value.map((c) => c.creator).filter(Boolean))].sort()
)

const caseTime = (item) => new Date(item.created_at || item.updated_at).getTime()

const buildTrend = (current, previous, reverse = false) => {
  const diff = current - previous
  return {
    trendLabel: '较上周',
    trendText: diff > 0 ? `+${diff}` : diff < 0 ? String(diff) : '持平',
    trendUp: reverse ? diff <= 0 : diff >= 0,
  }
}

const statCards = computed(() => {
  const list = cases.value
  const weekAgo = Date.now() - 7 * 24 * 3600 * 1000
  const existed = (item) => {
    const ts = caseTime(item)
    return !Number.isNaN(ts) && ts <= weekAgo
  }

  const total = list.length
  const totalPrev = list.filter(existed).length
  const enabled = list.filter((c) => c.is_enabled).length
  const enabledPrev = list.filter((c) => existed(c) && c.is_enabled).length
  const disabled = total - enabled
  const disabledPrev = totalPrev - enabledPrev
  const modules = new Set(list.map((c) => c.module).filter(Boolean)).size
  const modulesPrev = new Set(list.filter(existed).map((c) => c.module).filter(Boolean)).size

  return [
    { key: 'total', label: '用例总数', value: total, ...buildTrend(total, totalPrev) },
    { key: 'enabled', label: '启用用例', value: enabled, ...buildTrend(enabled, enabledPrev) },
    { key: 'disabled', label: '禁用用例', value: disabled, ...buildTrend(disabled, disabledPrev, true) },
    { key: 'modules', label: '用例模块', value: modules, ...buildTrend(modules, modulesPrev) },
  ]
})

const filteredRows = computed(() => {
  const kw = filters.keyword.trim().toLowerCase()
  return activeSource.value.filter((row) => {
    if (kw) {
      const hit = [row.name, row.filename, row.tags, row.module]
        .join(' ')
        .toLowerCase()
        .includes(kw)
      if (!hit) return false
    }
    if (filters.module && row.module !== filters.module) return false
    if (filters.tag && !row.tagList.includes(filters.tag)) return false
    if (filters.enabled === 'enabled' && !row.is_enabled) return false
    if (filters.enabled === 'disabled' && row.is_enabled) return false
    if (filters.creator && row.creator !== filters.creator) return false
    return true
  })
})

const pagedRows = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

watch([filteredRows, pageSize], () => {
  page.value = 1
})

const tagClass = (tag) => {
  if (tag === 'smoke') return 'tag-smoke'
  if (tag === 'regression') return 'tag-regression'
  if (tag === 'P0') return 'tag-p0'
  if (tag === 'P1') return 'tag-p1'
  if (tag === 'P2') return 'tag-p2'
  return 'tag-default'
}

const formatTime = (value) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value || '—'
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

const resetFilters = () => {
  Object.assign(filters, { keyword: '', module: '', tag: '', enabled: '', creator: '' })
}

const onSelectionChange = (rows) => {
  selectedRows.value = rows
}

const loadCases = async () => {
  const list = await caseApi.uiCases()
  cases.value = list.map(normalizeCase)
}

// View / Run
const viewDrawer = ref(false)
const viewCase = ref(null)
const runLogs = ref([])

const openView = (row) => {
  viewCase.value = { ...row }
  runLogs.value = []
  viewDrawer.value = true
}

const runCase = async (row) => {
  running.value = true
  runLogs.value = [`[INFO] 开始执行 ${row.name}`]
  try {
    const res = await caseApi.runUiCase(row.id)
    runLogs.value = [
      `[INFO] 开始执行 ${row.name}`,
      ...res.logs.map((l) => `[PASS] ${l.step || '步骤执行成功'}`),
      `[INFO] 执行完成，状态：${res.status}`,
    ]
    ElMessage.success(`运行完成：${res.status}`)
    await loadCases()
    if (viewCase.value?.id === row.id) {
      viewCase.value = cases.value.find((c) => c.id === row.id) || viewCase.value
    }
  } finally {
    running.value = false
  }
}

// CRUD
const caseDialog = ref(false)
const caseEditId = ref(null)
const caseForm = reactive({
  name: '',
  module: '',
  filename: '',
  tags: '',
  priority: '中',
  browser: 'Chrome',
  is_enabled: true,
  status: '未执行',
  creator: 'admin',
  steps: [],
})

const caseDialogTitle = computed(() => (caseEditId.value ? '编辑用例' : '新建用例'))

const openEdit = (row) => {
  caseEditId.value = row?.id || null
  if (row) {
    Object.assign(caseForm, {
      name: row.name,
      module: row.module,
      filename: row.filename,
      tags: row.tags || row.tagList.join(','),
      priority: row.priority,
      browser: row.browser,
      is_enabled: row.is_enabled,
      status: row.status,
      creator: row.creator,
      steps: row.steps || [],
    })
  } else {
    Object.assign(caseForm, {
      name: '',
      module: '登录模块',
      filename: '',
      tags: 'smoke,P0',
      priority: '高',
      browser: 'Chrome',
      is_enabled: true,
      status: '未执行',
      creator: 'admin',
      steps: [],
    })
  }
  caseDialog.value = true
}

const saveCase = async () => {
  if (!caseForm.name.trim()) {
    ElMessage.warning('请输入用例名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: caseForm.name.trim(),
      module: caseForm.module.trim(),
      filename: caseForm.filename.trim() || `test_${Date.now()}.py`,
      tags: caseForm.tags.trim(),
      priority: caseForm.priority,
      browser: caseForm.browser,
      is_enabled: caseForm.is_enabled,
      status: caseForm.status,
      creator: caseForm.creator,
      steps: caseForm.steps,
    }
    if (caseEditId.value) {
      await caseApi.updateUiCase(caseEditId.value, payload)
      ElMessage.success('用例已更新')
    } else {
      await caseApi.createUiCase(payload)
      ElMessage.success('用例已创建')
    }
    caseDialog.value = false
    await loadCases()
  } finally {
    saving.value = false
  }
}

const downloadCase = (row) => {
  const blob = new Blob([JSON.stringify(row, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${row.filename.replace('.py', '') || row.name}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const onRowMore = async (cmd, row) => {
  if (cmd === 'run') {
    router.push({ path: '/ui-test/run', query: { caseId: row.id } })
    return
  }
  if (cmd === 'toggle') {
    await caseApi.updateUiCase(row.id, {
      ...row,
      is_enabled: !row.is_enabled,
      steps: row.steps || [],
    })
    ElMessage.success(row.is_enabled ? '已禁用' : '已启用')
    await loadCases()
    return
  }
  if (cmd === 'copy') {
    await caseApi.createUiCase({
      name: `${row.name}（副本）`,
      module: row.module,
      filename: row.filename.replace('.py', '_copy.py'),
      tags: row.tags,
      priority: row.priority,
      browser: row.browser,
      is_enabled: row.is_enabled,
      status: '未执行',
      creator: row.creator,
      steps: row.steps || [],
    })
    ElMessage.success('已复制用例')
    await loadCases()
    return
  }
  if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm(`确定删除用例「${row.name}」吗？`, '删除确认', { type: 'warning' })
    } catch {
      return
    }
    if (activeTab.value === 'trash') {
      await caseApi.removeUiCase(row.id)
      trashedCases.value = trashedCases.value.filter((c) => c.id !== row.id)
    } else {
      trashedCases.value.unshift({ ...row, deletedAt: Date.now() })
      await caseApi.removeUiCase(row.id)
      cases.value = cases.value.filter((c) => c.id !== row.id)
    }
    ElMessage.success('已删除')
  }
}

const importDialog = ref(false)
const importText = ref('')

const importCases = async () => {
  try {
    const parsed = JSON.parse(importText.value)
    const list = Array.isArray(parsed) ? parsed : [parsed]
    for (const item of list) {
      await caseApi.createUiCase({
        name: item.name || '未命名用例',
        module: item.module || '默认模块',
        filename: item.filename || `test_${Date.now()}.py`,
        tags: item.tags || 'P2',
        priority: item.priority || '中',
        browser: item.browser || 'Chrome',
        is_enabled: item.is_enabled !== false,
        status: '未执行',
        creator: item.creator || 'admin',
        steps: item.steps || [],
      })
    }
    ElMessage.success(`已导入 ${list.length} 条用例`)
    importDialog.value = false
    importText.value = ''
    await loadCases()
  } catch {
    ElMessage.error('JSON 格式不正确')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await loadCases()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.ui-cases-page {
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

.cases-stat-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
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

.cases-panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 0 0 12px;
  overflow: hidden;
}

.cases-tabs {
  padding: 0 18px;

  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background: rgba(255, 255, 255, 0.45);
  }
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 14px 18px 12px;
}

.toolbar-search {
  width: 260px;
}

.toolbar-filter {
  width: 120px;
}

.toolbar-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
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

.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.case-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.4;
}

.tag-smoke {
  color: #248a3d;
  background: rgba(52, 199, 89, 0.14);
}

.tag-regression {
  color: #5856d6;
  background: rgba(88, 86, 214, 0.12);
}

.tag-p0 {
  color: #d70015;
  background: rgba(255, 59, 48, 0.1);
}

.tag-p1 {
  color: #007aff;
  background: rgba(0, 122, 255, 0.1);
}

.tag-p2 {
  color: #64748b;
  background: rgba(148, 163, 184, 0.16);
}

.tag-default {
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.45);
}

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
    width: 52px;
    color: var(--text-secondary);
  }
}

.drawer-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}

.drawer-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 10px;
}

.run-logs {
  margin-top: 18px;
  padding: 12px;
  border-radius: var(--glass-radius-sm);
  background: rgba(15, 23, 42, 0.88);
  color: rgba(255, 255, 255, 0.82);
  font-family: 'SF Mono', Consolas, monospace;
  font-size: 12px;
  line-height: 1.7;
  max-height: 180px;
  overflow: auto;
}

@media (max-width: 1280px) {
  .cases-stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .toolbar-actions {
    width: 100%;
    margin-left: 0;
    justify-content: flex-end;
  }
}
</style>
