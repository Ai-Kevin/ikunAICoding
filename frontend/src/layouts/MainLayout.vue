<template>
  <div class="layout" :class="{ collapsed }">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-logo brand-logo">
        <div class="logo-mark">A</div>
        <div class="logo-text" v-show="!collapsed">
          <div class="logo-title">AutoTest <span class="pro">Pro</span></div>
          <div class="logo-sub">自动化测试平台</div>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="side-menu"
        :collapse="collapsed"
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

      <div class="sidebar-foot" @click="collapsed = !collapsed">
        <el-icon><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon>
        <span v-show="!collapsed">收起菜单</span>
      </div>
    </aside>

    <!-- Main -->
    <div class="main">
      <header class="topbar">
        <div class="topbar-left">
          <div class="selector">
            <span class="sel-label">当前项目</span>
            <el-select v-model="currentProject" size="default" style="width: 150px">
              <el-option label="电商平台项目" value="电商平台项目" />
              <el-option label="支付中台项目" value="支付中台项目" />
            </el-select>
          </div>
          <div class="selector">
            <span class="sel-label">环境</span>
            <el-select v-model="currentEnv" size="default" style="width: 130px">
              <el-option label="测试环境" value="测试环境" />
              <el-option label="预发环境" value="预发环境" />
              <el-option label="生产环境" value="生产环境" />
            </el-select>
          </div>
        </div>

        <div class="topbar-right">
          <el-input
            v-model="search"
            placeholder="全局搜索"
            :prefix-icon="Search"
            class="global-search"
            @keyup.enter="onSearch"
          >
            <template #suffix><span class="kbd">Ctrl + K</span></template>
          </el-input>
          <el-dropdown trigger="click">
            <el-badge :value="3" class="badge-icon">
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="n in notifications" :key="n">{{ n }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-icon :size="20" class="help-icon" @click="onHelp"><QuestionFilled /></el-icon>
          <el-dropdown @command="onUserCommand">
            <div class="user-chip">
              <el-avatar :size="30" class="user-avatar">{{
                userInitial
              }}</el-avatar>
              <span class="user-name">{{ user?.username || 'Admin' }}</span>
              <el-icon><ArrowDown /></el-icon>
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
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Bell, QuestionFilled, ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const collapsed = ref(false)
const search = ref('')
const currentProject = ref('电商平台项目')
const currentEnv = ref('测试环境')

const user = computed(() => userStore.user)
const userInitial = computed(() =>
  (user.value?.username || 'A').charAt(0).toUpperCase()
)
const activeMenu = computed(() => route.path)

const notifications = [
  '【支付接口专项测试】执行失败，成功率 85.7%',
  '回归测试计划已完成，通过率 98.3%',
  '有 3 个用例待评审',
]

const onSearch = () => {
  if (search.value.trim()) {
    ElMessage.info(`正在搜索：${search.value}`)
  }
}
const onHelp = () => {
  ElMessage.info('帮助文档建设中，可查看项目 README')
}

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
]

const onUserCommand = (cmd) => {
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
.layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  background: #fff;
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: width 0.25s;
  flex-shrink: 0;

  .layout.collapsed & {
    width: 72px;
  }
}

.sidebar-logo {
  height: 64px;
  padding: 0 18px;
  border-bottom: 1px solid var(--border-light);
  flex-shrink: 0;
}

.side-menu {
  flex: 1;
  border-right: none;
  padding: 10px;
  overflow-y: auto;

  :deep(.el-menu-item) {
    height: 46px;
    border-radius: 9px;
    margin-bottom: 4px;
    color: var(--text-regular);
    font-size: 14px;

    &:hover {
      background: #f2f5ff;
      color: var(--brand-primary);
    }

    &.is-active {
      background: var(--brand-primary);
      color: #fff;
      font-weight: 600;
      box-shadow: 0 6px 14px rgba(47, 107, 255, 0.3);
    }
  }
}

.sidebar-foot {
  height: 48px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 22px;
  border-top: 1px solid var(--border-light);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  flex-shrink: 0;
  &:hover {
    color: var(--brand-primary);
  }
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  gap: 22px;
  .selector {
    display: flex;
    align-items: center;
    gap: 8px;
    .sel-label {
      font-size: 13px;
      color: var(--text-secondary);
    }
  }
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
  .global-search {
    width: 240px;
    .kbd {
      font-size: 11px;
      color: #b3b9c7;
      border: 1px solid var(--border-light);
      border-radius: 4px;
      padding: 1px 5px;
    }
  }
  .badge-icon,
  .help-icon {
    cursor: pointer;
    color: var(--text-regular);
  }
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  .user-avatar {
    background: var(--brand-gradient);
    font-weight: 600;
  }
  .user-name {
    font-size: 14px;
    font-weight: 600;
  }
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}
</style>
