<template>
  <div class="plans" v-loading="loading">
    <div class="page-card head-card">
      <div>
        <div class="section-title" style="font-size: 18px">测试计划</div>
        <p class="sub">管理与编排自动化测试计划，可按计划批量执行用例。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openDialog">新建测试计划</el-button>
    </div>

    <div class="page-card">
      <el-table :data="plans" style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="计划名称" min-width="180" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="env" label="环境" width="110" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="light">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="success" size="small" @click="runPlan(row)">执行</el-button>
            <el-button link type="danger" size="small" @click="removePlan(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!plans.length" description="暂无测试计划，点击「新建测试计划」创建" />
    </div>

    <el-dialog v-model="dialog" title="新建测试计划" width="500px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="计划名称"><el-input v-model="form.name" placeholder="如：每日回归测试" /></el-form-item>
        <el-form-item label="计划类型">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="API / UI" value="API / UI" />
            <el-option label="API" value="API" />
            <el-option label="UI" value="UI" />
            <el-option label="性能" value="性能" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行环境">
          <el-select v-model="form.env" style="width: 100%">
            <el-option label="测试环境" value="测试环境" />
            <el-option label="预发环境" value="预发环境" />
            <el-option label="生产环境" value="生产环境" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划描述"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="create">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { planApi } from '@/api'

const loading = ref(false)
const saving = ref(false)
const plans = ref([])

const statusType = (s) =>
  s === '成功' ? 'success' : s === '失败' ? 'danger' : s === '执行中' ? 'warning' : 'info'

const formatTime = (d) => (d ? new Date(d).toLocaleString('zh-CN') : '')

const dialog = ref(false)
const form = reactive({ name: '', type: 'API / UI', env: '测试环境', description: '' })
const openDialog = () => {
  Object.assign(form, { name: '', type: 'API / UI', env: '测试环境', description: '' })
  dialog.value = true
}
const create = async () => {
  if (!form.name.trim()) {
    ElMessage.warning('请输入计划名称')
    return
  }
  saving.value = true
  try {
    await planApi.create({ ...form, status: '待执行' })
    ElMessage.success('测试计划已创建')
    dialog.value = false
    await load()
  } finally {
    saving.value = false
  }
}
const runPlan = (row) => {
  ElMessage.success(`计划「${row.name}」已加入执行队列`)
}
const removePlan = (row) => {
  ElMessageBox.confirm(`确定删除计划「${row.name}」？`, '删除测试计划', {
    type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消',
  }).then(async () => {
    await planApi.remove(row.id)
    ElMessage.success('计划已删除')
    await load()
  }).catch(() => {})
}

const load = async () => {
  loading.value = true
  try {
    plans.value = await planApi.list()
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped lang="scss">
.plans {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.head-card {
  padding: 18px 22px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  .sub {
    margin: 6px 0 0;
    color: var(--text-secondary);
    font-size: 13px;
  }
}
.page-card {
  padding: 16px 18px;
}
</style>
