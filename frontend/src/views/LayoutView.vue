<template>
  <div class="tesla-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ 'sidebar--collapsed': collapsed }">
      <!-- Logo -->
      <div class="sidebar__logo">
        <div class="logo-mark">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <path d="M14 2L4 8v12l10 6 10-6V8L14 2z" fill="#3B82F6" opacity="0.15"/>
            <path d="M14 2L4 8v12l10 6 10-6V8L14 2z" stroke="#3B82F6" stroke-width="1.5" stroke-linejoin="round"/>
            <path d="M10 14l3 3 5-6" stroke="#3B82F6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <transition name="fade">
          <div v-if="!collapsed" class="logo-text">
            <span class="logo-name">Tesla</span>
            <span class="logo-sub">测试平台</span>
          </div>
        </transition>
      </div>

      <!-- 导航菜单 -->
      <nav class="sidebar__nav">
        <div
          v-for="group in navGroups"
          :key="group.title"
          class="nav-group"
        >
          <transition name="fade">
            <div v-if="!collapsed" class="nav-group__title">{{ group.title }}</div>
          </transition>
          <div class="nav-group__items">
            <div
              v-for="item in group.items"
              :key="item.key"
              class="nav-item"
              :class="{
                'nav-item--active': isActive(item),
                'nav-item--disabled': item.permission && !hasPermission(item.permission)
              }"
              @click="handleNavClick(item)"
            >
              <div class="nav-item__indicator" />
              <component :is="item.icon" class="nav-item__icon" />
              <transition name="fade">
                <span v-if="!collapsed" class="nav-item__label">{{ item.label }}</span>
              </transition>
              <transition name="fade">
                <span
                  v-if="!collapsed && item.badge"
                  class="nav-item__badge"
                >{{ item.badge }}</span>
              </transition>
            </div>
          </div>
        </div>
      </nav>

      <!-- 侧边栏底部：版本信息 -->
      <div class="sidebar__footer">
        <div class="collapse-btn" @click="toggleCollapsed" :title="collapsed ? '展开侧边栏' : '收起侧边栏'">
          <span class="collapse-icon">{{ collapsed ? '&#9776;' : '&#10005;' }}</span>
          <transition name="fade">
            <span v-if="!collapsed" class="collapse-text">收起</span>
          </transition>
        </div>
        <transition name="fade">
          <div v-if="!collapsed" class="version-info">
            <span>Tesla v1.0</span>
          </div>
        </transition>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header__left">
          <div class="breadcrumb">
            <span class="breadcrumb__item breadcrumb__item--root">
              <component :is="currentNavIcon" class="breadcrumb__icon" />
              <span class="breadcrumb__text">{{ pageTitle }}</span>
            </span>
          </div>
        </div>

        <div class="header__right">
          <!-- 产品线切换 -->
          <div v-if="userStore.productLines.length" class="product-line">
            <a-dropdown :trigger="['click']" placement="bottomRight">
              <div class="product-line__trigger">
                <span class="product-line__dot" :style="{ background: currentPLColor }"></span>
                <span class="product-line__name">{{ userStore.currentProductLine?.name || '全部产品线' }}</span>
                <span class="product-line__arrow">&#9660;</span>
              </div>
            <template #overlay>
              <div class="dropdown-menu">
                <div
                  class="dropdown-menu__item"
                  :class="{ 'dropdown-menu__item--active': !userStore.currentProductLine }"
                  @click="userStore.currentProductLine = null"
                >
                  <span class="pl-dot" style="background: #9CA3AF"></span>
                  <span>全部产品线</span>
                  <span v-if="!userStore.currentProductLine" class="pl-check">&#10003;</span>
                </div>
                <div class="dropdown-menu__divider" v-if="userStore.productLines.length" />
                <div
                  v-for="pl in userStore.productLines"
                  :key="pl.id"
                  class="dropdown-menu__item"
                  :class="{ 'dropdown-menu__item--active': userStore.currentProductLine?.id === pl.id }"
                  @click="userStore.currentProductLine = pl"
                >
                  <span class="pl-dot" :style="{ background: getPLColor(pl.id) }"></span>
                  <span>{{ pl.name }}</span>
                  <span v-if="userStore.currentProductLine?.id === pl.id" class="pl-check">&#10003;</span>
                </div>
              </div>
            </template>
            </a-dropdown>
          </div>

          <!-- 通知 -->
          <div class="header-badge" :title="通知">
            <span class="header-badge__count" v-if="3">3</span>
            <div class="header-icon-btn">
              &#128276;
            </div>
          </div>

          <!-- 全屏 -->
          <div class="header-icon-btn" @click="toggleFullscreen" title="全屏">
            {{ isFullscreen ? '&#9974;' : '&#9975;' }}
          </div>

          <!-- 用户信息 -->
          <a-dropdown :trigger="['click']" placement="bottomRight">
            <div class="user-profile">
              <div class="user-avatar">
                <img v-if="userStore.userInfo?.avatar_url" :src="userStore.userInfo.avatar_url" alt="avatar" />
                <span v-else class="avatar-letter">{{ avatarLetter }}</span>
              </div>
              <div class="user-info">
                <span class="user-name">{{ displayName }}</span>
                <span class="user-role">{{ userStore.userInfo?.role || '测试工程师' }}</span>
              </div>
              <span class="user-arrow">&#9660;</span>
            </div>
            <template #overlay>
              <div class="user-dropdown">
                <div class="user-dropdown__item" @click="$router.push('/account')">
                  &#128100; 个人信息
                </div>
                <div class="user-dropdown__item" @click="handleLogout">
                  &#128682; 退出登录
                </div>
              </div>
            </template>
          </a-dropdown>
        </div>
      </header>

      <!-- 内容区 -->
      <main class="content">
        <router-view />
      </main>
    </div>

    <!-- 全局确认弹框 -->
    <ConfirmDialog
      :visible="confirmVisible"
      :title="confirmOptions.title"
      :message="confirmOptions.message"
      :type="confirmOptions.type"
      :confirm-text="confirmOptions.confirmText"
      :cancel-text="confirmOptions.cancelText"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
    <!-- 全局提示弹框 -->
    <AlertDialog />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import AlertDialog from '@/components/AlertDialog.vue'
import { useConfirm } from '@/composables/useConfirm'
import {
  HomeOutlined,
  FolderOutlined,
  AppstoreOutlined,
  LinkOutlined,
  FileTextOutlined,
  DesktopOutlined,
  RobotOutlined,
  AppstoreAddOutlined,
  LineChartOutlined,
  GlobalOutlined,
  ShopOutlined,
  ThunderboltOutlined,
  RocketOutlined,
  SafetyCertificateOutlined,
  UserOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 确认弹框
const { confirmVisible, confirmOptions, handleConfirm, handleCancel } = useConfirm()

// 侧边栏折叠
const collapsed = ref(false)
const isFullscreen = ref(false)

// 导航分组
const navGroups = [
  {
    title: '工作台',
    items: [
      { key: 'dashboard', label: '首页概览', icon: HomeOutlined, path: '/dashboard' },
    ]
  },
  {
    title: '测试资产',
    items: [
      { key: 'projects', label: '项目管理', icon: FolderOutlined, path: '/projects', permission: 'project:list' },
      { key: 'sprints', label: '迭代管理', icon: AppstoreOutlined, path: '/sprints', permission: 'project:list' },
      { key: 'endpoints', label: '接口管理', icon: LinkOutlined, path: '/endpoints', permission: 'endpoint:list' },
      { key: 'cases', label: '接口用例', icon: FileTextOutlined, path: '/cases', permission: 'case:list' },
      { key: 'ui-cases', label: 'UI 用例', icon: DesktopOutlined, path: '/ui-cases' },
    ]
  },
  {
    title: '执行调度',
    items: [
      { key: 'automation', label: '脚本与数据', icon: RobotOutlined, path: '/automation' },
      { key: 'suites', label: '套件管理', icon: AppstoreAddOutlined, path: '/suites', permission: 'suite:list' },
      { key: 'results', label: '执行结果', icon: LineChartOutlined, path: '/results', permission: 'result:list' },
    ]
  },
  {
    title: '配置管理',
    items: [
      { key: 'environments', label: '环境管理', icon: GlobalOutlined, path: '/environments', permission: 'environment:list' },
      { key: 'product-lines', label: '产品线', icon: ShopOutlined, path: '/product-lines', permission: 'product_line:list' },
      { key: 'performance', label: '性能测试', icon: ThunderboltOutlined, path: '/performance' },
    ]
  },
  {
    title: '系统',
    items: [
      { key: 'account', label: '个人信息', icon: UserOutlined, path: '/account', permission: 'user:list' },
      { key: 'system', label: '系统管理', icon: SettingOutlined, path: '/system', permission: 'system:manage' },
    ]
  }
]

// 当前激活的导航
const activeKey = computed(() => {
  const name = route.name
  if (!name) return 'dashboard'
  // 匹配详情页
  if (name.endsWith('-detail') || name.endsWith('-new')) {
    return name.replace('-detail', '').replace('-new', '')
  }
  return name
})

const currentNavIcon = computed(() => {
  const iconMap = {
    dashboard: HomeOutlined,
    projects: FolderOutlined,
    sprints: AppstoreOutlined,
    endpoints: LinkOutlined,
    cases: FileTextOutlined,
    'ui-cases': DesktopOutlined,
    automation: RobotOutlined,
    suites: AppstoreAddOutlined,
    results: LineChartOutlined,
    environments: GlobalOutlined,
    'product-lines': ShopOutlined,
    performance: ThunderboltOutlined,
    account: UserOutlined,
    system: SettingOutlined,
  }
  return iconMap[activeKey.value] || HomeOutlined
})

const pageTitle = computed(() => {
  const titleMap = {
    dashboard: '首页概览',
    projects: '项目管理',
    sprints: '迭代管理',
    endpoints: '接口管理',
    cases: '接口用例',
    'ui-cases': 'UI 用例',
    'ui-case-detail': 'UI 用例详情',
    'ui-case-new': '新建 UI 用例',
    suites: '套件管理',
    environments: '环境管理',
    results: '执行结果',
    'result-detail': '执行结果详情',
    'suite-detail': '套件详情',
    'suite-new': '新建套件',
    'project-detail': '项目详情',
    'project-edit': '项目管理',
    'project-new': '项目管理',
    'sprint-detail': '迭代详情',
    'endpoint-detail': '接口详情',
    'endpoint-new': '新建接口',
    'case-detail': '用例详情',
    account: '个人信息',
    system: '系统管理',
    'product-lines': '产品线管理',
    automation: '脚本与数据',
    'automation-run-detail': '执行详情',
    performance: '性能测试',
  }
  return titleMap[route.name] || 'Tesla 测试平台'
})

// 权限判断
const hasPermission = (permission) => {
  if (!permission) return true
  const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
  return permissions.includes('*') || permissions.includes(permission)
}

const isActive = (item) => {
  if (item.key === activeKey.value) return true
  // 详情页高亮
  if (item.key === 'cases' && (route.name === 'case-detail')) return true
  if (item.key === 'projects' && route.name === 'project-detail') return true
  if (item.key === 'sprints' && route.name === 'sprint-detail') return true
  if (item.key === 'suites' && (route.name === 'suite-detail' || route.name === 'suite-new')) return true
  if (item.key === 'endpoints' && (route.name === 'endpoint-detail' || route.name === 'endpoint-new')) return true
  if (item.key === 'ui-cases' && (route.name === 'ui-case-detail' || route.name === 'ui-case-new')) return true
  if (item.key === 'results' && route.name === 'result-detail') return true
  return false
}

const handleNavClick = (item) => {
  if (item['permission'] && !hasPermission(item.permission)) return
  router.push(item.path)
}

// 折叠侧边栏
const toggleCollapsed = () => {
  collapsed.value = !collapsed.value
  localStorage.setItem('sidebar-collapsed', collapsed.value)
}

// 全屏切换
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

// 登出
const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}

// 产品线切换
const handleSwitchProductLine = async ({ key }) => {
  if (key === 'all') {
    await userStore.switchProductLine(null)
  } else {
    const pl = userStore.productLines.find(p => p.id.toString() === key.toString())
    if (pl) await userStore.switchProductLine(pl)
  }
  router.go(0)
}

// 产品线颜色
const plColors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4']
const getPLColor = (id) => plColors[id % plColors.length]
const currentPLColor = computed(() => {
  if (!userStore.currentProductLine) return '#9CA3AF'
  return getPLColor(userStore.currentProductLine.id)
})

// 用户信息
const displayName = computed(() => {
  const u = userStore.userInfo
  return u?.nickname || u?.username || u?.userInfo?.username || '用户'
})

const avatarLetter = computed(() => {
  const name = displayName.value
  return name.charAt(0).toUpperCase()
})

// 初始化
onMounted(async () => {
  // 恢复侧边栏状态
  const savedCollapsed = localStorage.getItem('sidebar-collapsed')
  if (savedCollapsed) collapsed.value = savedCollapsed === 'true'

  if (userStore.access) {
    if (!userStore.userInfo) await userStore.fetchUserInfo()
    if (!userStore.productLines.length) await userStore.fetchProductLines()
  }
})
</script>

<style scoped>
/* ─── 整体布局 ─── */
.tesla-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg-page);
  font-family: var(--font-sans);
}

/* ─── 侧边栏 ─── */
.sidebar {
  width: 240px;
  min-height: 100vh;
  background: var(--color-bg-card);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
  z-index: var(--z-sticky);
}

.sidebar--collapsed {
  width: 64px;
}

/* Logo */
.sidebar__logo {
  height: 64px;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0 var(--space-5);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  overflow: hidden;
}

.logo-mark {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  white-space: nowrap;
}

.logo-name {
  font-size: var(--text-md);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.logo-sub {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  line-height: 1.2;
}

/* 导航 */
.sidebar__nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--space-4) 0;
}

.sidebar__nav::-webkit-scrollbar {
  width: 0;
}

.nav-group {
  margin-bottom: var(--space-2);
}

.nav-group__title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
  padding: var(--space-3) var(--space-5) var(--space-2);
  white-space: nowrap;
  overflow: hidden;
}

.nav-group__items {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

/* 导航项 */
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 40px;
  padding: 0 var(--space-5);
  cursor: pointer;
  position: relative;
  transition: all var(--transition-fast);
  border-radius: 0;
  overflow: hidden;
  white-space: nowrap;
}

.nav-item:hover {
  background: var(--color-bg-hover);
}

.nav-item--active {
  background: var(--color-primary-bg);
}

.nav-item--active .nav-item__label,
.nav-item--active .nav-item__icon {
  color: var(--color-primary);
}

/* 选中指示器（小圆点） */
.nav-item__indicator {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: transparent;
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  transition: all var(--transition-fast);
}

.nav-item--active .nav-item__indicator {
  height: 20px;
  background: var(--color-primary);
  border-radius: 0 2px 2px 0;
}

.nav-item__icon {
  font-size: 16px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
  width: 20px;
  text-align: center;
  transition: color var(--transition-fast);
}

.nav-item:hover .nav-item__icon {
  color: var(--color-text-primary);
}

.nav-item__label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color var(--transition-fast);
}

.nav-item:hover .nav-item__label {
  color: var(--color-text-primary);
}

.nav-item--active .nav-item__label {
  font-weight: var(--font-semibold);
}

.nav-item__badge {
  flex-shrink: 0;
}

.nav-item--disabled {
  opacity: 0.4;
  cursor: not-allowed;
  pointer-events: none;
}

/* 侧边栏底部 */
.sidebar__footer {
  flex-shrink: 0;
  padding: var(--space-4) var(--space-3);
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.collapse-btn {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
  transition: all var(--transition-fast);
  overflow: hidden;
}

.collapse-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.collapse-text {
  white-space: nowrap;
}

.version-info {
  text-align: center;
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  padding: var(--space-2);
}

/* ─── 主内容区 ─── */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ─── 顶部导航 ─── */
.header {
  height: 64px;
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-10);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  flex-shrink: 0;
}

.header__left {
  display: flex;
  align-items: center;
  gap: var(--space-6);
}

.breadcrumb__item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.breadcrumb__icon {
  font-size: 18px;
  color: var(--color-primary);
}

.breadcrumb__text {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.header__right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

/* 产品线切换 */
.product-line {
  position: relative;
}

.product-line__trigger {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--color-bg-card);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.product-line__trigger:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.product-line__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.product-line__name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-line__arrow {
  font-size: 10px;
  color: var(--color-text-tertiary);
  transition: transform var(--transition-fast);
}

/* 产品线菜单 */
.pl-menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 160px;
  padding: var(--space-2) 0;
}

.pl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pl-check {
  margin-left: auto;
  color: var(--color-primary);
  font-size: 12px;
}

/* 头部图标按钮 */
.header-icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  font-size: 16px;
  transition: all var(--transition-fast);
  position: relative;
}

.header-icon-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.header-badge {
  position: relative;
  cursor: pointer;
}

.header-badge__count {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: #EF4444;
  color: white;
  font-size: 10px;
  font-weight: 600;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
}

/* 用户信息 */
.user-profile {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-profile:hover {
  background: var(--color-bg-hover);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  overflow: hidden;
  background: linear-gradient(135deg, #3B82F6, #60A5FA);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: white;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-letter {
  color: white;
  font-weight: var(--font-semibold);
}

.user-info {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
  line-height: 1.3;
}

.user-role {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  white-space: nowrap;
  line-height: 1.3;
}

.user-arrow {
  font-size: 10px;
  color: var(--color-text-tertiary);
  transition: transform var(--transition-fast);
}

/* ─── 下拉菜单 ─── */
.dropdown-menu {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 6px;
  min-width: 160px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background 0.15s;
}

.dropdown-menu__item:hover {
  background: var(--color-bg-hover);
}

.dropdown-menu__item--active {
  color: var(--color-primary);
  font-weight: 500;
}

.dropdown-menu__divider {
  height: 1px;
  background: var(--color-border);
  margin: 6px 0;
}

.pl-check {
  margin-left: auto;
  color: var(--color-primary);
  font-weight: bold;
}

.pl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.user-dropdown {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 6px;
  min-width: 140px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.user-dropdown__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 14px;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background 0.15s;
}

.user-dropdown__item:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

/* ─── 内容区 ─── */
.content {
  flex: 1;
  padding: var(--space-8);
  min-height: 0;
  overflow-y: auto;
}

/* ─── 过渡动画 ─── */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-4px);
}

/* ─── 响应式 ─── */
@media (max-width: 1024px) {
  .header {
    padding: 0 var(--space-6);
  }

  .user-info {
    display: none;
  }

  .product-line__name {
    max-width: 80px;
  }

  .content {
    padding: var(--space-6);
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .content {
    padding: var(--space-4);
  }
}
</style>
