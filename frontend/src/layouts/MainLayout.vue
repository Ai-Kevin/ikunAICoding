<template>
  <div class="layout" :class="{ collapsed, 'sidebar-animating': sidebarAnimating }">
    <aside
      ref="sidebarRef"
      class="sidebar glass-panel"
      :class="{ collapsed, 'is-animating': sidebarAnimating }"
      @transitionend="onSidebarTransitionEnd"
    >
      <div class="sidebar-inner">
      <div class="sidebar-logo brand-logo">
        <img src="/logo.png?v=2" alt="AutoTest Pro" class="logo-mark" />
        <div class="logo-text sidebar-label" :class="{ 'sidebar-label--hide': collapsed }">
          <div class="logo-title">AutoTest <span class="pro">Pro</span></div>
          <div class="logo-sub">自动化测试平台</div>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="side-menu"
        :collapse="collapsed"
        :collapse-transition="false"
        router
        background-color="transparent"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-foot" @click="toggleSidebar">
        <el-icon><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon>
        <span class="sidebar-foot-text sidebar-label" :class="{ 'sidebar-label--hide': collapsed }">
          收起菜单
        </span>
      </div>
      </div>
    </aside>

    <div class="main">
      <header class="topbar glass-panel">
        <div class="topbar-left">
          <el-select v-model="currentProject" class="pill-select" style="width: 160px">
            <el-option label="电商平台项目" value="电商平台项目" />
            <el-option label="支付中台项目" value="支付中台项目" />
          </el-select>
          <div class="env-pill">
            <span class="env-dot" />
            <el-select v-model="currentEnv" class="pill-select env-select" style="width: 120px">
              <el-option label="测试环境" value="测试环境" />
              <el-option label="预发环境" value="预发环境" />
              <el-option label="生产环境" value="生产环境" />
            </el-select>
          </div>
        </div>

        <div class="topbar-right">
          <el-dropdown trigger="click">
            <el-badge :value="3" class="badge-icon">
              <div class="icon-btn"><el-icon :size="17"><Bell /></el-icon></div>
            </el-badge>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="n in notifications" :key="n">{{ n }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <div class="icon-btn" @click="onHelp">
            <el-icon :size="17"><QuestionFilled /></el-icon>
          </div>
          <el-dropdown @command="onUserCommand">
            <div class="user-chip">
              <el-avatar :size="28" :src="avatarUrl" class="user-avatar">{{ userInitial }}</el-avatar>
              <span class="user-name">{{ user?.username || 'Admin' }}</span>
              <el-icon :size="12"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="content">
        <div class="content-glass">
          <router-view />
        </div>
      </main>
    </div>

    <HelpDocDialog v-model="helpVisible" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, QuestionFilled, ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import HelpDocDialog from '@/components/HelpDocDialog.vue'

const SIDEBAR_DURATION_MS = 380

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const sidebarRef = ref(null)
const collapsed = ref(false)
const sidebarAnimating = ref(false)
const helpVisible = ref(false)
const currentProject = ref('电商平台项目')
const currentEnv = ref('测试环境')

const user = computed(() => userStore.user)
const avatarUrl = computed(() => userStore.avatarUrl)
const userInitial = computed(() =>
  (user.value?.username || 'A').charAt(0).toUpperCase()
)
const activeMenu = computed(() => route.path)

const notifications = [
  '【支付接口专项测试】执行失败，成功率 85.7%',
  '回归测试计划已完成，通过率 98.3%',
  '有 3 个用例待评审',
]

const onHelp = () => {
  helpVisible.value = true
}

const toggleSidebar = () => {
  if (sidebarAnimating.value) return

  sidebarAnimating.value = true
  clearTimeout(sidebarAnimTimer)
  collapsed.value = !collapsed.value
  sidebarAnimTimer = setTimeout(finishSidebarAnim, SIDEBAR_DURATION_MS + 80)
}

const finishSidebarAnim = () => {
  clearTimeout(blurRestoreTimer)
  blurRestoreTimer = setTimeout(() => {
    sidebarAnimating.value = false
  }, 120)
}

const onSidebarTransitionEnd = (event) => {
  if (event.target !== sidebarRef.value || event.propertyName !== 'width') return
  clearTimeout(sidebarAnimTimer)
  finishSidebarAnim()
}

let sidebarAnimTimer = null
let blurRestoreTimer = null

watch(sidebarAnimating, (active) => {
  document.body.classList.toggle('sidebar-animating', active)
})

onUnmounted(() => {
  clearTimeout(sidebarAnimTimer)
  clearTimeout(blurRestoreTimer)
  document.body.classList.remove('sidebar-animating')
})

const menuItems = [
  { path: '/dashboard', title: '首页', icon: 'HomeFilled' },
  { path: '/projects', title: '项目管理', icon: 'Folder' },
  { path: '/api-test', title: 'API 测试', icon: 'Connection' },
  { path: '/ui-test', title: 'UI 测试', icon: 'Monitor' },
  { path: '/performance', title: '性能测试', icon: 'TrendCharts' },
  { path: '/plans', title: '测试计划', icon: 'List' },
  { path: '/executions', title: '执行记录', icon: 'VideoPlay' },
  { path: '/reports', title: '测试报告', icon: 'Document' },
  { path: '/environments', title: '环境配置', icon: 'Setting' },
  { path: '/data', title: '数据管理', icon: 'Coin' },
  { path: '/system', title: '系统管理', icon: 'Tools' },
  { path: '/profile', title: '个人中心', icon: 'UserFilled' },
]

const onUserCommand = (cmd) => {
  if (cmd === 'profile') {
    router.push('/profile')
  } else if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
$sidebar-ease: cubic-bezier(0.4, 0, 0.2, 1);
$sidebar-duration: 0.38s;

.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  padding: 14px;
  gap: 14px;
}

.glass-panel {
  position: relative;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(36px) saturate(200%);
  -webkit-backdrop-filter: blur(36px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.82);
  box-shadow: var(--glass-shadow);
  transition:
    background 0.32s ease,
    backdrop-filter 0.32s ease,
    -webkit-backdrop-filter 0.32s ease;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.95) 0%,
      rgba(255, 255, 255, 0.3) 50%,
      rgba(255, 255, 255, 0.7) 100%
    );
    -webkit-mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
  }
}

.sidebar {
  width: 220px;
  border-radius: var(--glass-radius-xl);
  flex-shrink: 0;
  overflow: hidden;
  transition: width $sidebar-duration $sidebar-ease;

  &.collapsed {
    width: 72px;

    .sidebar-inner {
      width: 72px;
      min-width: 72px;
    }

    .sidebar-logo {
      justify-content: center;
      padding: 0;
      width: 100%;
    }

    .sidebar-foot {
      justify-content: center;
      padding: 0;
      gap: 0;
      width: 100%;
    }

    .side-menu {
      padding: 10px 6px;
      width: 100%;

      :deep(.el-menu--collapse) {
        width: 100%;
      }

      :deep(.el-menu-item) {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 0 !important;
        margin-left: 0;
        margin-right: 0;

        .el-icon {
          margin: 0 !important;
          position: relative;
          z-index: 1;
        }

        .el-menu-tooltip__trigger {
          position: absolute;
          inset: 0;
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 0 !important;
        }

        &:hover:not(.is-active),
        &.is-active:hover {
          transform: none;
        }
      }
    }
  }

  &.is-animating.glass-panel {
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
  }
}

.sidebar-inner {
  width: 220px;
  min-width: 220px;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: width $sidebar-duration $sidebar-ease, min-width $sidebar-duration $sidebar-ease;
}

.sidebar-label {
  overflow: hidden;
  white-space: nowrap;
  flex-shrink: 0;
  max-width: 160px;
  opacity: 1;
  transition:
    opacity 0.22s ease,
    max-width $sidebar-duration $sidebar-ease;

  &--hide {
    opacity: 0;
    max-width: 0;
    pointer-events: none;
  }
}

.sidebar-logo {
  height: 64px;
  padding: 0 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  transition: padding $sidebar-duration $sidebar-ease;
}

.logo-text {
  margin-left: 0;
}

.side-menu {
  flex: 1;
  border-right: none;
  padding: 10px 8px;
  overflow-y: auto;
  --el-menu-hover-bg-color: transparent;
  --el-menu-bg-color: transparent;
  --el-menu-active-color: var(--menu-active-color);

  :deep(.el-menu-item) {
    position: relative;
    overflow: hidden;
    height: 42px;
    border-radius: var(--glass-radius-sm);
    margin-bottom: 2px;
    color: var(--text-regular);
    font-size: 13px;
    font-weight: 500;
    letter-spacing: -0.01em;
    border: 1px solid transparent;
    background: transparent !important;
    transition:
      background 0.28s cubic-bezier(0.25, 0.46, 0.45, 0.94),
      border-color 0.28s ease,
      box-shadow 0.28s ease,
      color 0.28s ease,
      transform 0.28s ease;

    .el-icon {
      font-size: 17px;
      transition: color 0.28s ease, filter 0.28s ease;
    }

    // 玻璃折射高光（hover 时显现，非纯白铺底）
    &::before {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: inherit;
      padding: 1px;
      background: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.72) 0%,
        rgba(255, 255, 255, 0.12) 48%,
        rgba(255, 255, 255, 0.38) 100%
      );
      -webkit-mask:
        linear-gradient(#fff 0 0) content-box,
        linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      opacity: 0;
      transition: opacity 0.28s ease;
      pointer-events: none;
    }

    &::after {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: inherit;
      background: linear-gradient(
        125deg,
        rgba(255, 255, 255, 0.28) 0%,
        rgba(255, 255, 255, 0.04) 42%,
        transparent 68%
      );
      opacity: 0;
      transition: opacity 0.28s ease;
      pointer-events: none;
    }

    &:hover:not(.is-active) {
      background: rgba(255, 255, 255, 0.28) !important;
      backdrop-filter: blur(22px) saturate(195%);
      -webkit-backdrop-filter: blur(22px) saturate(195%);
      border-color: rgba(255, 255, 255, 0.52);
      color: var(--brand-primary);
      box-shadow:
        0 4px 18px rgba(0, 122, 255, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.48),
        inset 0 -1px 0 rgba(255, 255, 255, 0.12);
      transform: translateX(2px);

      &::before {
        opacity: 0.75;
      }

      &::after {
        opacity: 0.85;
      }

      .el-icon {
        filter: drop-shadow(0 0 4px rgba(0, 122, 255, 0.25));
      }
    }

    &.is-active {
      background: rgba(0, 122, 255, 0.16) !important;
      backdrop-filter: blur(24px) saturate(200%);
      -webkit-backdrop-filter: blur(24px) saturate(200%);
      color: var(--menu-active-color);
      font-weight: 600;
      border-color: rgba(0, 122, 255, 0.22);
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.75),
        0 4px 16px rgba(0, 122, 255, 0.12);

      .el-icon {
        color: var(--brand-primary);
      }

      &::before {
        opacity: 0.55;
        background: linear-gradient(
          135deg,
          rgba(255, 255, 255, 0.65) 0%,
          rgba(0, 122, 255, 0.08) 50%,
          rgba(255, 255, 255, 0.35) 100%
        );
      }
    }

    &.is-active:hover {
      background: rgba(0, 122, 255, 0.22) !important;
      border-color: rgba(0, 122, 255, 0.3);
      box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.65),
        0 6px 20px rgba(0, 122, 255, 0.14);
      transform: translateX(2px);

      &::before {
        opacity: 0.85;
      }

      &::after {
        opacity: 0.6;
      }
    }
  }
}

.sidebar-foot {
  height: 48px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.5);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  flex-shrink: 0;
  border-radius: 0 0 var(--glass-radius-xl) var(--glass-radius-xl);
  transition:
    color 0.25s ease,
    background 0.25s ease,
    padding $sidebar-duration $sidebar-ease,
    gap $sidebar-duration $sidebar-ease;
  box-sizing: border-box;

  .el-icon {
    flex-shrink: 0;
    font-size: 16px;
  }

  &:hover {
    color: var(--brand-primary);
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
  }
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  gap: 14px;
  min-width: 0;
}

.topbar {
  height: 56px;
  border-radius: var(--glass-radius-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.env-pill {
  display: flex;
  align-items: center;
  gap: 6px;
}

.env-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 6px rgba(52, 199, 89, 0.6);
  flex-shrink: 0;
}

.pill-select {
  :deep(.el-select__wrapper) {
    min-height: 34px;
    font-size: 13px;
    font-weight: 500;
  }
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-regular);
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.65);
  transition:
    background 0.28s ease,
    border-color 0.28s ease,
    box-shadow 0.28s ease,
    transform 0.28s cubic-bezier(0.25, 0.46, 0.45, 0.94),
    color 0.28s ease,
    backdrop-filter 0.28s ease;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);

  &:hover {
    background: rgba(255, 255, 255, 0.82);
    backdrop-filter: blur(24px) saturate(220%);
    -webkit-backdrop-filter: blur(24px) saturate(220%);
    border-color: rgba(255, 255, 255, 0.98);
    color: var(--brand-primary);
    box-shadow:
      0 8px 22px rgba(0, 122, 255, 0.14),
      inset 0 1px 0 rgba(255, 255, 255, 1);
    transform: translateY(-2px) scale(1.04);
  }

  &:active {
    transform: translateY(0) scale(1);
  }
}

.badge-icon {
  cursor: pointer;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  padding: 3px 12px 3px 3px;
  border-radius: var(--glass-radius-pill);
  background: rgba(255, 255, 255, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition:
    background 0.28s ease,
    border-color 0.28s ease,
    box-shadow 0.28s ease,
    transform 0.28s ease,
    backdrop-filter 0.28s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.82);
    backdrop-filter: blur(24px) saturate(220%);
    -webkit-backdrop-filter: blur(24px) saturate(220%);
    border-color: rgba(255, 255, 255, 0.98);
    box-shadow:
      0 8px 22px rgba(0, 122, 255, 0.12),
      inset 0 1px 0 rgba(255, 255, 255, 1);
    transform: translateY(-2px);
  }

  .user-avatar {
    background: var(--brand-gradient);
    font-weight: 600;
    font-size: 12px;
  }
  .user-name {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: -0.01em;
  }
}

.content {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.content-glass {
  height: 100%;
  border-radius: var(--glass-radius-xl);
  background: rgba(255, 255, 255, 0.48);
  backdrop-filter: blur(36px) saturate(200%);
  -webkit-backdrop-filter: blur(36px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.78);
  box-shadow: var(--glass-shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition:
    background 0.32s ease,
    backdrop-filter 0.32s ease,
    -webkit-backdrop-filter 0.32s ease;

  > * {
    flex: 1;
    min-height: 0;
    overflow: auto;
  }
}
</style>
