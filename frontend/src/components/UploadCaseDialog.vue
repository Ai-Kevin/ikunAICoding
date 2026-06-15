<template>
  <el-dialog
    v-model="visible"
    title="上传用例"
    width="640px"
    class="upload-case-dialog"
    :close-on-click-modal="false"
    destroy-on-close
    @closed="resetWizard"
  >
    <el-steps :active="step" align-center finish-status="success" class="upload-steps">
      <el-step title="上传文件" />
      <el-step title="解析预览" />
      <el-step title="完成" />
    </el-steps>

    <!-- Step 1 -->
    <div v-if="step === 0" class="step-panel">
      <div
        class="upload-dropzone"
        :class="{ 'is-dragover': dragOver, 'has-file': !!selectedFile }"
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @drop.prevent="onDrop"
        @click="triggerSelect"
      >
        <input
          ref="fileInputRef"
          type="file"
          accept=".py"
          class="file-input"
          @change="onFileSelected"
        />
        <div class="upload-visual">
          <div class="py-badge">PY</div>
          <div class="upload-arrow">
            <el-icon :size="22"><UploadFilled /></el-icon>
          </div>
        </div>
        <div class="upload-main-text">点击或拖拽 .py 文件到此区域上传</div>
        <div class="upload-sub-text">仅支持上传 .py 文件，单个文件大小不超过 10MB</div>
        <div class="upload-actions" @click.stop>
          <el-button type="primary" round class="select-btn" @click="triggerSelect">
            选择 .py 文件
          </el-button>
        </div>
        <div v-if="selectedFile" class="selected-file" @click.stop>
          <div class="selected-file-main">
            <div class="file-icon-wrap">
              <el-icon :size="18"><Document /></el-icon>
            </div>
            <div class="file-info">
              <div class="file-name" :title="selectedFile.name">{{ selectedFile.name }}</div>
              <div class="file-size">{{ formatSize(selectedFile.size) }}</div>
            </div>
            <button type="button" class="remove-btn" @click="clearFile">移除</button>
          </div>
        </div>
      </div>

      <div class="upload-tips">
        <div class="tips-title">上传说明</div>
        <ul>
          <li v-for="tip in uploadTips" :key="tip">
            <el-icon><CircleCheck /></el-icon>
            <span>{{ tip }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Step 2 -->
    <div v-else-if="step === 1" class="step-panel" v-loading="parsing">
      <div v-if="preview" class="preview-card glass-inner">
        <div class="preview-head">
          <div class="preview-file">
            <div class="py-badge small">PY</div>
            <div>
              <div class="preview-name">{{ preview.filename }}</div>
              <div class="preview-meta">
                {{ formatSize(preview.file_size) }} · {{ preview.line_count }} 行 · {{ preview.steps.length }} 个步骤
              </div>
            </div>
          </div>
        </div>

        <el-form :model="form" label-width="88px" class="preview-form">
          <el-form-item label="用例名称">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="所属模块">
            <el-input v-model="form.module" />
          </el-form-item>
          <el-form-item label="标签">
            <el-input v-model="form.tags" placeholder="smoke,P0" />
          </el-form-item>
          <el-form-item label="浏览器">
            <el-select v-model="form.browser" style="width: 100%">
              <el-option label="Chrome" value="Chrome" />
              <el-option label="Firefox" value="Firefox" />
              <el-option label="Edge" value="Edge" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="form.priority" style="width: 100%">
              <el-option label="高 (P0)" value="高" />
              <el-option label="中 (P1)" value="中" />
              <el-option label="低 (P2)" value="低" />
            </el-select>
          </el-form-item>
        </el-form>

        <div class="preview-section-title">脚本预览</div>
        <pre class="script-preview">{{ preview.script_preview }}</pre>

        <div class="preview-section-title">解析步骤</div>
        <el-table :data="preview.steps" size="small" max-height="180">
          <el-table-column type="index" label="#" width="44" />
          <el-table-column prop="action" label="操作" width="90" />
          <el-table-column prop="locator" label="定位" min-width="120" show-overflow-tooltip />
          <el-table-column prop="desc" label="说明" min-width="120" show-overflow-tooltip />
        </el-table>
      </div>
    </div>

    <!-- Step 3 -->
    <div v-else class="step-panel step-done">
      <div class="done-icon">
        <el-icon :size="42" color="#34c759"><CircleCheckFilled /></el-icon>
      </div>
      <h3>上传成功</h3>
      <p>用例「{{ createdCase?.name }}」已创建并保存脚本 {{ createdCase?.filename }}</p>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button round @click="handleCancel">{{ step === 2 ? '关闭' : '取消' }}</el-button>
        <el-button v-if="step === 0" type="primary" round :disabled="!canNext" @click="goParse">
          下一步
        </el-button>
        <el-button v-else-if="step === 1" round @click="step = 0">上一步</el-button>
        <el-button v-if="step === 1" type="primary" round :loading="submitting" @click="submitUpload">
          确认上传
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled, Document, CircleCheck, CircleCheckFilled,
} from '@element-plus/icons-vue'
import { caseApi } from '@/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'success'])

const MAX_SIZE = 10 * 1024 * 1024
const FILENAME_RE = /^[a-zA-Z0-9][a-zA-Z0-9_\-\.]*\.py$/

const uploadTips = [
  '仅支持 Python 脚本文件（.py）',
  '单个文件大小不超过 10MB',
  '文件编码建议为 UTF-8',
  '文件名不能包含中文、空格及特殊字符',
]

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const step = ref(0)
const dragOver = ref(false)
const selectedFile = ref(null)
const fileInputRef = ref(null)
const parsing = ref(false)
const submitting = ref(false)
const preview = ref(null)
const createdCase = ref(null)

const form = reactive({
  name: '',
  module: '',
  tags: '',
  browser: 'Chrome',
  priority: '中',
})

const canNext = computed(() => !!selectedFile.value)

const formatSize = (size) => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(2)} MB`
}

const validateFile = (file) => {
  if (!file.name.toLowerCase().endsWith('.py')) {
    ElMessage.warning('仅支持上传 .py 文件')
    return false
  }
  if (/[\u4e00-\u9fff]/.test(file.name)) {
    ElMessage.warning('文件名不能包含中文')
    return false
  }
  if (/\s/.test(file.name)) {
    ElMessage.warning('文件名不能包含空格')
    return false
  }
  if (!FILENAME_RE.test(file.name)) {
    ElMessage.warning('文件名仅允许字母、数字、下划线、连字符和点')
    return false
  }
  if (file.size > MAX_SIZE) {
    ElMessage.warning('单个文件大小不能超过 10MB')
    return false
  }
  return true
}

const setFile = (file) => {
  if (!file || !validateFile(file)) return
  selectedFile.value = file
  preview.value = null
}

const triggerSelect = () => fileInputRef.value?.click()

const onFileSelected = (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  setFile(file)
}

const onDrop = (event) => {
  dragOver.value = false
  setFile(event.dataTransfer.files?.[0])
}

const clearFile = () => {
  selectedFile.value = null
  preview.value = null
}

const goParse = async () => {
  if (!selectedFile.value) return
  parsing.value = true
  try {
    const data = await caseApi.parseUiUpload(selectedFile.value)
    preview.value = data
    Object.assign(form, {
      name: data.name,
      module: data.module,
      tags: data.tags,
      browser: data.browser,
      priority: data.priority,
    })
    step.value = 1
  } catch {
    // 错误由拦截器提示
  } finally {
    parsing.value = false
  }
}

const submitUpload = async () => {
  if (!selectedFile.value) return
  if (!form.name.trim()) {
    ElMessage.warning('请输入用例名称')
    return
  }
  submitting.value = true
  try {
    const data = await caseApi.uploadUiCase(selectedFile.value, { ...form })
    createdCase.value = data
    step.value = 2
    emit('success', data)
    ElMessage.success('用例上传成功')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  visible.value = false
}

const resetWizard = () => {
  step.value = 0
  dragOver.value = false
  selectedFile.value = null
  preview.value = null
  createdCase.value = null
  parsing.value = false
  submitting.value = false
  Object.assign(form, {
    name: '',
    module: '',
    tags: '',
    browser: 'Chrome',
    priority: '中',
  })
}
</script>

<style scoped lang="scss">
.upload-steps {
  margin-bottom: 24px;

  :deep(.el-step__title) {
    font-size: 13px;
  }
}

.step-panel {
  min-height: 320px;
}

.upload-dropzone {
  border: 1px dashed rgba(0, 122, 255, 0.35);
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(0, 122, 255, 0.06) 0%, rgba(255, 255, 255, 0.42) 100%);
  padding: 28px 24px 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;

  &.is-dragover,
  &:hover {
    border-color: rgba(0, 122, 255, 0.65);
    background: linear-gradient(180deg, rgba(0, 122, 255, 0.1) 0%, rgba(255, 255, 255, 0.55) 100%);
    box-shadow: 0 8px 24px rgba(0, 122, 255, 0.08);
  }

  &.has-file {
    padding-bottom: 20px;
  }
}

.file-input {
  display: none;
}

.upload-visual {
  position: relative;
  width: 72px;
  height: 72px;
  margin: 0 auto 16px;
}

.py-badge {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: rgba(0, 122, 255, 0.12);
  border: 1px solid rgba(0, 122, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
  color: #007aff;
  letter-spacing: 0.04em;

  &.small {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    font-size: 14px;
    flex-shrink: 0;
  }
}

.upload-arrow {
  position: absolute;
  right: -8px;
  bottom: -4px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #007aff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 16px rgba(0, 122, 255, 0.28);
}

.upload-main-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
}

.upload-sub-text {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.upload-actions {
  display: flex;
  justify-content: center;
  margin-top: 18px;
}

.select-btn {
  min-width: 148px;
  font-weight: 600;
}

.selected-file {
  width: calc(100% - 8px);
  max-width: 420px;
  margin: 14px auto 0;
}

.selected-file-main {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(0, 122, 255, 0.14);
  box-shadow: 0 4px 14px rgba(0, 122, 255, 0.06);
  text-align: left;
}

.file-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  margin-top: 2px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.3;
}

.remove-btn {
  flex-shrink: 0;
  height: 30px;
  padding: 0 14px;
  border: 1px solid rgba(255, 59, 48, 0.35);
  border-radius: 999px;
  background: #fff;
  color: #ff3b30;
  font-size: 13px;
  font-weight: 600;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;

  &:hover {
    background: rgba(255, 59, 48, 0.08);
    border-color: rgba(255, 59, 48, 0.55);
    color: #d70015;
  }
}

.upload-tips {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.38);
  border: 1px solid rgba(255, 255, 255, 0.55);

  .tips-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-main);
    margin-bottom: 10px;
  }

  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    gap: 8px;
  }

  li {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-secondary);

    .el-icon {
      color: #007aff;
      flex-shrink: 0;
    }
  }
}

.preview-card {
  padding: 16px;
}

.preview-head {
  margin-bottom: 14px;
}

.preview-file {
  display: flex;
  align-items: center;
  gap: 12px;
}

.preview-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
}

.preview-meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.preview-form {
  margin-top: 8px;

  :deep(.el-form-item) {
    margin-bottom: 14px;
  }
}

.preview-section-title {
  margin: 16px 0 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.script-preview {
  margin: 0;
  padding: 12px;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.88);
  color: rgba(255, 255, 255, 0.82);
  font-family: 'SF Mono', Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  max-height: 140px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.step-done {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 24px 12px 12px;

  h3 {
    margin: 14px 0 8px;
    font-size: 20px;
    color: var(--text-main);
  }

  p {
    margin: 0;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
