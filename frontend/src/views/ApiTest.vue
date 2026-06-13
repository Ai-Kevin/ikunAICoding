<template>
  <div class="api-test page-shell-fill" v-loading="loading">
    <div class="page-header">
      <el-breadcrumb separator="/" class="page-crumb">
        <el-breadcrumb-item>API 测试</el-breadcrumb-item>
        <el-breadcrumb-item>接口目录</el-breadcrumb-item>
        <el-breadcrumb-item>{{ current.name || '请选择用例' }}</el-breadcrumb-item>
      </el-breadcrumb>
      <div class="header-main">
        <div>
          <div class="page-title-row">
            <h1>{{ current.name || '请选择用例' }}</h1>
            <el-tag v-if="current.id" size="small" effect="light">{{ current.method }}</el-tag>
          </div>
          <div class="meta-grid" v-if="current.id">
            <div class="meta-item">
              <span class="meta-label">请求方法</span>
              <span class="meta-value">{{ current.method }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">环境</span>
              <span class="meta-value">测试环境</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">模块</span>
              <span class="meta-value">{{ currentModule }}</span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" round :icon="Promotion" :loading="sending" @click="send">发送</el-button>
          <el-button round :icon="DocumentChecked" :loading="saving" @click="save">保存</el-button>
          <el-button round :icon="Plus" @click="openCreateCase">新建</el-button>
        </div>
      </div>
    </div>

    <div class="api-body">
    <!-- Left: interface directory -->
    <div class="glass-inner tree-panel">
      <div class="tree-head">
        <span class="section-title">接口目录</span>
        <el-icon class="add" @click="openCreateCase"><Plus /></el-icon>
      </div>
      <el-input v-model="keyword" placeholder="搜索接口/路径" :prefix-icon="Search" size="small" class="tree-search" clearable />
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="{ label: 'label', children: 'children' }"
        :filter-node-method="filterNode"
        default-expand-all
        node-key="id"
        highlight-current
        @node-click="onNodeClick"
        class="api-tree"
      >
        <template #default="{ data }">
          <span class="tree-node">
            <el-tag v-if="data.method" :type="methodType(data.method)" size="small" effect="plain" class="method-tag">
              {{ data.method }}
            </el-tag>
            <el-icon v-else><Folder /></el-icon>
            <span class="node-label">{{ data.label }}</span>
            <span class="node-actions" @click.stop>
              <el-icon
                class="na-icon"
                title="编辑"
                @click.stop="data.method ? openEditCase(data.raw) : openRenameModule(data.module)"
              ><Edit /></el-icon>
              <el-icon
                class="na-icon na-del"
                title="删除"
                @click.stop="data.method ? confirmDeleteCase(data.raw) : confirmDeleteModule(data.module)"
              ><Delete /></el-icon>
            </span>
          </span>
        </template>
      </el-tree>
    </div>

    <!-- Center: request builder -->
    <div class="center-panel">
      <div class="glass-inner req-card">
        <div class="req-tabs">
          <span class="tab active">{{ current.method }} {{ current.name }}</span>
        </div>

        <div class="url-bar">
          <el-select v-model="current.method" style="width: 100px" size="default">
            <el-option v-for="m in methods" :key="m" :label="m" :value="m" />
          </el-select>
          <el-input v-model="current.url" size="default" placeholder="请输入请求地址" />
        </div>

        <el-tabs v-model="reqTab" class="req-detail-tabs">
          <el-tab-pane name="params">
            <template #label>
              Params
              <el-badge v-if="enabledParamCount" :value="enabledParamCount" class="tab-badge" />
            </template>
          </el-tab-pane>
          <el-tab-pane name="headers">
            <template #label>
              Headers
              <el-badge v-if="enabledHeaderCount" :value="enabledHeaderCount" class="tab-badge" />
            </template>
          </el-tab-pane>
          <el-tab-pane name="body">
            <template #label>
              Body
              <el-badge v-if="hasBody" :value="1" class="tab-badge" />
            </template>
          </el-tab-pane>
          <el-tab-pane label="Auth" name="auth" />
        </el-tabs>

        <div class="body-editor">
          <div v-if="reqTab === 'body'" class="body-pane">
            <div class="body-types">
              <span
                v-for="t in bodyTypes"
                :key="t.value"
                class="bt-item"
                :class="{ active: bodyType === t.value }"
                @click="bodyType = t.value"
              >
                {{ t.label }}
              </span>
            </div>

            <div v-if="isTextBody" class="body-toolbar">
              <span class="bt-lang">{{ currentBodyLabel }}</span>
              <span class="bt-actions">
                <el-button text size="small" :icon="MagicStick" @click="formatBody">格式化</el-button>
                <el-button text size="small" :icon="CopyDocument" @click="copyBody">复制</el-button>
              </span>
            </div>

            <CodeEditor
              v-if="isTextBody"
              v-model="current.body"
              :language="bodyType"
              :placeholder="bodyPlaceholder"
            />
            <KvEditor
              v-else-if="bodyType === 'form-data' || bodyType === 'urlencoded'"
              v-model="formData"
              title="表单参数"
              value-placeholder="值"
              add-label="添加参数"
            />
            <div v-else-if="bodyType === 'binary'" class="body-empty">
              <el-icon :size="30"><Upload /></el-icon>
              <p>二进制文件请求体（演示）</p>
            </div>
            <div v-else class="body-empty">
              <el-icon :size="30"><Document /></el-icon>
              <p>该请求没有 Body</p>
            </div>
          </div>
          <KvEditor
            v-else-if="reqTab === 'headers'"
            v-model="headers"
            title="Headers"
            value-placeholder="参数值"
            add-label="添加参数"
            :hidden-count="9"
          />
          <KvEditor
            v-else-if="reqTab === 'params'"
            v-model="params"
            title="Query 参数"
            value-placeholder="参数值"
            add-label="添加参数"
          />
          <div v-else class="auth-tab">
            <el-select v-model="authType" style="width: 200px">
              <el-option label="No Auth" value="none" />
              <el-option label="Bearer Token" value="bearer" />
              <el-option label="Basic Auth" value="basic" />
            </el-select>
            <el-input v-if="authType !== 'none'" v-model="authToken" placeholder="Token / 凭证" style="margin-top: 12px" />
          </div>
        </div>
      </div>

      <div class="glass-inner assert-card">
        <div class="card-head">
          <div class="section-title">断言</div>
          <el-button size="small" :icon="Plus" @click="addAssertion">添加断言</el-button>
        </div>
        <el-table :data="assertions" size="small" style="width: 100%">
          <el-table-column label="启用" width="60">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="断言类型" width="140">
            <template #default="{ row }">
              <el-select v-model="row.type" size="small">
                <el-option label="状态码断言" value="状态码断言" />
                <el-option label="响应时间断言" value="响应时间断言" />
                <el-option label="JSON 字段断言" value="JSON 字段断言" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="断言内容">
            <template #default="{ row }"><el-input v-model="row.field" size="small" /></template>
          </el-table-column>
          <el-table-column label="期望值">
            <template #default="{ row }"><el-input v-model="row.expect" size="small" /></template>
          </el-table-column>
          <el-table-column label="实际值" width="120">
            <template #default="{ row }">{{ row.actual ?? '—' }}</template>
          </el-table-column>
          <el-table-column label="结果" width="70">
            <template #default="{ row }">
              <el-tag v-if="row.pass !== undefined && row.pass !== null" :type="row.pass ? 'success' : 'danger'" size="small" effect="light">
                {{ row.pass ? '通过' : '失败' }}
              </el-tag>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="50">
            <template #default="{ $index }">
              <el-icon class="del-icon" @click="assertions.splice($index, 1)"><Delete /></el-icon>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Right: response -->
    <div class="glass-terminal resp-panel">
      <div class="resp-head">
        <span class="section-title">响应结果</span>
        <div class="resp-meta" v-if="response">
          <el-tag :type="response.status_code < 400 ? 'success' : 'danger'" size="small" effect="dark">
            {{ response.status_code }} {{ response.status_text }}
          </el-tag>
          <span>耗时: {{ response.time_ms }}ms</span>
          <span>大小: {{ response.size }}</span>
          <el-tag v-if="response.mocked" type="warning" size="small" effect="plain">模拟</el-tag>
        </div>
      </div>
      <el-tabs v-model="respTab" class="resp-tabs">
        <el-tab-pane label="Body" name="body" />
        <el-tab-pane label="响应头" name="headers" />
        <el-tab-pane label="Cookies" name="cookies" />
      </el-tabs>
      <div class="resp-body">
        <pre v-if="!response" class="placeholder-text">点击「发送」查看响应结果</pre>
        <pre v-else-if="respTab === 'body'">{{ response.body }}</pre>
        <pre v-else-if="respTab === 'headers'">{{ prettyHeaders }}</pre>
        <pre v-else>暂无 Cookies</pre>
      </div>
    </div>
    </div>

    <!-- New / edit case dialog -->
    <el-dialog v-model="caseDialog" :title="caseForm.id ? '编辑 API 用例' : '新建 API 用例'" width="520px">
      <el-form :model="caseForm" label-width="80px">
        <el-form-item label="用例名称"><el-input v-model="caseForm.name" /></el-form-item>
        <el-form-item label="所属模块"><el-input v-model="caseForm.module" placeholder="如：用户模块" /></el-form-item>
        <el-form-item label="请求方法">
          <el-select v-model="caseForm.method" style="width: 100%">
            <el-option v-for="m in methods" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="请求地址"><el-input v-model="caseForm.url" /></el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="caseForm.priority" style="width: 100%">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="caseDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitCase">{{ caseForm.id ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>

    <!-- Rename module dialog -->
    <el-dialog v-model="moduleDialog" title="重命名模块" width="420px">
      <el-form label-width="80px">
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
  Plus,
  Search,
  Folder,
  Promotion,
  DocumentChecked,
  Delete,
  Edit,
  MagicStick,
  CopyDocument,
  Upload,
  Document,
} from '@element-plus/icons-vue'
import { caseApi } from '@/api'
import KvEditor from '@/components/KvEditor.vue'
import CodeEditor from '@/components/CodeEditor.vue'

const loading = ref(false)
const sending = ref(false)
const saving = ref(false)
const keyword = ref('')
const reqTab = ref('body')
const respTab = ref('body')
const apiCases = ref([])
const treeRef = ref()
const authType = ref('none')
const authToken = ref('')
const response = ref(null)

const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

const current = reactive({
  id: null,
  name: '请选择用例',
  method: 'POST',
  url: '{{baseUrl}}/api/v1/users/create',
  body: '',
})

const currentModule = computed(() => {
  if (!current.id) return '—'
  return apiCases.value.find((c) => c.id === current.id)?.module || '—'
})

const params = ref([])
const headers = ref([])
const assertions = ref([])

const enabledParamCount = computed(
  () => params.value.filter((p) => p.enabled && p.key).length
)
const enabledHeaderCount = computed(
  () => headers.value.filter((h) => h.enabled && h.key).length
)

const normalizeRows = (data) =>
  data.map((p) => ({
    enabled: p.enabled !== false,
    key: p.key || '',
    value: p.value ?? '',
    type: p.type || 'string',
    desc: p.desc || '',
  }))

// Params: supports JSON array (new), JSON object, or legacy "k=v&k2=v2" string
const parseParams = (raw) => {
  if (!raw) return []
  try {
    const data = JSON.parse(raw)
    if (Array.isArray(data)) return normalizeRows(data)
    if (data && typeof data === 'object') {
      return normalizeRows(Object.entries(data).map(([key, value]) => ({ key, value })))
    }
  } catch {
    return raw.split('&').filter(Boolean).map((pair) => {
      const [key, value = ''] = pair.split('=')
      return { enabled: true, key: key.trim(), value: value.trim(), type: 'string', desc: '' }
    })
  }
  return []
}

// Headers: supports JSON array (new) or JSON object (legacy / seed default)
const parseHeaders = (raw) => {
  if (!raw) return []
  try {
    const data = JSON.parse(raw)
    if (Array.isArray(data)) return normalizeRows(data)
    if (data && typeof data === 'object') {
      return normalizeRows(Object.entries(data).map(([key, value]) => ({ key, value })))
    }
  } catch {
    return []
  }
  return []
}

const serializeRows = (rows) =>
  JSON.stringify(
    rows.map((p) => ({
      enabled: p.enabled,
      key: p.key,
      value: p.value,
      type: p.type,
      desc: p.desc,
    }))
  )

const serializeParams = () => serializeRows(params.value)
const serializeHeaders = () => serializeRows(headers.value)

const buildQueryString = () =>
  params.value
    .filter((p) => p.enabled && p.key)
    .map((p) => `${encodeURIComponent(p.key)}=${encodeURIComponent(p.value)}`)
    .join('&')

// Build a JSON object string of enabled headers for the request payload
const headersToObject = () => {
  const obj = {}
  headers.value
    .filter((h) => h.enabled && h.key)
    .forEach((h) => {
      obj[h.key] = h.value
    })
  return JSON.stringify(obj)
}

// ---------------- Body ----------------
const bodyType = ref('json')
const formData = ref([])
const bodyTypes = [
  { label: 'none', value: 'none' },
  { label: 'form-data', value: 'form-data' },
  { label: 'x-www-form-urlencoded', value: 'urlencoded' },
  { label: 'JSON', value: 'json' },
  { label: 'XML', value: 'xml' },
  { label: 'Text', value: 'text' },
  { label: 'Binary', value: 'binary' },
  { label: 'GraphQL', value: 'graphql' },
  { label: 'msgpack', value: 'msgpack' },
]
const textBodyTypes = ['json', 'xml', 'text', 'graphql', 'msgpack']
const isTextBody = computed(() => textBodyTypes.includes(bodyType.value))
const currentBodyLabel = computed(
  () => bodyTypes.find((t) => t.value === bodyType.value)?.label || ''
)
const bodyPlaceholder = computed(() => {
  if (bodyType.value === 'json') return '请输入 JSON 请求体'
  if (bodyType.value === 'xml') return '请输入 XML 请求体'
  if (bodyType.value === 'graphql') return '请输入 GraphQL 查询'
  return '请输入请求体'
})
const hasBody = computed(
  () =>
    (isTextBody.value && !!current.body.trim()) ||
    ((bodyType.value === 'form-data' || bodyType.value === 'urlencoded') &&
      formData.value.some((f) => f.enabled && f.key))
)

const formatBody = () => {
  if (bodyType.value !== 'json') {
    ElMessage.info('当前类型暂不支持格式化')
    return
  }
  if (!current.body.trim()) {
    ElMessage.warning('请求体为空')
    return
  }
  try {
    current.body = JSON.stringify(JSON.parse(current.body), null, 2)
    ElMessage.success('已格式化')
  } catch {
    ElMessage.error('JSON 格式不正确，无法格式化')
  }
}

const copyBody = async () => {
  if (!current.body) {
    ElMessage.warning('请求体为空')
    return
  }
  try {
    await navigator.clipboard.writeText(current.body)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请使用 Ctrl+C')
  }
}

// Compose the actual body string for sending based on body type
const getBodyForSend = () => {
  if (bodyType.value === 'none' || bodyType.value === 'binary') return ''
  if (bodyType.value === 'urlencoded' || bodyType.value === 'form-data') {
    return formData.value
      .filter((f) => f.enabled && f.key)
      .map((f) => `${encodeURIComponent(f.key)}=${encodeURIComponent(f.value)}`)
      .join('&')
  }
  return current.body
}

const prettyHeaders = computed(() =>
  response.value ? JSON.stringify(response.value.headers, null, 2) : ''
)

const methodType = (m) => {
  const map = { GET: 'success', POST: 'warning', PUT: 'primary', DELETE: 'danger', PATCH: 'info' }
  return map[m] || 'info'
}

const treeData = computed(() => {
  const groups = {}
  apiCases.value.forEach((c) => {
    if (!groups[c.module]) groups[c.module] = []
    groups[c.module].push({
      id: `case-${c.id}`,
      label: c.name,
      method: c.method,
      raw: c,
    })
  })
  return Object.entries(groups).map(([module, children], idx) => ({
    id: `group-${idx}`,
    label: `${module} (${children.length})`,
    module,
    children,
  }))
})

watch(keyword, (val) => treeRef.value?.filter(val))
const filterNode = (value, data) => {
  if (!value) return true
  return data.label.includes(value)
}

const loadCaseIntoEditor = (c) => {
  current.id = c.id
  current.name = c.name
  current.method = c.method
  current.url = c.url
  headers.value = parseHeaders(c.headers)
  params.value = parseParams(c.params)
  current.body = c.body || ''
  try {
    assertions.value = JSON.parse(c.assertions || '[]').map((a) => ({
      enabled: a.enabled !== false,
      type: a.type || '状态码断言',
      field: a.field || '',
      expect: String(a.expect ?? ''),
      actual: null,
      pass: null,
    }))
  } catch {
    assertions.value = []
  }
  response.value = null
}

const onNodeClick = (data) => {
  if (data.raw) loadCaseIntoEditor(data.raw)
}

const addAssertion = () => {
  assertions.value.push({
    enabled: true,
    type: 'JSON 字段断言',
    field: '$.code',
    expect: '200',
    actual: null,
    pass: null,
  })
}

const send = async () => {
  sending.value = true
  try {
    const qs = buildQueryString()
    const fullUrl = qs
      ? current.url + (current.url.includes('?') ? '&' : '?') + qs
      : current.url
    const payload = {
      method: current.method,
      url: fullUrl,
      headers: headersToObject(),
      body: getBodyForSend(),
      assertions: JSON.stringify(
        assertions.value.map((a) => ({
          enabled: a.enabled,
          type: a.type,
          field: a.field,
          expect: a.expect,
        }))
      ),
    }
    const res = await caseApi.runApiCase(payload)
    response.value = res
    respTab.value = 'body'
    // map assertion results back
    res.assertions.forEach((r, i) => {
      if (assertions.value[i]) {
        assertions.value[i].actual = r.actual
        assertions.value[i].pass = r.pass
      }
    })
    ElMessage.success(`请求完成：${res.status_code} ${res.status_text}`)
  } finally {
    sending.value = false
  }
}

const save = async () => {
  if (!current.id) {
    ElMessage.warning('请先从左侧选择一个用例，或新建用例')
    return
  }
  saving.value = true
  try {
    const selected = apiCases.value.find((c) => c.id === current.id) || {}
    await caseApi.updateApiCase(current.id, {
      name: current.name === '请选择用例' ? selected.name : current.name,
      method: current.method,
      url: current.url,
      module: selected.module || '',
      priority: selected.priority || '中',
      status: selected.status || '已启用',
      tags: selected.tags || '',
      params: serializeParams(),
      headers: serializeHeaders(),
      body: current.body,
      assertions: JSON.stringify(
        assertions.value.map((a) => ({
          enabled: a.enabled,
          type: a.type,
          field: a.field,
          expect: a.expect,
        }))
      ),
    })
    ElMessage.success('用例已保存')
    await loadCases()
  } finally {
    saving.value = false
  }
}

const caseDialog = ref(false)
const caseForm = reactive({
  id: null, name: '', module: '', method: 'GET', url: '{{baseUrl}}/api/v1/', priority: '中',
})
const openCreateCase = () => {
  Object.assign(caseForm, {
    id: null, name: '', module: '', method: 'GET', url: '{{baseUrl}}/api/v1/', priority: '中',
  })
  caseDialog.value = true
}
const openEditCase = (c) => {
  Object.assign(caseForm, {
    id: c.id,
    name: c.name,
    module: c.module || '',
    method: c.method,
    url: c.url,
    priority: c.priority || '中',
  })
  caseDialog.value = true
}
const submitCase = async () => {
  if (!caseForm.name.trim()) {
    ElMessage.warning('请输入用例名称')
    return
  }
  saving.value = true
  try {
    if (caseForm.id) {
      const existing = apiCases.value.find((c) => c.id === caseForm.id) || {}
      await caseApi.updateApiCase(caseForm.id, {
        name: caseForm.name,
        module: caseForm.module || '默认模块',
        method: caseForm.method,
        url: caseForm.url,
        priority: caseForm.priority,
        status: existing.status || '已启用',
        tags: existing.tags || '',
        params: existing.params || '',
        headers: existing.headers || '',
        body: existing.body || '',
        assertions: existing.assertions || '[]',
      })
      ElMessage.success('用例已更新')
      caseDialog.value = false
      await loadCases()
      const updated = apiCases.value.find((c) => c.id === caseForm.id)
      if (updated && current.id === caseForm.id) loadCaseIntoEditor(updated)
    } else {
      const created = await caseApi.createApiCase({
        name: caseForm.name,
        module: caseForm.module || '默认模块',
        method: caseForm.method,
        url: caseForm.url,
        priority: caseForm.priority,
        status: '已启用',
        tags: '',
        headers: '{\n  "Content-Type": "application/json"\n}',
        assertions: JSON.stringify([
          { enabled: true, type: '状态码断言', field: 'Status code', expect: '200' },
        ]),
      })
      ElMessage.success('用例已创建')
      caseDialog.value = false
      await loadCases()
      loadCaseIntoEditor(created)
    }
  } finally {
    saving.value = false
  }
}

const confirmDeleteCase = async (c) => {
  try {
    await ElMessageBox.confirm(`确定删除用例「${c.name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  await caseApi.removeApiCase(c.id)
  ElMessage.success('用例已删除')
  if (current.id === c.id) {
    current.id = null
    current.name = '请选择用例'
    response.value = null
  }
  await loadCases()
}

// ---------------- Module rename / delete ----------------
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
    await caseApi.renameApiModule(moduleOldName.value, newName)
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
  const deletedIds = apiCases.value.filter((c) => c.module === name).map((c) => c.id)
  await caseApi.removeApiModule(name)
  ElMessage.success('模块已删除')
  if (deletedIds.includes(current.id)) {
    current.id = null
    current.name = '请选择用例'
    response.value = null
  }
  await loadCases()
}

const loadCases = async () => {
  apiCases.value = await caseApi.apiCases()
}

onMounted(async () => {
  loading.value = true
  try {
    await loadCases()
    const createUser = apiCases.value.find((c) => c.name === '创建用户')
    if (createUser) loadCaseIntoEditor(createUser)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.api-test {
  gap: 20px;
  padding: 20px 24px;
}

.api-body {
  flex: 1;
  display: grid;
  grid-template-columns: 240px 1fr 360px;
  gap: 14px;
  min-height: 0;
  overflow: hidden;
}

.tree-panel {
  padding: 14px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  .tree-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
    .add { cursor: pointer; color: var(--brand-primary); }
  }
  .tree-search { margin: 10px 0; }
  .api-tree { flex: 1; overflow-y: auto; }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  .method-tag {
    width: 48px;
    text-align: center;
    font-size: 10px;
    padding: 0 2px;
  }
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

.center-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
}

.req-card {
  padding: 14px 16px;
}
.req-tabs {
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid var(--border-light);
  padding-bottom: 10px;
  .tab {
    font-size: 13px;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 4px 10px;
    border-radius: 8px;
    border: 1px solid transparent;
    transition:
      color 0.25s ease,
      background 0.25s ease,
      border-color 0.25s ease,
      box-shadow 0.25s ease,
      backdrop-filter 0.25s ease;

    &:hover {
      color: var(--brand-primary);
      background: rgba(255, 255, 255, 0.65);
      backdrop-filter: blur(16px) saturate(200%);
      border-color: rgba(255, 255, 255, 0.85);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }

    &.active {
      color: var(--brand-primary);
      font-weight: 600;
    }
  }
  .tab-actions {
    margin-left: auto;
    display: flex;
    gap: 8px;
  }
}
.url-bar {
  display: flex;
  gap: 10px;
  margin: 14px 0;
}
.auth-tab {
  padding: 6px 0;
}

.body-pane {
  min-height: 220px;
}
.body-types {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 4px 0 12px;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 12px;
  .bt-item {
    font-size: 13px;
    color: var(--text-regular);
    cursor: pointer;
    position: relative;
    padding: 4px 10px;
    border-radius: 8px;
    border: 1px solid transparent;
    transition:
      color 0.25s ease,
      background 0.25s ease,
      border-color 0.25s ease,
      box-shadow 0.25s ease,
      backdrop-filter 0.25s ease;

    &:hover {
      color: var(--brand-primary);
      background: rgba(255, 255, 255, 0.65);
      backdrop-filter: blur(16px) saturate(200%);
      border-color: rgba(255, 255, 255, 0.85);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }

    &.active {
      color: var(--brand-primary);
      font-weight: 600;
      background: rgba(0, 122, 255, 0.08);
      border-color: rgba(0, 122, 255, 0.15);
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);

      &::after {
        content: '';
        position: absolute;
        left: 10px;
        right: 10px;
        bottom: 0;
        height: 2px;
        background: var(--brand-primary);
        border-radius: 1px;
      }
    }
  }
}
.body-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  .bt-lang {
    font-size: 12px;
    background: rgba(0, 122, 255, 0.12);
    color: var(--brand-primary);
    padding: 3px 12px;
    border-radius: var(--glass-radius-pill);
    font-weight: 600;
    border: 1px solid rgba(0, 122, 255, 0.15);
  }
  .bt-actions {
    display: flex;
    gap: 4px;
  }
}
.body-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 200px;
  color: var(--text-secondary);
  font-size: 13px;
}

.tab-badge {
  margin-left: 4px;
  :deep(.el-badge__content) {
    background: var(--brand-primary);
  }
}

.assert-card {
  padding: 14px 16px;
}
.del-icon {
  cursor: pointer;
  color: var(--danger);
}

.resp-panel {
  padding: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .section-title {
    color: rgba(255, 255, 255, 0.9);
  }
}
.resp-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 14px 16px 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);

  .resp-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.55);
  }
}

.resp-tabs {
  padding: 0 16px;

  :deep(.el-tabs__item) {
    color: rgba(255, 255, 255, 0.5) !important;
    &.is-active { color: #60a5fa !important; }
  }
  :deep(.el-tabs__nav-wrap::after) {
    background: rgba(255, 255, 255, 0.08) !important;
  }
}

.resp-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  margin: 0;

  pre {
    margin: 0;
    color: rgba(255, 255, 255, 0.82);
    font-family: 'SF Mono', 'Consolas', monospace;
    font-size: 12.5px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-all;
  }
  .placeholder-text {
    color: rgba(255, 255, 255, 0.35);
  }
}
</style>
