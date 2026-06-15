<template>
  <div class="page-shell projects" v-loading="loading">
    <el-breadcrumb separator="/" class="page-crumb">
      <el-breadcrumb-item>项目管理</el-breadcrumb-item>
      <el-breadcrumb-item>项目列表</el-breadcrumb-item>
      <el-breadcrumb-item>{{ project.name }}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- Project header -->
    <div class="glass-inner project-head">
      <div class="ph-left">
        <div class="ph-logo"><el-icon :size="30"><ShoppingBag /></el-icon></div>
        <div>
          <div class="ph-title">
            {{ project.name }}
            <el-tag type="success" size="small" effect="light">{{ project.status }}</el-tag>
          </div>
          <div class="ph-meta">
            项目负责人：{{ project.owner }} &nbsp;·&nbsp; 创建时间：{{ formatDate(project.created_at) }}
          </div>
          <div class="ph-desc">{{ project.description }}</div>
        </div>
      </div>
      <div class="ph-actions">
        <el-button :icon="EditPen" @click="openEditProject">编辑项目</el-button>
        <el-button :icon="User" @click="openMembers">成员管理</el-button>
        <el-button type="danger" :icon="Delete" @click="onDeleteProject">删除项目</el-button>
      </div>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="proj-tabs">
      <el-tab-pane label="项目概览" name="overview" />
      <el-tab-pane label="模块管理" name="modules" />
      <el-tab-pane label="成员权限" name="members" />
      <el-tab-pane label="关联环境" name="env" />
      <el-tab-pane label="版本管理" name="version" />
      <el-tab-pane label="最近测试报告" name="reports" />
      <el-tab-pane label="操作日志" name="logs" />
    </el-tabs>

    <!-- ============ Overview / Modules tab ============ -->
    <template v-if="activeTab === 'overview' || activeTab === 'modules'">
      <div class="glass-stat-grid" v-if="activeTab === 'overview'">
        <div class="glass-stat" v-for="(s, i) in projectStats" :key="s.label">
          <div class="stat-icon" :style="{ background: iconBg[i] }">
            <el-icon :size="20"><component :is="s.icon" /></el-icon>
          </div>
          <div>
            <div class="stat-label">{{ s.label }}</div>
            <div class="stat-value">{{ s.value }}</div>
            <div class="stat-trend">
              {{ s.trendLabel }}
              <span :class="s.trend >= 0 ? 'up' : 'down'">
                {{ s.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(s.trend) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="bottom-row" :class="{ 'bottom-row-full': activeTab === 'modules' }">
        <div class="glass-inner panel-pad module-card">
          <div class="card-head">
            <div class="section-title">模块列表</div>
            <el-button type="primary" :icon="Plus" size="small" @click="openCreateModule">新建模块</el-button>
          </div>
          <el-table :data="pagedModules" class="module-table" style="width: 100%">
            <el-table-column prop="name" label="模块名称" min-width="128" show-overflow-tooltip align="left" header-align="center">
              <template #default="{ row }">
                <span class="module-name-cell">
                  <el-icon class="module-folder-icon"><Folder /></el-icon>
                  {{ row.name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="96" align="center" header-align="center">
              <template #default="{ row }">
                <el-tag size="small" effect="plain" :type="row.type === '系统模块' ? 'warning' : row.type === '客户端' ? 'info' : ''">
                  {{ row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="用例数" align="center" header-align="center">
              <el-table-column prop="api_count" label="API" width="72" align="center" header-align="center" />
              <el-table-column prop="ui_count" label="UI" width="72" align="center" header-align="center">
                <template #default="{ row }">{{ row.ui_count || '—' }}</template>
              </el-table-column>
              <el-table-column prop="perf_count" label="性能" width="72" align="center" header-align="center" />
            </el-table-column>
            <el-table-column prop="pass_rate" label="通过率" width="88" align="center" header-align="center">
              <template #default="{ row }">
                <span class="rate">{{ row.pass_rate }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="owner" label="负责人" min-width="88" align="center" header-align="center" />
            <el-table-column prop="updated_at" label="更新时间" min-width="148" align="center" header-align="center">
              <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="160" align="center" header-align="center">
              <template #default="{ row }">
                <div class="row-link-actions">
                  <button type="button" class="glass-inline-btn primary" @click="openViewModule(row)">查看</button>
                  <button type="button" class="glass-inline-btn primary" @click="openEditModule(row)">编辑</button>
                  <button type="button" class="glass-inline-btn danger" @click="onDeleteModule(row)">删除</button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div class="table-foot">
            <span>共 {{ project.modules?.length || 0 }} 条</span>
            <el-pagination
              layout="prev, pager, next"
              :total="project.modules?.length || 0"
              :page-size="pageSize"
              :current-page="currentPage"
              @current-change="currentPage = $event"
              small
            />
          </div>
        </div>

        <div v-if="activeTab === 'overview'" class="glass-inner panel-pad info-card">
          <div class="section-title">项目信息</div>
          <div class="info-list">
            <div class="info-item"><span>项目ID：</span>{{ project.code }}</div>
            <div class="info-item"><span>所属团队：</span>{{ project.dept }}</div>
            <div class="info-item"><span>项目类型：</span>{{ project.project_type }}</div>
            <div class="info-item"><span>当前版本：</span>{{ project.version }}</div>
            <div class="info-item">
              <span>Git 仓库：</span>
              <a class="git-link" :href="project.git_repo" target="_blank">{{ project.git_repo }}</a>
            </div>
          </div>

          <div class="section-title" style="margin-top: 22px">关联环境</div>
          <div class="env-list">
            <div class="env-item"><span class="dot green"></span> 测试环境 <em>https://test.ecommerce.com</em></div>
            <div class="env-item"><span class="dot blue"></span> 预发环境 <em>https://pre.ecommerce.com</em></div>
            <div class="env-item"><span class="dot gray"></span> 生产环境 (只读) <em>https://www.ecommerce.com</em></div>
          </div>

          <div class="section-title" style="margin-top: 22px">最近测试报告</div>
          <div class="report-list">
            <div class="report-item" v-for="r in reports" :key="r.name">
              <div>
                <div class="r-name">{{ r.name }}</div>
                <div class="r-time">{{ r.time }}</div>
              </div>
              <el-tag :type="r.status === '成功' ? 'success' : 'danger'" size="small" effect="light">{{ r.status }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ============ Members tab ============ -->
    <div v-else-if="activeTab === 'members'" class="glass-inner panel-pad tab-panel">
      <div class="card-head">
        <div class="section-title">成员权限</div>
        <el-button type="primary" :icon="Plus" size="small" @click="openMembers">管理成员</el-button>
      </div>
      <el-table :data="members" style="width: 100%">
        <el-table-column prop="name" label="成员" min-width="120">
          <template #default="{ row }">
            <el-avatar :size="26" style="margin-right: 8px; background: var(--brand-gradient)">{{ row.name.charAt(0) }}</el-avatar>
            {{ row.name }}
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="160" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <div class="row-link-actions">
              <el-button link type="danger" size="small" @click="onRemoveMember(row)">移除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ============ Other tabs placeholder ============ -->
    <div v-else class="glass-inner panel-pad tab-panel empty-tab">
      <el-icon :size="44" color="#c5cbd8"><component :is="tabIcon" /></el-icon>
      <p>「{{ currentTabLabel }}」内容演示，可在此扩展。</p>
    </div>

    <!-- ============ Project edit dialog ============ -->
    <el-dialog v-model="projectDialog" title="编辑项目" width="560px">
      <el-form :model="projectForm" label-width="90px">
        <el-form-item label="项目名称"><el-input v-model="projectForm.name" /></el-form-item>
        <el-form-item label="项目负责人"><el-input v-model="projectForm.owner" /></el-form-item>
        <el-form-item label="所属团队"><el-input v-model="projectForm.dept" /></el-form-item>
        <el-form-item label="项目类型"><el-input v-model="projectForm.project_type" /></el-form-item>
        <el-form-item label="当前版本"><el-input v-model="projectForm.version" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="projectForm.status" style="width: 100%">
            <el-option label="进行中" value="进行中" />
            <el-option label="已暂停" value="已暂停" />
            <el-option label="已完成" value="已完成" />
          </el-select>
        </el-form-item>
        <el-form-item label="Git 仓库"><el-input v-model="projectForm.git_repo" /></el-form-item>
        <el-form-item label="项目描述"><el-input v-model="projectForm.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="projectDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProject">保存</el-button>
      </template>
    </el-dialog>

    <!-- ============ Module dialog ============ -->
    <el-dialog v-model="moduleDialog" :title="moduleDialogTitle" width="520px">
      <el-form :model="moduleForm" label-width="90px" :disabled="moduleReadonly">
        <el-form-item label="模块名称"><el-input v-model="moduleForm.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="moduleForm.type" style="width: 100%">
            <el-option label="业务模块" value="业务模块" />
            <el-option label="系统模块" value="系统模块" />
            <el-option label="客户端" value="客户端" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人"><el-input v-model="moduleForm.owner" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="8"><el-form-item label="API"><el-input-number v-model="moduleForm.api_count" :min="0" controls-position="right" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="UI"><el-input-number v-model="moduleForm.ui_count" :min="0" controls-position="right" style="width: 100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="性能"><el-input-number v-model="moduleForm.perf_count" :min="0" controls-position="right" style="width: 100%" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="通过率(%)"><el-input-number v-model="moduleForm.pass_rate" :min="0" :max="100" :precision="1" controls-position="right" style="width: 100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialog = false">{{ moduleReadonly ? '关闭' : '取消' }}</el-button>
        <el-button v-if="!moduleReadonly" type="primary" :loading="saving" @click="saveModule">保存</el-button>
      </template>
    </el-dialog>

    <!-- ============ Members dialog ============ -->
    <el-dialog v-model="membersDialog" title="成员管理" width="560px">
      <div class="member-add">
        <el-input v-model="memberForm.name" placeholder="姓名" style="width: 120px" />
        <el-input v-model="memberForm.role" placeholder="角色" style="width: 130px" />
        <el-input v-model="memberForm.email" placeholder="邮箱" style="flex: 1" />
        <el-button type="primary" :icon="Plus" @click="addMember">添加</el-button>
      </div>
      <el-table :data="members" style="width: 100%; margin-top: 14px">
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="120" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <div class="row-link-actions">
              <el-button link type="danger" size="small" @click="onRemoveMember(row)">移除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ShoppingBag,
  EditPen,
  User,
  Delete,
  Plus,
  Folder,
  Connection,
  Monitor,
  TrendCharts,
  VideoCamera,
  CircleCheck,
  Setting,
  Files,
  Document,
} from '@element-plus/icons-vue'
import { projectApi } from '@/api'

const loading = ref(false)
const saving = ref(false)
const activeTab = ref('overview')
const project = ref({ modules: [], members: [] })
const members = ref([])

const currentPage = ref(1)
const pageSize = 20

const iconBg = ['rgba(0,122,255,0.1)', 'rgba(52,199,89,0.1)', 'rgba(88,86,214,0.1)', 'rgba(255,149,0,0.1)', 'rgba(0,122,255,0.08)', 'rgba(255,59,48,0.08)']

const tabLabels = {
  env: '关联环境',
  version: '版本管理',
  reports: '最近测试报告',
  logs: '操作日志',
}
const tabIcons = { env: Setting, version: Files, reports: Document, logs: Document }
const currentTabLabel = computed(() => tabLabels[activeTab.value] || '')
const tabIcon = computed(() => tabIcons[activeTab.value] || Files)

const pagedModules = computed(() => {
  const all = project.value.modules || []
  const start = (currentPage.value - 1) * pageSize
  return all.slice(start, start + pageSize)
})

const projectStats = ref([
  { label: 'API 用例数', value: '1,284', trend: 12.5, trendLabel: '较上周', icon: Connection },
  { label: 'UI 用例数', value: '326', trend: 8.3, trendLabel: '较上周', icon: Monitor },
  { label: '性能脚本数', value: '89', trend: 5.6, trendLabel: '较上周', icon: TrendCharts },
  { label: '执行次数 (本月)', value: '156', trend: 18.7, trendLabel: '较上月', icon: VideoCamera },
  { label: '通过率 (本月)', value: '96.8%', trend: 2.3, trendLabel: '较月', icon: CircleCheck },
  { label: '缺陷数', value: '17', trend: -5.6, trendLabel: '较月', icon: EditPen },
])

const reports = [
  { name: '2024-05-28 回归测试报告', time: '2024-05-28 10:30', status: '成功' },
  { name: '2024-05-27 接口自动化测试报告', time: '2024-05-27 18:45', status: '成功' },
  { name: '2024-05-26 性能测试报告', time: '2024-05-26 16:20', status: '部分失败' },
  { name: '2024-05-25 UI 自动化测试报告', time: '2024-05-25 09:15', status: '失败' },
]

const formatDate = (d) => (d ? new Date(d).toLocaleDateString('zh-CN') : '')
const formatDateTime = (d) =>
  d
    ? new Date(d).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    : ''

// ---------- Project ----------
const projectDialog = ref(false)
const projectForm = reactive({})

const openEditProject = () => {
  Object.assign(projectForm, project.value)
  projectDialog.value = true
}
const saveProject = async () => {
  saving.value = true
  try {
    const payload = {
      name: projectForm.name,
      code: projectForm.code,
      status: projectForm.status,
      owner: projectForm.owner,
      dept: projectForm.dept,
      project_type: projectForm.project_type,
      version: projectForm.version,
      git_repo: projectForm.git_repo,
      description: projectForm.description,
    }
    await projectApi.update(project.value.id, payload)
    ElMessage.success('项目已保存')
    projectDialog.value = false
    await load()
  } finally {
    saving.value = false
  }
}
const onDeleteProject = () => {
  ElMessageBox.confirm(
    `确定要删除项目「${project.value.name}」吗？该操作不可恢复。`,
    '删除项目',
    { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' }
  ).then(async () => {
    await projectApi.remove(project.value.id)
    ElMessage.success('项目已删除')
    await load()
  }).catch(() => {})
}

// ---------- Module ----------
const moduleDialog = ref(false)
const moduleReadonly = ref(false)
const moduleEditId = ref(null)
const moduleForm = reactive({
  name: '', type: '业务模块', owner: '',
  api_count: 0, ui_count: 0, perf_count: 0, pass_rate: 100,
})
const moduleDialogTitle = computed(() =>
  moduleReadonly.value ? '模块详情' : moduleEditId.value ? '编辑模块' : '新建模块'
)
const resetModuleForm = () => Object.assign(moduleForm, {
  name: '', type: '业务模块', owner: '',
  api_count: 0, ui_count: 0, perf_count: 0, pass_rate: 100,
})
const openCreateModule = () => {
  moduleReadonly.value = false
  moduleEditId.value = null
  resetModuleForm()
  moduleDialog.value = true
}
const openEditModule = (row) => {
  moduleReadonly.value = false
  moduleEditId.value = row.id
  Object.assign(moduleForm, row)
  moduleDialog.value = true
}
const openViewModule = (row) => {
  moduleReadonly.value = true
  moduleEditId.value = row.id
  Object.assign(moduleForm, row)
  moduleDialog.value = true
}
const saveModule = async () => {
  saving.value = true
  try {
    const payload = {
      name: moduleForm.name,
      type: moduleForm.type,
      owner: moduleForm.owner,
      api_count: moduleForm.api_count,
      ui_count: moduleForm.ui_count,
      perf_count: moduleForm.perf_count,
      pass_rate: moduleForm.pass_rate,
    }
    if (moduleEditId.value) {
      await projectApi.updateModule(project.value.id, moduleEditId.value, payload)
      ElMessage.success('模块已更新')
    } else {
      await projectApi.createModule(project.value.id, payload)
      ElMessage.success('模块已创建')
    }
    moduleDialog.value = false
    await load()
  } finally {
    saving.value = false
  }
}
const onDeleteModule = (row) => {
  ElMessageBox.confirm(`确定删除模块「${row.name}」？`, '删除模块', {
    type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消',
  }).then(async () => {
    await projectApi.removeModule(project.value.id, row.id)
    ElMessage.success('模块已删除')
    await load()
  }).catch(() => {})
}

// ---------- Members ----------
const membersDialog = ref(false)
const memberForm = reactive({ name: '', role: '测试工程师', email: '' })
const openMembers = async () => {
  await loadMembers()
  membersDialog.value = true
}
const loadMembers = async () => {
  members.value = await projectApi.members(project.value.id)
}
const addMember = async () => {
  if (!memberForm.name.trim()) {
    ElMessage.warning('请输入成员姓名')
    return
  }
  await projectApi.addMember(project.value.id, { ...memberForm })
  ElMessage.success('成员已添加')
  Object.assign(memberForm, { name: '', role: '测试工程师', email: '' })
  await loadMembers()
}
const onRemoveMember = (row) => {
  ElMessageBox.confirm(`移除成员「${row.name}」？`, '移除成员', {
    type: 'warning', confirmButtonText: '确定移除', cancelButtonText: '取消',
  }).then(async () => {
    await projectApi.removeMember(project.value.id, row.id)
    ElMessage.success('成员已移除')
    await loadMembers()
  }).catch(() => {})
}

// ---------- Load ----------
const load = async () => {
  loading.value = true
  try {
    const list = await projectApi.list()
    if (list.length) {
      project.value = await projectApi.detail(list[0].id)
      members.value = project.value.members || []
    } else {
      project.value = { modules: [], members: [] }
    }
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.projects {
  gap: 14px;
}

.project-head {
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  .ph-left {
    display: flex;
    gap: 16px;
  }
  .ph-logo {
    width: 56px;
    height: 56px;
    border-radius: 14px;
    background: var(--brand-gradient);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 14px rgba(0, 122, 255, 0.25);
  }
  .ph-title {
    font-size: 18px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: -0.02em;
  }
  .ph-meta {
    font-size: 13px;
    color: var(--text-secondary);
    margin: 6px 0;
  }
  .ph-desc {
    font-size: 13px;
    color: var(--text-regular);
    max-width: 620px;
  }
  .ph-actions {
    display: flex;
    gap: 8px;
  }
}

.proj-tabs {
  margin: -4px 0 0;
  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }
}

.bottom-row {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
  min-width: 0;

  &.bottom-row-full {
    grid-template-columns: 1fr;
  }
}

.module-card {
  min-width: 0;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.module-table {
  width: 100%;

  :deep(.el-table__header-wrapper table),
  :deep(.el-table__body-wrapper table) {
    width: 100% !important;
  }

  :deep(th.el-table__cell) {
    text-align: center;
  }

  :deep(.el-table__cell) {
    padding-left: 8px;
    padding-right: 8px;
  }

  :deep(th.el-table__cell:first-child),
  :deep(td.el-table__cell:first-child) {
    padding-right: 4px;
  }

  :deep(td.el-table__cell:first-child) {
    text-align: left;
  }

  :deep(th.el-table__cell:nth-child(2)),
  :deep(td.el-table__cell:nth-child(2)) {
    padding-left: 4px;
  }
}

.module-name-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  vertical-align: middle;
}

.module-folder-icon {
  flex-shrink: 0;
  color: var(--brand-primary);
}

.rate {
  color: var(--success);
  font-weight: 600;
}

.row-link-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  white-space: nowrap;
  width: 100%;
}

.glass-inline-btn {
  height: 24px;
  padding: 0 8px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(12px) saturate(170%);
  -webkit-backdrop-filter: blur(12px) saturate(170%);
  box-shadow:
    0 1px 3px rgba(15, 23, 42, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.92);
  font-size: 12px;
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition:
    background 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.15s ease;

  &.primary {
    color: #007aff;

    &:hover {
      background: rgba(0, 122, 255, 0.14);
      border-color: rgba(0, 122, 255, 0.38);
      color: #0066d6;
      box-shadow:
        0 2px 6px rgba(0, 122, 255, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }
  }

  &.danger {
    color: #ff3b30;
    border-color: rgba(255, 59, 48, 0.28);

    &:hover {
      background: rgba(255, 59, 48, 0.12);
      border-color: rgba(255, 59, 48, 0.45);
      color: #d70015;
      box-shadow:
        0 2px 6px rgba(255, 59, 48, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }
  }

  &:active {
    transform: scale(0.97);
  }
}

.row-link-actions :deep(.el-button.is-link) {
  padding: 0 4px;
  height: auto;
  min-height: unset;
  font-size: 13px;
  font-weight: 600;
  opacity: 1;
  -webkit-font-smoothing: antialiased;

  &.el-button--primary {
    color: #007aff;

    &:hover {
      color: #0066d6;
    }
  }

  &.el-button--danger {
    color: #ff3b30;

    &:hover {
      color: #d70015;
    }
  }
}

.table-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
  font-size: 13px;
  color: var(--text-secondary);
}

.empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 50px;
  color: var(--text-secondary);
}

.member-add {
  display: flex;
  gap: 10px;
  align-items: center;
}

.info-list {
  margin-top: 12px;
  .info-item {
    font-size: 13px;
    color: var(--text-main);
    padding: 7px 0;
    span {
      color: var(--text-secondary);
    }
  }
}
.git-link {
  color: var(--brand-primary);
  word-break: break-all;
}
.env-list {
  margin-top: 10px;
  .env-item {
    font-size: 13px;
    padding: 6px 0;
    em {
      display: block;
      font-style: normal;
      color: var(--text-secondary);
      font-size: 12px;
      margin-left: 16px;
    }
    .dot {
      display: inline-block;
      width: 7px;
      height: 7px;
      border-radius: 50%;
      margin-right: 8px;
      &.green { background: var(--success); box-shadow: 0 0 6px rgba(52, 199, 89, 0.5); }
      &.blue { background: var(--brand-primary); }
      &.gray { background: #94a3b8; }
    }
  }
}
.report-list {
  margin-top: 10px;
  .report-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.4);
    &:last-child { border-bottom: none; }
    .r-name {
      font-size: 13px;
      color: var(--brand-primary);
    }
    .r-time {
      font-size: 11px;
      color: var(--text-secondary);
      margin-top: 2px;
    }
  }
}
</style>
