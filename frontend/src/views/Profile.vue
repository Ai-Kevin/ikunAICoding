<template>
  <div class="profile page-shell-fill">
    <el-breadcrumb separator="/" class="page-crumb">
      <el-breadcrumb-item>个人中心</el-breadcrumb-item>
      <el-breadcrumb-item>{{ sectionTitle }}</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="profile-body">
      <!-- 左侧：用户信息 + 子导航 -->
      <aside class="profile-aside glass-inner">
        <div class="profile-hero">
          <div
            class="avatar-uploader"
            :class="{ uploading: avatarUploading }"
            title="点击更换头像"
            @click="triggerAvatarUpload"
          >
            <el-avatar :size="72" :src="avatarSrc" class="profile-avatar">
              {{ userInitial }}
            </el-avatar>
            <div class="avatar-mask">
              <el-icon :size="18"><Camera /></el-icon>
              <span>{{ avatarUploading ? '上传中...' : '更换头像' }}</span>
            </div>
            <input
              ref="avatarInputRef"
              type="file"
              class="avatar-input"
              accept="image/jpeg,image/png,image/webp,image/gif"
              @change="onAvatarSelected"
            />
          </div>
          <div class="profile-name">
            {{ displayName }}
            <el-tag size="small" type="primary" effect="light" round>{{ roleLabel }}</el-tag>
          </div>
          <div class="profile-email">{{ displayEmail }}</div>
          <div class="profile-join">加入时间：{{ profile.joinTime }}</div>
        </div>
        <nav class="profile-nav">
          <button
            v-for="item in navItems"
            :key="item.key"
            type="button"
            class="profile-nav-item"
            :class="{ active: activeSection === item.key }"
            @click="switchSection(item.key)"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </button>
        </nav>
      </aside>

      <!-- 中间：主内容 -->
      <div class="profile-main">
        <section
          v-show="activeSection === 'account' || activeSection === 'security'"
          id="section-basic"
          class="glass-inner profile-card"
        >
          <div class="card-title">基本信息</div>
          <el-form label-width="88px" class="profile-form">
            <el-form-item label="用户名">
              <el-input :model-value="displayName" readonly />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input :model-value="displayEmail" readonly />
            </el-form-item>
            <el-form-item label="手机号">
              <div class="inline-field">
                <el-input :model-value="profile.phone" readonly />
                <el-button round size="small" @click="ElMessage.info('修改手机号功能建设中')">修改</el-button>
              </div>
            </el-form-item>
            <el-form-item label="角色">
              <el-input :model-value="roleLabel" readonly />
            </el-form-item>
            <el-form-item label="所属团队">
              <el-input :model-value="profile.team" readonly />
            </el-form-item>
            <el-form-item label="个人简介">
              <el-input
                v-model="profile.bio"
                type="textarea"
                :rows="3"
                maxlength="200"
                show-word-limit
                placeholder="介绍一下你自己..."
              />
            </el-form-item>
          </el-form>
        </section>

        <section
          v-show="activeSection === 'account' || activeSection === 'security'"
          id="section-security"
          class="glass-inner profile-card"
        >
          <div class="card-title">安全设置</div>
          <div class="security-list">
            <div class="security-item">
              <div class="security-info">
                <div class="security-label">登录密码</div>
                <div class="security-desc">用于账号登录，建议定期更换</div>
              </div>
              <el-button round size="small" @click="ElMessage.info('修改密码功能建设中')">修改密码</el-button>
            </div>
            <div class="security-item">
              <div class="security-info">
                <div class="security-label">绑定邮箱</div>
                <div class="security-desc">用于接收系统通知与找回密码</div>
              </div>
              <div class="security-action">
                <span class="security-value">{{ displayEmail }}</span>
                <el-button round size="small" @click="ElMessage.info('修改邮箱功能建设中')">修改</el-button>
              </div>
            </div>
            <div class="security-item">
              <div class="security-info">
                <div class="security-label">绑定手机</div>
                <div class="security-desc">用于接收短信验证码与安全提醒</div>
              </div>
              <div class="security-action">
                <span class="security-value">{{ profile.phone }}</span>
                <el-button round size="small" @click="ElMessage.info('修改手机号功能建设中')">修改</el-button>
              </div>
            </div>
            <div class="security-item">
              <div class="security-info">
                <div class="security-label">两步验证</div>
                <div class="security-desc">开启后，登录时需验证手机或邮箱验证码</div>
              </div>
              <el-switch v-model="profile.twoFactor" />
            </div>
          </div>
        </section>

        <section
          v-show="activeSection === 'notification'"
          id="section-notification"
          class="glass-inner profile-card"
        >
          <div class="card-title">通知设置</div>
          <div class="notify-list">
            <div v-for="item in notifySettings" :key="item.key" class="notify-item">
              <div class="notify-info">
                <div class="notify-label">{{ item.label }}</div>
                <div class="notify-desc">{{ item.desc }}</div>
              </div>
              <el-switch v-model="item.enabled" />
            </div>
          </div>
        </section>

        <section
          v-show="activeSection === 'log'"
          id="section-log"
          class="glass-inner profile-card"
        >
          <div class="card-title">操作日志</div>
          <el-table :data="operationLogs" style="width: 100%">
            <el-table-column prop="time" label="时间" width="170" />
            <el-table-column prop="action" label="操作" min-width="140" />
            <el-table-column prop="ip" label="IP" width="130" />
            <el-table-column prop="result" label="结果" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="row.result === '成功' ? 'success' : 'danger'" effect="light">
                  {{ row.result }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </div>

      <!-- 右侧：最近登录 -->
      <aside
        v-show="activeSection === 'account' || activeSection === 'security'"
        class="profile-side glass-inner"
        v-loading="loginRecordsLoading"
      >
        <div class="card-title">
          最近登录记录
          <span v-if="loginRecordsPolling" class="live-dot" title="自动刷新中" />
        </div>
        <ul v-if="loginRecords.length" class="login-records">
          <li v-for="item in loginRecords" :key="item.id" class="login-record">
            <div class="record-icon" :class="item.device">
              <el-icon><component :is="item.device === 'mobile' ? 'Iphone' : 'Monitor'" /></el-icon>
            </div>
            <div class="record-body">
              <div class="record-title">
                {{ item.title }}
                <el-tag v-if="item.current" size="small" type="success" effect="light" round>本机</el-tag>
              </div>
              <div class="record-meta">{{ formatRecordTime(item.time) }}</div>
              <div class="record-location">{{ item.location }}</div>
            </div>
          </li>
        </ul>
        <el-empty v-else description="暂无登录记录" :image-size="72" />
        <el-button
          v-if="loginRecords.length < loginRecordsTotal"
          class="view-more-btn"
          round
          :loading="loginRecordsLoadingMore"
          @click="loadMoreLoginRecords"
        >
          查看更多
        </el-button>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'
import { authApi } from '@/api'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const activeSection = ref('account')
const avatarInputRef = ref(null)
const avatarUploading = ref(false)

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
const MAX_AVATAR_SIZE = 2 * 1024 * 1024

const navItems = [
  { key: 'account', label: '账号信息', icon: 'User' },
  { key: 'security', label: '安全设置', icon: 'Lock' },
  { key: 'notification', label: '通知设置', icon: 'Bell' },
  { key: 'log', label: '操作日志', icon: 'Document' },
]

const sectionTitleMap = {
  account: '账号信息',
  security: '安全设置',
  notification: '通知设置',
  log: '操作日志',
}

const sectionTitle = computed(() => sectionTitleMap[activeSection.value])

const displayName = computed(() => userStore.user?.username || 'Admin')
const displayEmail = computed(() => userStore.user?.email || 'admin@test.com')
const userInitial = computed(() => displayName.value.charAt(0).toUpperCase())
const avatarSrc = computed(() => userStore.avatarUrl)
const roleLabel = computed(() => {
  const role = userStore.user?.role || 'admin'
  return role === 'admin' ? '管理员' : role
})

const profile = reactive({
  phone: '138****8888',
  team: '测试团队',
  bio: '',
  joinTime: '2024-01-15 10:20:30',
  twoFactor: true,
})

const notifySettings = reactive([
  { key: 'exec', label: '测试执行通知', desc: '用例执行完成或失败时推送消息', enabled: true },
  { key: 'plan', label: '计划运行通知', desc: '测试计划开始或结束时提醒', enabled: true },
  { key: 'report', label: '报告生成通知', desc: '测试报告生成后发送邮件', enabled: false },
  { key: 'system', label: '系统公告', desc: '平台维护与版本更新通知', enabled: true },
])

const loginRecords = ref([])
const loginRecordsTotal = ref(0)
const loginRecordsLimit = ref(10)
const loginRecordsLoading = ref(false)
const loginRecordsLoadingMore = ref(false)
const loginRecordsPolling = ref(false)

const LOGIN_RECORDS_POLL_MS = 15000
let loginRecordsPollTimer = null

const formatRecordTime = (value) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}

const fetchLoginRecords = async ({ silent = false, append = false } = {}) => {
  if (silent) {
    loginRecordsPolling.value = true
  } else if (append) {
    loginRecordsLoadingMore.value = true
  } else {
    loginRecordsLoading.value = true
  }

  try {
    const res = await authApi.loginRecords({
      limit: loginRecordsLimit.value,
      offset: 0,
      session_id: localStorage.getItem('session_id') || undefined,
    })
    loginRecords.value = res.items
    loginRecordsTotal.value = res.total
  } catch {
    if (!silent) {
      loginRecords.value = []
      loginRecordsTotal.value = 0
    }
  } finally {
    loginRecordsLoading.value = false
    loginRecordsLoadingMore.value = false
    loginRecordsPolling.value = false
  }
}

const loadMoreLoginRecords = async () => {
  loginRecordsLimit.value += 10
  await fetchLoginRecords({ append: true })
}

const startLoginRecordsPolling = () => {
  stopLoginRecordsPolling()
  loginRecordsPollTimer = window.setInterval(() => {
    fetchLoginRecords({ silent: true })
  }, LOGIN_RECORDS_POLL_MS)
}

const stopLoginRecordsPolling = () => {
  if (loginRecordsPollTimer) {
    clearInterval(loginRecordsPollTimer)
    loginRecordsPollTimer = null
  }
}

const handleVisibilityChange = () => {
  if (document.hidden) {
    stopLoginRecordsPolling()
    return
  }
  fetchLoginRecords({ silent: true })
  startLoginRecordsPolling()
}

onMounted(() => {
  fetchLoginRecords()
  startLoginRecordsPolling()
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  stopLoginRecordsPolling()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})

const operationLogs = [
  { time: '2024-05-20 10:28:15', action: '登录系统', ip: '192.168.1.105', result: '成功' },
  { time: '2024-05-20 09:42:03', action: '运行 UI 用例「登录功能测试」', ip: '192.168.1.105', result: '成功' },
  { time: '2024-05-19 16:20:44', action: '修改 API 用例「用户登录接口」', ip: '192.168.1.105', result: '成功' },
  { time: '2024-05-19 11:05:18', action: '创建测试计划「回归测试计划」', ip: '10.0.0.23', result: '成功' },
  { time: '2024-05-18 08:55:02', action: '登录系统', ip: '10.0.0.23', result: '失败' },
]

const switchSection = (key) => {
  activeSection.value = key
  if (key === 'security') {
    requestAnimationFrame(() => {
      document.getElementById('section-security')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  } else if (key === 'account') {
    requestAnimationFrame(() => {
      document.getElementById('section-basic')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }
}

const triggerAvatarUpload = () => {
  if (avatarUploading.value) return
  avatarInputRef.value?.click()
}

const onAvatarSelected = async (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return

  if (!ALLOWED_TYPES.includes(file.type)) {
    ElMessage.warning('仅支持 JPG / PNG / WebP / GIF 格式的图片')
    return
  }
  if (file.size > MAX_AVATAR_SIZE) {
    ElMessage.warning('头像文件不能超过 2MB')
    return
  }

  avatarUploading.value = true
  try {
    const user = await authApi.uploadAvatar(file)
    userStore.setUser(user)
    ElMessage.success('头像已更新')
  } catch {
    // 错误提示由 request 拦截器处理
  } finally {
    avatarUploading.value = false
  }
}
</script>

<style scoped lang="scss">
.profile {
  gap: 16px;
  padding: 20px 24px;
}

.profile-body {
  flex: 1;
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr) 300px;
  gap: 16px;
  min-height: 0;
  align-items: start;
}

.profile-aside {
  padding: 0;
  overflow: hidden;
  position: sticky;
  top: 0;
}

.profile-hero {
  padding: 28px 20px 22px;
  text-align: center;
  background: linear-gradient(
    180deg,
    rgba(0, 122, 255, 0.14) 0%,
    rgba(88, 86, 214, 0.06) 55%,
    transparent 100%
  );
  border-bottom: 1px solid rgba(255, 255, 255, 0.45);
}

.avatar-uploader {
  position: relative;
  display: inline-flex;
  cursor: pointer;
  border-radius: 50%;

  &:hover .avatar-mask {
    opacity: 1;
  }

  &.uploading {
    pointer-events: none;

    .avatar-mask {
      opacity: 1;
    }
  }
}

.avatar-input {
  display: none;
}

.avatar-mask {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: rgba(15, 23, 42, 0.48);
  color: #fff;
  font-size: 11px;
  font-weight: 500;
  opacity: 0;
  transition: opacity 0.22s ease;
}

.profile-avatar {
  background: var(--brand-gradient);
  font-size: 28px;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.28);
}

.profile-name {
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.02em;
}

.profile-email {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.profile-join {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.profile-nav {
  padding: 12px 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 42px;
  padding: 0 14px;
  border: 1px solid transparent;
  border-radius: var(--glass-radius-sm);
  background: transparent;
  color: var(--text-regular);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition:
    background 0.22s ease,
    color 0.22s ease,
    border-color 0.22s ease,
    box-shadow 0.22s ease;

  .el-icon {
    font-size: 16px;
  }

  &:hover {
    background: rgba(255, 255, 255, 0.45);
    color: var(--brand-primary);
  }

  &.active {
    background: rgba(0, 122, 255, 0.12);
    border-color: rgba(0, 122, 255, 0.18);
    color: var(--brand-primary);
    font-weight: 600;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
  }
}

.profile-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  overflow-y: auto;
  padding-right: 2px;
}

.profile-card,
.profile-side {
  padding: 20px 22px;
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: -0.01em;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #34c759;
  box-shadow: 0 0 0 0 rgba(52, 199, 89, 0.45);
  animation: live-pulse 2s ease-in-out infinite;
}

@keyframes live-pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(52, 199, 89, 0.45);
  }
  50% {
    box-shadow: 0 0 0 5px rgba(52, 199, 89, 0);
  }
}

.profile-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }

  :deep(.el-form-item__label) {
    color: var(--text-secondary);
    font-size: 13px;
  }

  :deep(.el-input__wrapper),
  :deep(.el-textarea__inner) {
    background: rgba(255, 255, 255, 0.5) !important;
  }
}

.inline-field {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;

  .el-input {
    flex: 1;
  }
}

.security-list,
.notify-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.security-item,
.notify-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.45);

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  &:first-child {
    padding-top: 0;
  }
}

.security-label,
.notify-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 4px;
}

.security-desc,
.notify-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.security-action {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.security-value {
  font-size: 13px;
  color: var(--text-regular);
  white-space: nowrap;
}

.profile-side {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
}

.login-records {
  list-style: none;
  margin: 0;
  padding: 0;
  flex: 1;
}

.login-record {
  display: flex;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.4);

  &:last-child {
    border-bottom: none;
  }
}

.record-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(0, 122, 255, 0.1);
  color: var(--brand-primary);

  &.mobile {
    background: rgba(88, 86, 214, 0.1);
    color: var(--brand-secondary);
  }
}

.record-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  line-height: 1.4;
}

.record-meta {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.record-location {
  margin-top: 2px;
  font-size: 11px;
  color: var(--text-tertiary);
}

.view-more-btn {
  width: 100%;
  margin-top: 16px;
}

@media (max-width: 1280px) {
  .profile-body {
    grid-template-columns: 248px minmax(0, 1fr);
  }

  .profile-side {
    grid-column: 1 / -1;
    position: static;
  }
}
</style>
