import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled' },
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/Projects.vue'),
        meta: { title: '项目管理', icon: 'Folder' },
      },
      {
        path: 'api-test',
        name: 'ApiTest',
        component: () => import('@/views/ApiTest.vue'),
        meta: { title: 'API 测试', icon: 'Connection' },
      },
      {
        path: 'ui-test',
        name: 'UiTest',
        component: () => import('@/views/UiTest.vue'),
        meta: { title: 'UI 测试', icon: 'Monitor' },
      },
      {
        path: 'performance',
        name: 'Performance',
        component: () => import('@/views/Placeholder.vue'),
        meta: { title: '性能测试', icon: 'TrendCharts' },
      },
      {
        path: 'plans',
        name: 'Plans',
        component: () => import('@/views/Plans.vue'),
        meta: { title: '测试计划', icon: 'List' },
      },
      {
        path: 'executions',
        name: 'Executions',
        component: () => import('@/views/Placeholder.vue'),
        meta: { title: '执行记录', icon: 'VideoPlay' },
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Placeholder.vue'),
        meta: { title: '测试报告', icon: 'Document' },
      },
      {
        path: 'environments',
        name: 'Environments',
        component: () => import('@/views/Placeholder.vue'),
        meta: { title: '环境配置', icon: 'Setting' },
      },
      {
        path: 'data',
        name: 'DataManage',
        component: () => import('@/views/Placeholder.vue'),
        meta: { title: '数据管理', icon: 'Coin' },
      },
      {
        path: 'system',
        name: 'System',
        component: () => import('@/views/Placeholder.vue'),
        meta: { title: '系统管理', icon: 'Tools' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心', icon: 'User' },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    return { path: '/login' }
  }
  if (to.path === '/login' && token) {
    return { path: '/dashboard' }
  }
  document.title = to.meta.title
    ? `${to.meta.title} - AutoTest Pro`
    : 'AutoTest Pro'
  return true
})

export default router
