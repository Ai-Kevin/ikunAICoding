<template>
  <div class="ui-test page-shell-fill" v-loading="loading">
    <div class="page-header">
      <el-breadcrumb separator="/" class="page-crumb">
        <el-breadcrumb-item>UI 测试</el-breadcrumb-item>
        <el-breadcrumb-item>用例列表</el-breadcrumb-item>
        <el-breadcrumb-item>{{ selectedCase.name || '请选择用例' }}</el-breadcrumb-item>
      </el-breadcrumb>

      <div class="header-main">
        <div class="header-left">
          <div class="page-title-row">
            <h1>{{ selectedCase.name || '请选择用例' }}</h1>
            <el-tag v-if="selectedCase.id" :type="statusTagType" size="small" effect="light">
              {{ displayStatus }}
            </el-tag>
            <el-icon v-if="selectedCase.id" class="edit-icon" @click="openEditCase"><EditPen /></el-icon>
          </div>
          <div class="meta-grid" v-if="selectedCase.id">
            <div class="meta-item">
              <span class="meta-label">所属模块</span>
              <span class="meta-value">{{ selectedCase.module }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">环境</span>
              <span class="meta-value">{{ currentEnv }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">执行人</span>
              <span class="meta-value">{{ selectedCase.creator }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">开始时间</span>
              <span class="meta-value">{{ startTime || '—' }}</span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" round :loading="running" :disabled="!selectedCase.id" @click="runCase">
            <el-icon><VideoPlay /></el-icon> 运行
          </el-button>
          <el-button round :disabled="!running" @click="stopRun">
            <el-icon><VideoPause /></el-icon> 停止
          </el-button>
          <el-dropdown trigger="click" @command="onMoreCommand">
            <el-button round>
              更多 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="steps">步骤编排</el-dropdown-item>
                <el-dropdown-item command="import">导入步骤</el-dropdown-item>
                <el-dropdown-item command="export">导出步骤</el-dropdown-item>
                <el-dropdown-item command="edit" divided>编辑用例</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <div class="ui-body">
      <!-- Left: case list -->
      <div class="case-panel glass-inner">
        <div class="panel-head">
          <span class="panel-title">用例列表</span>
        </div>
        <div class="search-row">
          <el-input
            v-model="keyword"
            placeholder="搜索用例名称"
            :prefix-icon="Search"
            size="default"
            clearable
          />
          <div class="filter-btn" @click="ElMessage.info('筛选功能建设中')">
            <el-icon><Filter /></el-icon>
          </div>
        </div>

        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="{ label: 'label', children: 'children' }"
          :filter-node-method="filterNode"
          default-expand-all
          node-key="id"
          highlight-current
          @node-click="onNodeClick"
          class="case-tree"
        >
          <template #default="{ data }">
            <span class="tree-node" :class="{ 'is-case': data.isCase }">
              <el-icon v-if="!data.isCase" class="folder-icon"><Folder /></el-icon>
              <span class="node-label">{{ data.label }}</span>
              <el-tag
                v-if="data.isCase"
                size="small"
                :type="caseStatusTag(data.status, data.raw?.id)"
                effect="light"
                class="node-status"
              >
                {{ caseStatusLabel(data.status, data.raw?.id) }}
              </el-tag>
              <span v-if="data.isCase || data.module" class="node-actions" @click.stop>
                <el-icon class="na-icon" @click.stop="data.isCase ? openEditCaseFor(data.raw) : openRenameModule(data.module)"><Edit /></el-icon>
                <el-icon class="na-icon na-del" @click.stop="data.isCase ? confirmDeleteCase(data.raw) : confirmDeleteModule(data.module)"><Delete /></el-icon>
              </span>
            </span>
          </template>
        </el-tree>

        <el-button type="primary" round class="new-case-btn" @click="openCreateCase">
          <el-icon><Plus /></el-icon> 新建用例
        </el-button>
      </div>

      <!-- Right: execution log -->
      <div class="log-panel glass-terminal">
        <div class="log-head">
          <span class="log-title">执行日志</span>
          <el-button text size="small" class="clear-btn" @click="clearLogs">清空日志</el-button>
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
            <p>选择用例并点击「运行」查看执行日志</p>
          </div>
        </div>
        <div class="log-foot">
          <el-checkbox v-model="autoScroll" size="small">自动滚动</el-checkbox>
          <el-button text size="small" @click="downloadLogs">
            <el-icon><Download /></el-icon> 下载日志
          </el-button>
        </div>
      </div>
    </div>

    <!-- Steps dialog -->
    <el-dialog v-model="stepsDialog" title="步骤编排" width="720px" top="8vh">
      <div class="steps-toolbar">
        <el-button type="primary" :icon="Plus" size="small" @click="openAddStep">添加步骤</el-button>
      </div>
      <el-table :data="steps" size="small" style="width: 100%" max-height="360">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column prop="action" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="locator" label="元素定位" min-width="160" />
        <el-table-column prop="value" label="操作值" min-width="120" />
        <el-table-column prop="desc" label="断言 / 说明" min-width="140" />
        <el-table-column label="" width="50">
          <template #default="{ $index }">
            <el-icon class="del-icon" @click="removeStep($index)"><Delete /></el-icon>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!steps.length" description="暂无步骤" :image-size="60" />
    </el-dialog>

    <!-- Add step dialog -->
    <el-dialog v-model="stepDialog" title="添加步骤" width="480px">
      <el-form :model="stepForm" label-width="90px">
        <el-form-item label="操作类型">
          <el-select v-model="stepForm.action" style="width: 100%">
            <el-option v-for="a in actions" :key="a" :label="a" :value="a" />
          </el-select>
        </el-form-item>
        <el-form-item label="元素定位"><el-input v-model="stepForm.locator" placeholder="如：id=username" /></el-form-item>
        <el-form-item label="操作值"><el-input v-model="stepForm.value" placeholder="如：test_admin" /></el-form-item>
        <el-form-item label="说明"><el-input v-model="stepForm.desc" placeholder="断言 / 说明" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stepDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="addStep">添加</el-button>
      </template>
    </el-dialog>

    <!-- Import dialog -->
    <el-dialog v-model="importDialog" title="导入步骤（JSON）" width="520px">
      <el-input v-model="importText" type="textarea" :rows="10" placeholder='[{"action":"点击","locator":"id=btn","value":"","desc":"说明"}]' />
      <template #footer>
        <el-button @click="importDialog = false">取消</el-button>
        <el-button type="primary" @click="importSteps">导入</el-button>
      </template>
    </el-dialog>

    <!-- Edit case dialog -->
    <el-dialog v-model="caseDialog" :title="caseDialogTitle" width="480px">
      <el-form :model="caseForm" label-width="90px">
        <el-form-item label="用例名称"><el-input v-model="caseForm.name" /></el-form-item>
        <el-form-item label="所属模块"><el-input v-model="caseForm.module" /></el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="caseForm.priority" style="width: 100%">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="浏览器">
          <el-select v-model="caseForm.browser" style="width: 100%">
            <el-option label="Chrome" value="Chrome" />
            <el-option label="Firefox" value="Firefox" />
            <el-option label="Edge" value="Edge" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="caseDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveCase">保存</el-button>
      </template>
    </el-dialog>

    <!-- Rename module dialog -->
    <el-dialog v-model="moduleDialog" title="重命名模块" width="420px">
      <el-form label-width="90px">
        <el-form-item label="模块名称"><el-input v-model="moduleNewName" placeholder="请输入模块名称" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitRenameModule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, Filter, Folder, EditPen, Edit, Plus, Download, Delete,
  VideoPlay, VideoPause, ArrowDown, Monitor,
} from '@element-plus/icons-vue'
import { caseApi } from '@/api'

const loading = ref(false)
const saving = ref(false)
const running = ref(false)
const keyword = ref('')
const uiCases = ref([])
const treeRef = ref()
const logRef = ref()
const steps = ref([])
const execLogs = ref([])
const terminalLines = ref([])
const autoScroll = ref(true)
const startTime = ref('')
const currentEnv = ref('测试环境')
const stepsDialog = ref(false)

const selectedCase = reactive({
  id: null, name: '', status: '', module: '', priority: '', creator: '', browser: '',
})

const actions = ['打开页面', '输入', '点击', '等待', '断言', '截图', '悬停', '选择', '滚动']

const displayStatus = computed(() => {
  if (running.value) return '运行中'
  if (selectedCase.status === '未执行') return '未开始'
  if (selectedCase.status === '已通过') return '已通过'
  if (selectedCase.status === '失败') return '失败'
  return selectedCase.status || '未开始'
})

const statusTagType = computed(() => {
  if (running.value) return 'success'
  if (selectedCase.status === '失败') return 'danger'
  if (selectedCase.status === '未执行') return 'info'
  return 'success'
})

const caseStatusLabel = (status, id) => {
  if (running.value && id === selectedCase.id) return '运行中'
  if (status === '未执行') return '未开始'
  if (status === '已通过') return '已通过'
  if (status === '失败') return '失败'
  return status
}

const caseStatusTag = (status, id) => {
  if (running.value && id === selectedCase.id) return 'success'
  if (status === '未执行') return 'info'
  if (status === '失败') return 'danger'
  return 'success'
}

const treeData = computed(() => {
  const groups = {}
  uiCases.value.forEach((c) => {
    if (!groups[c.module]) groups[c.module] = []
    groups[c.module].push({
      id: `case-${c.id}`, label: c.name, isCase: true, status: c.status, raw: c,
    })
  })
  return Object.entries(groups).map(([module, items], idx) => ({
    id: `group-${idx}`, label: module, module, children: items,
  }))
})

watch(keyword, (val) => treeRef.value?.filter(val))
const filterNode = (value, data) => !value || data.label.includes(value)

const fmtTime = () => {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

const fmtStartTime = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${fmtTime()}`
}

const pushLog = (level, levelText, message) => {
  terminalLines.value.push({ time: fmtTime(), level, levelText, message })
  if (autoScroll.value) {
    nextTick(() => {
      if (logRef.value) logRef.value.scrollTop = logRef.value.scrollHeight
    })
  }
}

const loadCase = (c) => {
  Object.assign(selectedCase, {
    id: c.id, name: c.name, status: c.status, module: c.module,
    priority: c.priority, creator: c.creator, browser: c.browser,
  })
  steps.value = (c.steps || []).map((s) => ({ ...s }))
  execLogs.value = []
  terminalLines.value = []
  startTime.value = ''
}

const onNodeClick = (data) => {
  if (data.isCase && data.raw) loadCase(data.raw)
}

const persistSteps = async () => {
  if (!selectedCase.id) return
  await caseApi.updateUiCase(selectedCase.id, {
    name: selectedCase.name, module: selectedCase.module,
    browser: selectedCase.browser, priority: selectedCase.priority,
    status: selectedCase.status, creator: selectedCase.creator,
    steps: steps.value,
  })
  await loadCases()
}

const stepDialog = ref(false)
const stepForm = reactive({ action: '点击', locator: '', value: '', desc: '' })
const openAddStep = () => {
  if (!selectedCase.id) { ElMessage.warning('请先选择一个用例'); return }
  Object.assign(stepForm, { action: '点击', locator: '', value: '', desc: '' })
  stepDialog.value = true
}
const addStep = async () => {
  steps.value.push({ ...stepForm })
  saving.value = true
  try {
    await persistSteps()
    ElMessage.success('步骤已添加')
    stepDialog.value = false
  } finally { saving.value = false }
}
const removeStep = async (index) => {
  steps.value.splice(index, 1)
  await persistSteps()
  ElMessage.success('步骤已删除')
}

const importDialog = ref(false)
const importText = ref('')
const importSteps = async () => {
  try {
    const parsed = JSON.parse(importText.value)
    if (!Array.isArray(parsed)) throw new Error()
    steps.value = parsed.map((s) => ({
      action: s.action || '点击', locator: s.locator || '',
      value: s.value || '', desc: s.desc || '',
    }))
    await persistSteps()
    ElMessage.success(`已导入 ${parsed.length} 个步骤`)
    importDialog.value = false
    importText.value = ''
  } catch { ElMessage.error('JSON 格式不正确') }
}
const exportSteps = () => {
  if (!steps.value.length) { ElMessage.warning('暂无步骤可导出'); return }
  const blob = new Blob([JSON.stringify(steps.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${selectedCase.name || 'ui-case'}-steps.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('步骤已导出')
}

const runCase = async () => {
  if (!selectedCase.id) { ElMessage.warning('请先选择一个用例'); return }
  if (!steps.value.length) { ElMessage.warning('当前用例没有步骤'); return }
  running.value = true
  startTime.value = fmtStartTime()
  terminalLines.value = []
  pushLog('info', '[INFO]', `Starting execution for case: ${selectedCase.name}`)
  pushLog('info', '[INFO]', `Browser: ${selectedCase.browser}, Env: ${currentEnv.value}`)
  try {
    const res = await caseApi.runUiCase(selectedCase.id)
    execLogs.value = res.logs
    selectedCase.status = res.status
    res.logs.forEach((log, idx) => {
      const step = steps.value[idx]
      if (step) {
        const loc = step.locator ? ` → ${step.locator}` : ''
        const val = step.value ? `, value=${step.value}` : ''
        pushLog('step', `[STEP ${idx + 1}]`, `${step.action}${loc}${val}`)
      }
      pushLog('pass', '[PASS]', log.step || '执行成功')
    })
    pushLog('info', '[INFO]', `Execution completed. Status: ${res.status}`)
    ElMessage.success(`运行完成：${res.status}`)
    await loadCases()
  } finally { running.value = false }
}

const stopRun = () => {
  running.value = false
  pushLog('info', '[INFO]', 'Execution stopped by user.')
  ElMessage.warning('已停止运行')
}

const clearLogs = () => {
  terminalLines.value = []
  execLogs.value = []
}

const downloadLogs = () => {
  if (!terminalLines.value.length) { ElMessage.warning('暂无日志'); return }
  const text = terminalLines.value.map((l) => `${l.time} ${l.levelText} ${l.message}`).join('\n')
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${selectedCase.name || 'ui-test'}-log.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const onMoreCommand = (cmd) => {
  const map = {
    steps: () => { if (!selectedCase.id) return ElMessage.warning('请先选择用例'); stepsDialog.value = true },
    import: () => { if (!selectedCase.id) return ElMessage.warning('请先选择用例'); importDialog.value = true },
    export: exportSteps,
    edit: openEditCase,
  }
  map[cmd]?.()
}

const caseDialog = ref(false)
const caseEditId = ref(null)
const editingCase = ref(null)
const caseForm = reactive({ name: '', module: '', priority: '中', browser: 'Chrome' })
const caseDialogTitle = computed(() => (caseEditId.value ? '编辑用例' : '新建用例'))

const openCreateCase = () => {
  caseEditId.value = null
  editingCase.value = null
  Object.assign(caseForm, { name: '', module: '登录模块', priority: '中', browser: 'Chrome' })
  caseDialog.value = true
}
const openEditCase = () => {
  if (!selectedCase.id) return
  caseEditId.value = selectedCase.id
  editingCase.value = { ...selectedCase, steps: steps.value }
  Object.assign(caseForm, {
    name: selectedCase.name, module: selectedCase.module,
    priority: selectedCase.priority, browser: selectedCase.browser,
  })
  caseDialog.value = true
}
const openEditCaseFor = (c) => {
  caseEditId.value = c.id
  editingCase.value = c
  Object.assign(caseForm, { name: c.name, module: c.module, priority: c.priority, browser: c.browser })
  caseDialog.value = true
}
const saveCase = async () => {
  if (!caseForm.name.trim()) { ElMessage.warning('请输入用例名称'); return }
  saving.value = true
  try {
    if (caseEditId.value) {
      const src = editingCase.value || {}
      const isCurrent = caseEditId.value === selectedCase.id
      await caseApi.updateUiCase(caseEditId.value, {
        name: caseForm.name, module: caseForm.module,
        browser: caseForm.browser, priority: caseForm.priority,
        status: src.status || '未执行', creator: src.creator || 'Admin',
        steps: isCurrent ? steps.value : (src.steps || []),
      })
      if (isCurrent) Object.assign(selectedCase, { name: caseForm.name, module: caseForm.module, priority: caseForm.priority, browser: caseForm.browser })
      ElMessage.success('用例已更新')
    } else {
      const created = await caseApi.createUiCase({
        name: caseForm.name, module: caseForm.module,
        browser: caseForm.browser, priority: caseForm.priority,
        status: '未执行', creator: 'Admin', steps: [],
      })
      ElMessage.success('用例已创建')
      await loadCases()
      loadCase(created)
      caseDialog.value = false
      return
    }
    caseDialog.value = false
    await loadCases()
  } finally { saving.value = false }
}

const confirmDeleteCase = async (c) => {
  try {
    await ElMessageBox.confirm(`确定删除用例「${c.name}」吗？`, '删除确认', { type: 'warning' })
  } catch { return }
  await caseApi.removeUiCase(c.id)
  ElMessage.success('用例已删除')
  if (selectedCase.id === c.id) {
    Object.assign(selectedCase, { id: null, name: '', status: '', module: '', priority: '', creator: '', browser: '' })
    steps.value = []
    terminalLines.value = []
  }
  await loadCases()
}

const moduleDialog = ref(false)
const moduleOldName = ref('')
const moduleNewName = ref('')
const openRenameModule = (name) => {
  moduleOldName.value = name
  moduleNewName.value = name
  moduleDialog.value = true
}
const submitRenameModule = async () => {
  const newName = moduleNewName.value.trim()
  if (!newName) { ElMessage.warning('请输入模块名称'); return }
  if (newName === moduleOldName.value) { moduleDialog.value = false; return }
  saving.value = true
  try {
    await caseApi.renameUiModule(moduleOldName.value, newName)
    if (selectedCase.module === moduleOldName.value) selectedCase.module = newName
    ElMessage.success('模块已重命名')
    moduleDialog.value = false
    await loadCases()
  } finally { saving.value = false }
}
const confirmDeleteModule = async (name) => {
  try {
    await ElMessageBox.confirm(`确定删除模块「${name}」吗？`, '删除确认', { type: 'warning' })
  } catch { return }
  await caseApi.removeUiModule(name)
  ElMessage.success('模块已删除')
  if (selectedCase.module === name) {
    Object.assign(selectedCase, { id: null, name: '', status: '', module: '', priority: '', creator: '', browser: '' })
    steps.value = []
    terminalLines.value = []
  }
  await loadCases()
}

const loadCases = async () => { uiCases.value = await caseApi.uiCases() }

onMounted(async () => {
  loading.value = true
  try {
    await loadCases()
    const loginCase = uiCases.value.find((c) => c.name === '登录功能测试') || uiCases.value[0]
    if (loginCase) loadCase(loginCase)
  } finally { loading.value = false }
})
</script>

<style scoped lang="scss">
.ui-test {
  gap: 20px;
  padding: 20px 24px;
}

.ui-body {
  flex: 1;
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 16px;
  min-height: 0;
}

.edit-icon {
  cursor: pointer;
  color: var(--text-tertiary);
  font-size: 15px;
  &:hover { color: var(--brand-primary); }
}

.case-panel {
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.panel-head {
  margin-bottom: 12px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.search-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;

  .el-input { flex: 1; }
}

.filter-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--glass-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.7);
  color: var(--text-secondary);
  flex-shrink: 0;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: all 0.2s;

  &:hover {
    color: var(--brand-primary);
    background: rgba(255, 255, 255, 0.7);
  }
}

.case-tree {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 12px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  font-size: 13px;
  padding-right: 4px;

  .folder-icon {
    color: var(--brand-primary);
    font-size: 15px;
  }

  .node-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .node-status {
    flex-shrink: 0;
    transform: scale(0.92);
  }

  .node-actions {
    margin-left: auto;
    display: none;
    align-items: center;
    gap: 6px;
  }

  &:hover .node-actions { display: flex; }

  .na-icon {
    font-size: 13px;
    color: var(--brand-primary);
    cursor: pointer;
    &:hover { opacity: 0.7; }
  }
  .na-del { color: var(--danger); }
}

.new-case-btn {
  width: 100%;
  height: 40px;
  font-size: 13px;
  font-weight: 600;
}

.log-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.log-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.log-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.clear-btn {
  color: rgba(255, 255, 255, 0.5) !important;
  font-size: 12px !important;
  &:hover { color: rgba(255, 255, 255, 0.85) !important; }
}

.log-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 18px;
  font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
  font-size: 12.5px;
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
  color: rgba(255, 255, 255, 0.82);
}

.log-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.35);
  font-size: 13px;

  p { margin: 0; }
}

.log-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);

  :deep(.el-checkbox__label) {
    color: rgba(255, 255, 255, 0.55);
    font-size: 12px;
  }

  .el-button {
    color: rgba(255, 255, 255, 0.55) !important;
    font-size: 12px !important;
    &:hover { color: rgba(255, 255, 255, 0.85) !important; }
  }
}

.steps-toolbar {
  margin-bottom: 12px;
}

.del-icon {
  cursor: pointer;
  color: var(--danger);
}
</style>
