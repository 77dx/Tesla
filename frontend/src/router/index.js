import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/403',
      name: '403',
      component: () => import('@/views/ForbiddenView.vue')
    },
    {
      path: '/',
      component: () => import('@/views/LayoutView.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue')
          // 首页无需权限
        },
        {
          path: 'projects',
          name: 'projects',
          meta: { permission: 'project:list' },
          component: () => import('@/views/ProjectView.vue')
        },
        {
          path: 'projects/:id',
          name: 'project-detail',
          meta: { permission: 'project:detail' },
          component: () => import('@/views/ProjectDetailView.vue')
        },
        {
          path: 'endpoints',
          name: 'endpoints',
          meta: { permission: 'endpoint:list' },
          component: () => import('@/views/EndpointView.vue')
        },
        {
          path: 'endpoints/new',
          name: 'endpoint-new',
          meta: { permission: 'endpoint:create' },
          component: () => import('@/views/EndpointFormView.vue')
        },
        {
          path: 'endpoints/:id',
          name: 'endpoint-detail',
          meta: { permission: 'endpoint:detail' },
          component: () => import('@/views/EndpointDetailView.vue')
        },
        {
          path: 'cases',
          name: 'cases',
          meta: { permission: 'case:list' },
          component: () => import('@/views/CaseView.vue')
        },
        {
          path: 'cases/:id',
          name: 'case-detail',
          meta: { permission: 'case:detail' },
          component: () => import('@/views/CaseDetailView.vue')
        },
        {
          path: 'suites',
          name: 'suites',
          meta: { permission: 'suite:list' },
          component: () => import('@/views/SuiteView.vue')
        },
        {
          path: 'suites/new',
          name: 'suite-new',
          meta: { permission: 'suite:create' },
          component: () => import('@/views/SuiteFormView.vue')
        },
        {
          path: 'suites/:id',
          name: 'suite-detail',
          meta: { permission: 'suite:detail' },
          component: () => import('@/views/SuiteDetailView.vue')
        },
        {
          path: 'results',
          name: 'results',
          meta: { permission: 'result:list' },
          component: () => import('@/views/ResultView.vue')
        },
        {
          path: 'results/:id',
          name: 'result-detail',
          meta: { permission: 'result:detail' },
          component: () => import('@/views/ResultDetailView.vue')
        },
        {
          path: 'environments',
          name: 'environments',
          meta: { permission: 'environment:list' },
          component: () => import('@/views/EnvironmentView.vue')
        },
        {
          path: 'account',
          name: 'account',
          meta: { permission: 'user:list' },
          component: () => import('@/views/AccountView.vue')
        },
        {
          path: 'system',
          name: 'system',
          meta: { permission: 'system:manage' },
          component: () => import('@/views/SystemView.vue')
        },
        {
          path: 'product-lines',
          name: 'product-lines',
          meta: { permission: 'system:manage' },
          component: () => import('@/views/ProductLineView.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 未登录 → 跳登录页
  if (!token && to.path !== '/login') {
    return next('/login')
  }
  // 已登录访问登录页 → 跳首页
  if (token && to.path === '/login') {
    return next('/dashboard')
  }
  // 403 页无需权限检查
  if (to.path === '/403') {
    return next()
  }

  // 路由权限检查
  const requiredPermission = to.meta?.permission
  if (requiredPermission) {
    const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
    const hasPermission = permissions.includes('*') || permissions.includes(requiredPermission)
    if (!hasPermission) {
      return next('/403')
    }
  }

  next()
})

export default router
