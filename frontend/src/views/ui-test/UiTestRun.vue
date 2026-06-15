<template>
  <div class="ui-run page-shell-fill" v-loading="loading">
    <el-breadcrumb separator="/" class="page-crumb">
      <el-breadcrumb-item :to="{ path: '/ui-test' }">UI 测试</el-breadcrumb-item>
      <el-breadcrumb-item>测试执行</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="run-header">
      <div class="run-header-text">
        <h1>测试执行</h1>
        <p>选择测试环境、用例与执行配置，开始自动化测试任务。</p>
      </div>
      <div class="run-header-actions">
        <el-button round @click="saveConfig">保存配置</el-button>
        <el-button round @click="resetConfig">清空配置</el-button>
        <el-button type="primary" round :loading="running" :disabled="!checkedCount" @click="startExecution">
          <el-icon><VideoPlay /></el-icon> 开始执行
        </el-button>
      </div>
    </div>

    <div class="run-body">
      <div class="run-main">
        <!-- 执行配置 -->
        <section class="panel glass-inner config-panel">
          <div class="panel-title">执行配置</div>
          <el-form label-width="88px" class="config-form" size="default">
            <el-form-item label="测试环境">
              <el-select v-model="execConfig.env" style="width: 100%">
                <el-option label="测试环境" value="测试环境" />
                <el-option label="预发环境" value="预发环境" />
                <el-option label="生产环境" value="生产环境" />
              </el-select>
            </el-form-item>
            <el-form-item label="执行机">
              <div class="machine-row">
                <el-select v-model="execConfig.machine" style="width: 100%">
                  <el-option label="Docker 执行机-01" value="Docker 执行机-01" />
                  <el-option label="Docker 执行机-02" value="Docker 执行机-02" />
                  <el-option label="本地执行机" value="本地执行机" />
                </el-select>
                <el-tag size="small" type="success" effect="light" round>空闲</el-tag>
              </div>
            </el-form-item>
            <el-form-item label="浏览器">
              <el-select v-model="execConfig.browser" style="width: 100%">
                <el-option label="Chrome" value="Chrome" />
                <el-option label="Firefox" value="Firefox" />
                <el-option label="Edge" value="Edge" />
              </el-select>
            </el-form-item>
            <el-form-item label="执行模式">
              <el-radio-group v-model="execConfig.mode">
                <el-radio value="parallel">并行执行</el-radio>
                <el-radio value="serial">串行执行</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="并发数">
              <el-input-number v-model="execConfig.concurrency" :min="1" :max="10" :disabled="execConfig.mode === 'serial'" />
            </el-form-item>
            <el-form-item label="超时时间">
              <el-input-number v-model="execConfig.timeout" :min="10" :max="600" />
              <span class="unit-text">秒</span>
            </el-form-item>
            <el-form-item label="失败重试">
              <el-input-number v-model="execConfig.retry" :min="0" :max="5" />
              <span class="unit-text">次</span>
            </el-form-item>
            <el-form-item label="高级选项">
              <div class="option-list">
                <el-checkbox v-model="execConfig.allure">生成 Allure 报告</el-checkbox>
                <el-checkbox v-model="execConfig.screenshot">失败截图</el-checkbox>
                <el-checkbox v-model="execConfig.video">失败录屏</el-checkbox>
                <el-checkbox v-model="execConfig.saveLog">保存运行日志</el-checkbox>
              </div>
            </el-form-item>
          </el-form>
        </section>

        <!-- 用例选择 -->
        <section class="panel glass-inner case-panel">
          <div class="panel-title">用例选择</div>
          <el-tabs v-model="caseTab" class="case-tabs">
            <el-tab-pane label="用例列表" name="list" />
            <el-tab-pane label="用例模块" name="module" />
            <el-tab-pane label="标签选择" name="tag" />
          </el-tabs>
          <div class="case-toolbar">
            <el-input
              v-model="keyword"
              placeholder="搜索用例名称"
              :prefix-icon="Search"
              clearable
              class="case-search"
            />
            <el-button circle :icon="Filter" @click="ElMessage.info('筛选功能建设中')" />
          </div>

          <el-tree
            v-if="caseTab !== 'tag'"
            ref="treeRef"
            :key="caseTab"
            :data="treeData"
            :props="{ label: 'label', children: 'children' }"
            :filter-node-method="filterNode"
            show-checkbox
            node-key="id"
            :default-expand-all="caseTab === 'list'"
            :default-expanded-keys="caseTab === 'module' ? expandedModuleKeys : []"
            class="case-tree"
            @check="onTreeCheck"
          >
            <template #default="{ data }">
              <span class="tree-node">
                <el-icon v-if="!data.isCase" class="folder-icon"><Folder /></el-icon>
                <span class="node-label">{{ data.label }}</span>
              </span>
            </template>
          </el-tree>

          <div v-else class="tag-select-list">
            <el-checkbox-group v-model="selectedTags" @change="syncTagSelection">
              <el-checkbox v-for="tag in allTags" :key="tag" :label="tag" :value="tag">
                {{ tag }}
              </el-checkbox>
            </el-checkbox-group>
            <el-empty v-if="!allTags.length" description="暂无标签" :image-size="56" />
          </div>

          <div class="case-foot">
            <span>已选 <strong>{{ checkedCount }}</strong> 个用例</span>
            <el-button link type="primary" :disabled="!checkedCount" @click="clearSelection">清空</el-button>
          </div>
        </section>

        <!-- 执行日志 -->
        <section class="panel glass-terminal log-panel">
          <div class="log-head">
            <span class="log-title">执行日志</span>
            <div class="log-tools">
              <el-checkbox v-model="autoScroll" size="small">自动滚动</el-checkbox>
              <el-button text size="small" class="log-tool-btn" @click="clearLogs">清空</el-button>
              <el-button text size="small" class="log-tool-btn" @click="exportLogs">
                <el-icon><Download /></el-icon> 导出日志
              </el-button>
            </div>
          </div>
          <div ref="logRef" class="log-body">
            <template v-if="terminalLines.length">
              <div v-for="(line, i) in terminalLines" :key="i" class="log-line">
                <span class="log-time">{{ line.time }}</span>
                <span class="log-level" :class="line.level">{{ line.levelText }}</span>
                <span class="log-msg">{{ line.message }}</span>
              </div>
            </template>
            <div v-else class="log-empty">
              <el-icon :size="32"><Monitor /></el-icon>
              <p>选择用例并点击「开始执行」查看实时日志</p>
            </div>
          </div>
        </section>
      </div>

      <div class="run-bottom">
        <section class="panel glass-inner result-panel">
          <div class="panel-title">
            执行结果
            <el-tag v-if="execResult.status" size="small" :type="execResult.status === '已完成' ? 'success' : 'warning'" effect="light" round>
              {{ execResult.status }}
            </el-tag>
          </div>
          <div class="result-stats">
            <div class="result-stat">
              <div class="stat-num">{{ execResult.total }}</div>
              <div class="stat-label">用例总数</div>
            </div>
            <div class="result-stat success">
              <div class="stat-num">{{ execResult.passed }}</div>
              <div class="stat-label">成功</div>
            </div>
            <div class="result-stat fail">
              <div class="stat-num">{{ execResult.failed }}</div>
              <div class="stat-label">失败</div>
            </div>
            <div class="result-stat skip">
              <div class="stat-num">{{ execResult.skipped }}</div>
              <div class="stat-label">跳过</div>
            </div>
            <div class="result-stat rate">
              <div class="stat-num">{{ execResult.rate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </div>
        </section>

        <section class="panel glass-inner info-panel">
          <div class="panel-title">执行信息</div>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">任务 ID</span>
              <span class="info-value">{{ execInfo.taskId || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">开始时间</span>
              <span class="info-value">{{ execInfo.startTime || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">结束时间</span>
              <span class="info-value">{{ execInfo.endTime || '—' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">执行时长</span>
              <span class="info-value">{{ execInfo.duration || '—' }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Filter, Folder, Download, VideoPlay, Monitor } from '@element-plus/icons-vue'
import { caseApi, uiExecutionApi } from '@/api'

const CONFIG_KEY = 'ui-test-exec-config'

const route = useRoute()

const loading = ref(false)
const running = ref(false)
const keyword = ref('')
const caseTab = ref('list')
const uiCases = ref([])
const treeRef = ref()
const logRef = ref()
const terminalLines = ref([])
const autoScroll = ref(true)
const checkedCaseIds = ref([])
const selectedTags = ref([])

const execConfig = reactive({
  env: '测试环境',
  machine: 'Docker 执行机-01',
  browser: 'Chrome',
  mode: 'parallel',
  concurrency: 3,
  timeout: 60,
  retry: 0,
  allure: true,
  screenshot: true,
  video: true,
  saveLog: true,
})

const execResult = reactive({
  status: '',
  total: 0,
  passed: 0,
  failed: 0,
  skipped: 0,
  rate: 0,
})

const execInfo = reactive({
  taskId: '',
  startTime: '',
  endTime: '',
  duration: '',
})

const enabledCases = computed(() => uiCases.value.filter((c) => c.is_enabled !== false))

const allTags = computed(() => {
  const tags = new Set()
  enabledCases.value.forEach((c) => {
    const list = (c.tags || '').split(',').map((t) => t.trim()).filter(Boolean)
    list.forEach((t) => tags.add(t))
  })
  return [...tags].sort()
})

const treeData = computed(() => {
  const groups = {}
  enabledCases.value.forEach((c) => {
    if (!groups[c.module]) groups[c.module] = []
    groups[c.module].push({
      id: `case-${c.id}`,
      label: c.name,
      isCase: true,
      raw: c,
    })
  })
  return Object.entries(groups).map(([module, items], idx) => ({
    id: `group-${idx}`,
    label: module,
    module,
    children: items,
  }))
})

const expandedModuleKeys = computed(() => treeData.value.map((g) => g.id))

const checkedCount = computed(() => checkedCaseIds.value.length)

watch(keyword, (val) => treeRef.value?.filter(val))
const filterNode = (value, data) => !value || data.label.includes(value)

const fmtClock = () => {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

const fmtDateTime = (date) => {
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

const toApiDateTime = (date) => fmtDateTime(date).replace(' ', 'T')

const pushLog = (level, levelText, message) => {
  terminalLines.value.push({ time: fmtClock(), level, levelText, message })
  if (autoScroll.value) {
    nextTick(() => {
      if (logRef.value) logRef.value.scrollTop = logRef.value.scrollHeight
    })
  }
}

const getCheckedCases = () =>
  enabledCases.value.filter((c) => checkedCaseIds.value.includes(`case-${c.id}`))

const onTreeCheck = () => {
  checkedCaseIds.value = treeRef.value?.getCheckedKeys(true).filter((k) => String(k).startsWith('case-')) || []
}

const restoreTreeSelection = (keys) => {
  if (!keys?.length) return
  nextTick(() => {
    treeRef.value?.setCheckedKeys(keys)
    checkedCaseIds.value = keys.filter((k) => String(k).startsWith('case-'))
  })
}

const clearSelection = () => {
  treeRef.value?.setCheckedKeys([])
  checkedCaseIds.value = []
  selectedTags.value = []
}

const syncTagSelection = () => {
  const ids = enabledCases.value
    .filter((c) => {
      const tags = (c.tags || '').split(',').map((t) => t.trim())
      return selectedTags.value.some((t) => tags.includes(t))
    })
    .map((c) => `case-${c.id}`)
  treeRef.value?.setCheckedKeys(ids)
  checkedCaseIds.value = ids
}

const saveConfig = () => {
  localStorage.setItem(CONFIG_KEY, JSON.stringify({ ...execConfig }))
  ElMessage.success('执行配置已保存')
}

const resetConfig = () => {
  Object.assign(execConfig, {
    env: '测试环境',
    machine: 'Docker 执行机-01',
    browser: 'Chrome',
    mode: 'parallel',
    concurrency: 3,
    timeout: 60,
    retry: 0,
    allure: true,
    screenshot: true,
    video: true,
    saveLog: true,
  })
  clearSelection()
  terminalLines.value = []
  Object.assign(execResult, { status: '', total: 0, passed: 0, failed: 0, skipped: 0, rate: 0 })
  Object.assign(execInfo, { taskId: '', startTime: '', endTime: '', duration: '' })
  localStorage.removeItem(CONFIG_KEY)
  ElMessage.success('配置已清空')
}

const loadSavedConfig = () => {
  try {
    const saved = JSON.parse(localStorage.getItem(CONFIG_KEY) || 'null')
    if (saved) Object.assign(execConfig, saved)
  } catch {
    // ignore
  }
}

const runSingleCase = async (caseItem) => {
  pushLog('info', '[INFO]', `开始执行用例：${caseItem.name}`)
  try {
    const res = await caseApi.runUiCase(caseItem.id)
    const ok = res.status === '已通过'
    pushLog(ok ? 'pass' : 'fail', ok ? '[PASS]' : '[FAIL]', `${caseItem.name} → ${res.status}`)
    res.logs?.forEach((log) => pushLog('step', '[STEP]', log.step || '步骤执行'))
    return ok
  } catch {
    pushLog('fail', '[FAIL]', `${caseItem.name} → 执行异常`)
    return false
  }
}

const runInBatches = async (cases, concurrency) => {
  let passed = 0
  let failed = 0
  for (let i = 0; i < cases.length; i += concurrency) {
    const batch = cases.slice(i, i + concurrency)
    const results = await Promise.all(batch.map((c) => runSingleCase(c)))
    results.forEach((ok) => { if (ok) passed += 1; else failed += 1 })
  }
  return { passed, failed }
}

const startExecution = async () => {
  const cases = getCheckedCases()
  if (!cases.length) {
    ElMessage.warning('请至少选择一个用例')
    return
  }

  running.value = true
  terminalLines.value = []
  const selectedIds = [...checkedCaseIds.value]
  const start = new Date()
  const taskId = `UI-${start.getFullYear()}${String(start.getMonth() + 1).padStart(2, '0')}${String(start.getDate()).padStart(2, '0')}-${String(Math.floor(Math.random() * 900) + 100)}`

  Object.assign(execInfo, {
    taskId,
    startTime: fmtDateTime(start),
    endTime: '',
    duration: '',
  })
  Object.assign(execResult, {
    status: '执行中',
    total: cases.length,
    passed: 0,
    failed: 0,
    skipped: 0,
    rate: 0,
  })

  pushLog('info', '[INFO]', `任务 ${taskId} 已创建`)
  pushLog('info', '[INFO]', `环境：${execConfig.env} · 执行机：${execConfig.machine} · 浏览器：${execConfig.browser}`)
  pushLog('info', '[INFO]', `模式：${execConfig.mode === 'parallel' ? '并行' : '串行'}执行 · 并发 ${execConfig.concurrency}`)

  let passed = 0
  let failed = 0

  try {
    if (execConfig.mode === 'parallel') {
      const result = await runInBatches(cases, execConfig.concurrency)
      passed = result.passed
      failed = result.failed
    } else {
      for (const item of cases) {
        const ok = await runSingleCase(item)
        if (ok) passed += 1
        else failed += 1
      }
    }

    const end = new Date()
    const seconds = Math.max(1, Math.round((end - start) / 1000))
    const rate = cases.length ? Math.round((passed / cases.length) * 100) : 0

    Object.assign(execResult, {
      status: '已完成',
      total: cases.length,
      passed,
      failed,
      skipped: 0,
      rate,
    })
    Object.assign(execInfo, {
      endTime: fmtDateTime(end),
      duration: `${seconds}s`,
    })

    pushLog('info', '[INFO]', `任务完成 · 成功 ${passed} · 失败 ${failed} · 成功率 ${rate}%`)
    if (execConfig.allure) pushLog('info', '[INFO]', 'Allure 报告已生成')

    const logText = terminalLines.value.map((l) => `${l.time} ${l.levelText} ${l.message}`).join('\n')
    const taskName = cases.length === 1 ? cases[0].name : `批量执行-${cases.length}个用例`
    try {
      const saved = await uiExecutionApi.create({
        name: taskName,
        env: execConfig.env,
        total_cases: cases.length,
        success_count: passed,
        fail_count: failed,
        skip_count: 0,
        duration_seconds: seconds,
        machine: execConfig.machine,
        mode: execConfig.mode,
        logs: logText,
        start_time: toApiDateTime(start),
        end_time: toApiDateTime(end),
      })
      execInfo.taskId = saved.task_id
      execInfo.startTime = fmtDateTime(new Date(saved.start_time))
      execInfo.endTime = fmtDateTime(new Date(saved.end_time))
    } catch {
      pushLog('info', '[INFO]', '执行记录保存失败，请稍后重试')
    }

    ElMessage.success(`执行完成，成功率 ${rate}%`)
    await loadCases()
    restoreTreeSelection(selectedIds)
  } finally {
    running.value = false
  }
}

const clearLogs = () => {
  terminalLines.value = []
}

const exportLogs = () => {
  if (!terminalLines.value.length) {
    ElMessage.warning('暂无日志可导出')
    return
  }
  const text = terminalLines.value.map((l) => `${l.time} ${l.levelText} ${l.message}`).join('\n')
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${execInfo.taskId || 'ui-exec'}-log.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const loadCases = async () => {
  uiCases.value = await caseApi.uiCases()
}

const applyQueryCase = () => {
  const caseId = Number(route.query.caseId)
  if (!caseId) return
  nextTick(() => {
    treeRef.value?.setChecked(`case-${caseId}`, true, false)
    onTreeCheck()
  })
}

onMounted(async () => {
  loadSavedConfig()
  loading.value = true
  try {
    await loadCases()
    applyQueryCase()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.ui-run {
  gap: 16px;
  padding: 20px 24px;
}

.run-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;

  h1 {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    color: var(--text-main);
  }

  p {
    margin: 8px 0 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
  }
}

.run-header-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.run-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.run-main {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(260px, 0.85fr) minmax(280px, 1fr) minmax(320px, 1.25fr);
  gap: 14px;
}

.run-bottom {
  flex-shrink: 0;
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 14px;
}

.panel {
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-panel,
.case-panel,
.result-panel,
.info-panel {
  padding: 16px 18px;
}

.config-form {
  :deep(.el-form-item) {
    margin-bottom: 14px;
  }

  :deep(.el-form-item__label) {
    color: var(--text-secondary);
    font-size: 13px;
  }
}

.machine-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.unit-text {
  margin-left: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.option-list {
  display: flex;
  flex-direction: column;
  gap: 8px;

  :deep(.el-checkbox__label) {
    font-size: 13px;
  }
}

.case-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 10px;
  }

  :deep(.el-tabs__item) {
    font-size: 13px;
    padding: 0 12px;
  }
}

.case-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;

  .case-search {
    flex: 1;
  }
}

.case-tree {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.tag-select-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 4px 2px;

  :deep(.el-checkbox-group) {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;

  .folder-icon {
    color: var(--brand-primary);
  }

  .node-label {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.case-foot {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.45);
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);

  strong {
    color: var(--brand-primary);
  }
}

.log-panel {
  padding: 0;
}

.log-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.log-title {
  font-size: 14px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
}

.log-tools {
  display: flex;
  align-items: center;
  gap: 8px;

  :deep(.el-checkbox__label) {
    color: rgba(255, 255, 255, 0.62);
    font-size: 12px;
  }
}

.log-tool-btn {
  color: rgba(255, 255, 255, 0.62) !important;
  font-size: 12px !important;

  &:hover {
    color: rgba(255, 255, 255, 0.92) !important;
  }
}

.log-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 14px 16px;
  font-family: 'SF Mono', Consolas, Monaco, monospace;
  font-size: 12px;
  line-height: 1.75;
}

.log-line {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.log-time {
  color: rgba(255, 255, 255, 0.45);
  flex-shrink: 0;
}

.log-level {
  flex-shrink: 0;
  font-weight: 600;

  &.info { color: #60a5fa; }
  &.step { color: #fbbf24; }
  &.pass { color: #4ade80; }
  &.fail { color: #f87171; }
}

.log-msg {
  color: rgba(255, 255, 255, 0.84);
}

.log-empty {
  height: 100%;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.35);
  font-size: 13px;

  p { margin: 0; }
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.result-stat {
  padding: 14px 10px;
  border-radius: 12px;
  text-align: center;
  background: rgba(255, 255, 255, 0.42);
  border: 1px solid rgba(255, 255, 255, 0.55);

  .stat-num {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1.2;
  }

  .stat-label {
    margin-top: 4px;
    font-size: 12px;
    color: var(--text-secondary);
  }

  &.success .stat-num { color: #34c759; }
  &.fail .stat-num { color: #ff3b30; }
  &.skip .stat-num { color: #94a3b8; }
  &.rate .stat-num { color: #007aff; }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.info-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  word-break: break-all;
}

@media (max-width: 1400px) {
  .run-main {
    grid-template-columns: 1fr 1fr;
  }

  .log-panel {
    grid-column: 1 / -1;
    min-height: 280px;
  }
}

@media (max-width: 1024px) {
  .run-main,
  .run-bottom,
  .result-stats {
    grid-template-columns: 1fr;
  }

  .run-header {
    flex-direction: column;
  }

  .ui-run {
    overflow-y: auto;
  }
}
</style>
