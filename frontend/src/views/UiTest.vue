<template>
  <div class="ui-test" v-loading="loading">
    <!-- Left: case list -->
    <div class="page-card list-panel">
      <div class="lp-head">
        <span class="section-title">用例列表</span>
        <el-icon class="add" @click="openCreateCase"><Plus /></el-icon>
      </div>
      <el-input v-model="keyword" placeholder="搜索用例名称" :prefix-icon="Search" size="small" class="lp-search" clearable />
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="{ label: 'label', children: 'children' }"
        :filter-node-method="filterNode"
        default-expand-all
        node-key="id"
        highlight-current
        @node-click="onNodeClick"
        class="ui-tree"
      >
        <template #default="{ data }">
          <span class="tree-node">
            <el-icon v-if="!data.isCase"><Folder /></el-icon>
            <el-icon v-else :color="statusColor(data.status)"><CircleCheckFilled /></el-icon>
            <span class="node-label">{{ data.label }}</span>
            <span v-if="data.isCase || data.module" class="node-actions" @click.stop>
              <el-icon
                class="na-icon"
                title="编辑"
                @click.stop="data.isCase ? openEditCaseFor(data.raw) : openRenameModule(data.module)"
              ><Edit /></el-icon>
              <el-icon
                class="na-icon na-del"
                title="删除"
                @click.stop="data.isCase ? confirmDeleteCase(data.raw) : confirmDeleteModule(data.module)"
              ><Delete /></el-icon>
            </span>
          </span>
        </template>
      </el-tree>

      <div class="tags-block">
        <div class="section-title" style="font-size: 13px">标签</div>
        <div class="tags">
          <el-tag size="small" effect="plain">管理端</el-tag>
          <el-tag size="small" effect="plain" type="success">登录</el-tag>
          <el-tag size="small" effect="plain" type="warning">高优先级</el-tag>
        </div>
      </div>
    </div>

    <!-- Center: steps -->
    <div class="center-panel">
      <div class="page-card case-head">
        <div class="ch-title">
          {{ selectedCase.name || '请选择用例' }}
          <el-tag v-if="selectedCase.id" :type="tagType(selectedCase.status)" size="small" effect="light">{{ selectedCase.status }}</el-tag>
          <el-icon v-if="selectedCase.id" class="edit" @click="openEditCase"><EditPen /></el-icon>
        </div>
        <div class="ch-meta" v-if="selectedCase.id">
          所属模块：{{ selectedCase.module }} &nbsp;·&nbsp; 优先级：{{ selectedCase.priority }} &nbsp;·&nbsp;
          创建人：{{ selectedCase.creator }} &nbsp;·&nbsp; 浏览器：{{ selectedCase.browser }}
        </div>
      </div>

      <div class="page-card steps-card">
        <div class="steps-toolbar">
          <el-button type="primary" :icon="Plus" size="small" @click="openAddStep">添加步骤</el-button>
          <el-button :icon="Upload" size="small" @click="importDialog = true">导入步骤</el-button>
          <el-button :icon="Download" size="small" @click="exportSteps">导出步骤</el-button>
          <el-button :icon="VideoPlay" size="small" type="success" style="margin-left: auto" :loading="running" @click="runCase">运行</el-button>
        </div>
        <el-table :data="steps" size="small" style="width: 100%">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="action" label="操作类型" width="100">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ row.action }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="locator" label="元素定位" min-width="160" />
          <el-table-column prop="value" label="操作值 / 数据" min-width="120" />
          <el-table-column prop="desc" label="断言 / 说明" min-width="140" />
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-icon class="del-icon" @click="removeStep($index)"><Delete /></el-icon>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!steps.length" description="暂无步骤，点击「添加步骤」开始编排" :image-size="80" />
      </div>

      <div class="page-card result-card">
        <div class="section-title" style="margin-bottom: 10px">执行结果</div>
        <el-table v-if="execLogs.length" :data="execLogs" size="small" style="width: 100%">
          <el-table-column prop="time" label="时间" width="90" />
          <el-table-column prop="step" label="步骤" />
          <el-table-column label="结果" width="80">
            <template #default="{ row }">
              <el-tag :type="row.result === '通过' ? 'success' : 'danger'" size="small" effect="light">{{ row.result }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="cost" label="耗时" width="90" />
        </el-table>
        <el-empty v-else description="点击「运行」查看执行结果" :image-size="70" />
      </div>
    </div>

    <!-- Right: element library / preview -->
    <div class="page-card preview-panel">
      <div class="section-title">元素库</div>
      <div class="element-list">
        <div class="element-item" v-for="e in elements" :key="e.id">
          <div class="el-id">{{ e.id }}</div>
          <div class="el-type">{{ e.type }}</div>
        </div>
      </div>

      <div class="section-title" style="margin-top: 18px">页面预览</div>
      <div class="preview-frame">
        <div class="mock-login">
          <div class="ml-logo">A</div>
          <div class="ml-title">欢迎登录</div>
          <div class="ml-input"></div>
          <div class="ml-input"></div>
          <div class="ml-btn">登录</div>
        </div>
      </div>
    </div>

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
      <el-input
        v-model="importText"
        type="textarea"
        :rows="10"
        placeholder='[{"action":"点击","locator":"id=btn","value":"","desc":"说明"}]'
      />
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
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Folder,
  CircleCheckFilled,
  EditPen,
  Edit,
  Plus,
  Upload,
  Download,
  VideoPlay,
  Delete,
} from '@element-plus/icons-vue'
import { caseApi } from '@/api'

const loading = ref(false)
const saving = ref(false)
const running = ref(false)
const keyword = ref('')
const uiCases = ref([])
const treeRef = ref()
const steps = ref([])
const execLogs = ref([])

const selectedCase = reactive({
  id: null, name: '', status: '', module: '', priority: '', creator: '', browser: '',
})

const actions = ['打开页面', '输入', '点击', '等待', '断言', '截图', '悬停', '选择', '滚动']

const elements = [
  { id: 'id=username', type: 'INPUT' },
  { id: 'id=password', type: 'INPUT' },
  { id: 'id=loginBtn', type: 'BUTTON' },
  { id: 'id=remember', type: 'CHECKBOX' },
  { id: 'id=homePage', type: 'DIV' },
  { id: 'id=userName', type: 'SPAN' },
]

const statusColor = (s) => (s === '失败' ? '#f0494b' : s === '未执行' ? '#c5cbd8' : '#18b566')
const tagType = (s) => (s === '失败' ? 'danger' : s === '未执行' ? 'info' : 'success')

const treeData = computed(() => {
  const groups = {}
  uiCases.value.forEach((c) => {
    if (!groups[c.module]) groups[c.module] = []
    groups[c.module].push({
      id: `case-${c.id}`, label: c.name, isCase: true, status: c.status, raw: c,
    })
  })
  const children = Object.entries(groups).map(([module, items], idx) => ({
    id: `group-${idx}`, label: `${module} (${items.length})`, module, children: items,
  }))
  return [{ id: 'all', label: `全部用例 (${uiCases.value.length})`, children }]
})

watch(keyword, (val) => treeRef.value?.filter(val))
const filterNode = (value, data) => {
  if (!value) return true
  return data.label.includes(value)
}

const loadCase = (c) => {
  Object.assign(selectedCase, {
    id: c.id, name: c.name, status: c.status, module: c.module,
    priority: c.priority, creator: c.creator, browser: c.browser,
  })
  steps.value = (c.steps || []).map((s) => ({ ...s }))
  execLogs.value = []
}

const onNodeClick = (data) => {
  if (data.isCase && data.raw) loadCase(data.raw)
}

const persistSteps = async () => {
  if (!selectedCase.id) return
  await caseApi.updateUiCase(selectedCase.id, {
    name: selectedCase.name,
    module: selectedCase.module,
    browser: selectedCase.browser,
    priority: selectedCase.priority,
    status: selectedCase.status,
    creator: selectedCase.creator,
    steps: steps.value,
  })
  await loadCases()
}

// ---- steps ----
const stepDialog = ref(false)
const stepForm = reactive({ action: '点击', locator: '', value: '', desc: '' })
const openAddStep = () => {
  if (!selectedCase.id) {
    ElMessage.warning('请先选择一个用例')
    return
  }
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
  } finally {
    saving.value = false
  }
}
const removeStep = async (index) => {
  steps.value.splice(index, 1)
  await persistSteps()
  ElMessage.success('步骤已删除')
}

// ---- import / export ----
const importDialog = ref(false)
const importText = ref('')
const importSteps = async () => {
  try {
    const parsed = JSON.parse(importText.value)
    if (!Array.isArray(parsed)) throw new Error('not array')
    steps.value = parsed.map((s) => ({
      action: s.action || '点击',
      locator: s.locator || '',
      value: s.value || '',
      desc: s.desc || '',
    }))
    await persistSteps()
    ElMessage.success(`已导入 ${parsed.length} 个步骤`)
    importDialog.value = false
    importText.value = ''
  } catch {
    ElMessage.error('JSON 格式不正确')
  }
}
const exportSteps = () => {
  if (!steps.value.length) {
    ElMessage.warning('暂无步骤可导出')
    return
  }
  const blob = new Blob([JSON.stringify(steps.value, null, 2)], {
    type: 'application/json',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${selectedCase.name || 'ui-case'}-steps.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('步骤已导出')
}

// ---- run ----
const runCase = async () => {
  if (!selectedCase.id) {
    ElMessage.warning('请先选择一个用例')
    return
  }
  if (!steps.value.length) {
    ElMessage.warning('当前用例没有步骤')
    return
  }
  running.value = true
  try {
    const res = await caseApi.runUiCase(selectedCase.id)
    execLogs.value = res.logs
    selectedCase.status = res.status
    ElMessage.success(`运行完成：${res.status}`)
    await loadCases()
  } finally {
    running.value = false
  }
}

// ---- case create/edit ----
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
  Object.assign(caseForm, {
    name: c.name, module: c.module, priority: c.priority, browser: c.browser,
  })
  caseDialog.value = true
}
const saveCase = async () => {
  if (!caseForm.name.trim()) {
    ElMessage.warning('请输入用例名称')
    return
  }
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
      if (isCurrent) {
        Object.assign(selectedCase, {
          name: caseForm.name, module: caseForm.module,
          priority: caseForm.priority, browser: caseForm.browser,
        })
      }
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
  } finally {
    saving.value = false
  }
}

const confirmDeleteCase = async (c) => {
  try {
    await ElMessageBox.confirm(`确定删除用例「${c.name}」吗？`, '删除确认', {
      type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
    })
  } catch {
    return
  }
  await caseApi.removeUiCase(c.id)
  ElMessage.success('用例已删除')
  if (selectedCase.id === c.id) {
    Object.assign(selectedCase, {
      id: null, name: '', status: '', module: '', priority: '', creator: '', browser: '',
    })
    steps.value = []
    execLogs.value = []
  }
  await loadCases()
}

// ---- module rename / delete ----
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
  if (!newName) {
    ElMessage.warning('请输入模块名称')
    return
  }
  if (newName === moduleOldName.value) {
    moduleDialog.value = false
    return
  }
  saving.value = true
  try {
    await caseApi.renameUiModule(moduleOldName.value, newName)
    if (selectedCase.module === moduleOldName.value) selectedCase.module = newName
    ElMessage.success('模块已重命名')
    moduleDialog.value = false
    await loadCases()
  } finally {
    saving.value = false
  }
}
const confirmDeleteModule = async (name) => {
  try {
    await ElMessageBox.confirm(
      `确定删除模块「${name}」吗？该模块下的所有用例都将被删除。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  await caseApi.removeUiModule(name)
  ElMessage.success('模块已删除')
  if (selectedCase.module === name) {
    Object.assign(selectedCase, {
      id: null, name: '', status: '', module: '', priority: '', creator: '', browser: '',
    })
    steps.value = []
    execLogs.value = []
  }
  await loadCases()
}

const loadCases = async () => {
  uiCases.value = await caseApi.uiCases()
}

onMounted(async () => {
  loading.value = true
  try {
    await loadCases()
    if (uiCases.value.length) loadCase(uiCases.value[0])
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.ui-test {
  display: grid;
  grid-template-columns: 260px 1fr 300px;
  gap: 14px;
  height: 100%;
}

.list-panel {
  padding: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  .lp-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .add {
      cursor: pointer;
      color: var(--brand-primary);
    }
  }
  .lp-search {
    margin: 12px 0;
  }
  .ui-tree {
    flex: 1;
    overflow-y: auto;
  }
}
.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  width: 100%;
  .node-label {
    font-size: 13px;
  }
  .node-actions {
    margin-left: auto;
    display: none;
    align-items: center;
    gap: 8px;
    padding-right: 6px;
  }
  &:hover .node-actions {
    display: flex;
  }
  .na-icon {
    font-size: 14px;
    color: var(--el-color-primary);
    cursor: pointer;
    &:hover {
      opacity: 0.7;
    }
  }
  .na-del {
    color: var(--el-color-danger);
  }
}
.tags-block {
  border-top: 1px solid var(--border-light);
  padding-top: 12px;
  .tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 10px;
  }
}

.center-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
}
.case-head {
  padding: 16px 18px;
  .ch-title {
    font-size: 17px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
    .edit {
      cursor: pointer;
      color: var(--text-secondary);
      &:hover {
        color: var(--brand-primary);
      }
    }
  }
  .ch-meta {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 8px;
  }
}
.steps-card,
.result-card {
  padding: 14px 16px;
}
.steps-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.del-icon {
  cursor: pointer;
  color: var(--danger);
}

.preview-panel {
  padding: 14px 16px;
  overflow-y: auto;
}
.element-list {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  .element-item {
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 8px 10px;
    .el-id {
      font-size: 13px;
      font-weight: 600;
    }
    .el-type {
      font-size: 11px;
      color: var(--text-secondary);
    }
  }
}
.preview-frame {
  margin-top: 12px;
  background: linear-gradient(135deg, #0d265e, #1b3a8c);
  border-radius: 10px;
  padding: 24px;
  display: flex;
  justify-content: center;
}
.mock-login {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  width: 180px;
  text-align: center;
  .ml-logo {
    width: 36px;
    height: 36px;
    margin: 0 auto 10px;
    border-radius: 9px;
    background: var(--brand-gradient);
    color: #fff;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .ml-title {
    font-weight: 700;
    margin-bottom: 14px;
    font-size: 14px;
  }
  .ml-input {
    height: 30px;
    background: #f0f2f7;
    border-radius: 6px;
    margin-bottom: 10px;
  }
  .ml-btn {
    height: 32px;
    background: var(--brand-primary);
    color: #fff;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
  }
}
</style>
