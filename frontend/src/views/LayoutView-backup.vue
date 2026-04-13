<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">
        <h2>⚡ 鱼小七</h2>
      </div>
      
      <nav class="nav-menu">
        <router-link to="/dashboard" class="nav-item">
          <span class="icon">🏠</span>
          <span>首页</span>
        </router-link>
        <router-link v-if="hasPermission('project:list')" to="/projects" class="nav-item">
          <span class="icon">📁</span>
          <span>项目管理</span>
        </router-link>
        <router-link v-if="hasPermission('project:list')" to="/sprints" class="nav-item">
          <span class="icon">🗂️</span>
          <span>迭代管理</span>
        </router-link>
        <router-link v-if="hasPermission('endpoint:list')" to="/endpoints" class="nav-item">
          <span class="icon">🔗</span>
          <span>接口管理</span>
        </router-link>
        <router-link v-if="hasPermission('case:list')" to="/cases" class="nav-item">
          <span class="icon">📝</span>
          <span>接口用例</span>
        </router-link>
        <router-link to="/ui-cases" class="nav-item">
          <span class="icon">🖥️</span>
          <span>UI用例</span>
        </router-link>
        <router-link to="/automation" class="nav-item">
          <span class="icon">🤖</span>
          <span>脚本调度与数据集</span>
        </router-link>
        <router-link v-if="hasPermission('suite:list')" to="/suites" class="nav-item">
          <span class="icon">📦</span>
          <span>套件管理</span>
        </router-link>
        <router-link v-if="hasPermission('result:list')" to="/results" class="nav-item">
          <span class="icon">📈</span>
          <span>执行结果</span>
        </router-link>
        <router-link v-if="hasPermission('environment:list')" to="/environments" class="nav-item">
          <span class="icon">🌐</span>
          <span>环境管理</span>
        </router-link>
        <router-link v-if="hasPermission('user:list')" to="/account" class="nav-item">
          <span class="icon">👤</span>
          <span>个人信息</span>
        </router-link>
        <router-link v-if="hasPermission('system:manage')" to="/system" class="nav-item">
          <span class="icon">⚙️</span>
          <span>系统管理</span>
        </router-link>
        <router-link v-if="hasPermission('product_line:list')" to="/product-lines" class="nav-item">
          <span class="icon">🏭</span>
          <span>产品线管理</span>
        </router-link>
        <router-link to="/performance" class="nav-item">
          <span class="icon">⚡</span>
          <span>性能测试</span>
        </router-link>
      </nav>
    </aside>
    
    <div class="main-content">
      <header class="header">
        <div class="header-left">
          <h3>{{ pageTitle }}</h3>
        </div>
        <div class="header-right">
          <!-- 产品线切换器 -->
          <div v-if="userStore.productLines.length" class="product-line-switcher">
            <div class="pl-dropdown">
              <button class="pl-current">
                <span class="pl-dot"></span>
                <span class="pl-name">{{ userStore.currentProductLine?.name || '请选择' }}</span>
                <span class="pl-arrow">▾</span>
              </button>
              <ul class="pl-menu">
                <li v-for="pl in userStore.productLines" :key="pl.id"
                  class="pl-menu-item"
                  :class="{ active: userStore.currentProductLine?.id === pl.id }"
                  @click="handleSwitchProductLine(pl)">
                  <span class="pl-item-dot"></span>
                  {{ pl.name }}
                  <span v-if="userStore.currentProductLine?.id === pl.id" class="pl-check">✓</span>
                </li>
              </ul>
            </div>
          </div>
          <router-link to="/account" class="user-profile">
            <div class="user-avatar">
              <img v-if="userStore.userInfo?.avatar_url" :src="userStore.userInfo?.avatar_url" alt="用户头像" class="avatar-img" />
              <div v-else class="avatar-placeholder">
                {{ (userStore.userInfo?.nickname || userStore.userInfo?.userInfo?.username || '用户').charAt(0) }}
              </div>
            </div>
            <span class="user-info">{{ userStore.userInfo?.nickname || userStore.userInfo?.userInfo?.username || '用户' }}</span>
          </router-link>
          <button @click="handleLogout" class="btn btn-logout">退出</button>
        </div>
      </header>
      
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
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import AlertDialog from '@/components/AlertDialog.vue'
import { useConfirm } from '@/composables/useConfirm'

const { hasPermission } = useUserStore()

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 确认弹框
const { confirmVisible, confirmOptions, handleConfirm, handleCancel } = useConfirm()

const pageTitle = computed(() => {
  const titles = {
    dashboard: '首页',
    projects: '项目管理',
    sprints: '迭代管理',
    endpoints: '接口管理',
    cases: '接口用例',
    'ui-cases': 'UI用例',
    'ui-case-detail': 'UI用例详情',
    'ui-case-new': '新建UI用例',
    suites: '套件管理',
    environments: '环境管理',
    results: '执行结果',
    account: '个人信息',
    system: '系统管理',
    'product-lines': '产品线管理',
    automation: '脚本调度与数据集',
    'automation-run-detail': '外部脚本执行详情',
  }
  return titles[route.name] || '鱼小七测试平台'
})

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}

const handleSwitchProductLine = async (pl) => {
  await userStore.switchProductLine(pl)
  // 切换后刷新当前页
  router.go(0)
}

// 获取用户信息和产品线
onMounted(async () => {
  if (userStore.access) {
    if (!userStore.userInfo) await userStore.fetchUserInfo()
    if (!userStore.productLines.length) await userStore.fetchProductLines()
  }
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-parchment);
}

/* ===== 侧边栏样式 ===== */
.sidebar {
  width: 260px;
  background-color: var(--color-deep-dark);
  color: var(--color-text-on-dark);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  overflow: hidden;
  border-right: 1px solid var(--color-dark-surface);
  z-index: 1000;
}

.logo {
  padding: var(--space-xl) var(--space-lg) var(--space-lg);
  border-bottom: 1px solid var(--color-dark-surface);
  flex-shrink: 0;
}

.logo h2 {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-subheading-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-on-dark);
  margin: 0;
  letter-spacing: 0.5px;
}

.nav-menu {
  flex: 1;
  padding: var(--space-md) 0;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
}

.nav-menu::-webkit-scrollbar {
  width: 6px;
}

.nav-menu::-webkit-scrollbar-thumb {
  background: var(--color-dark-surface);
  border-radius: var(--radius-subtle);
}

.nav-menu::-webkit-scrollbar-track {
  background: transparent;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-normal);
  line-height: var(--line-height-body);
  color: var(--color-text-on-dark);
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  margin: 0 var(--space-xs);
  border-radius: var(--radius-subtle);
}

.nav-item:hover {
  background-color: var(--color-dark-surface);
  color: var(--color-pure-white);
}

.nav-item.router-link-active {
  background-color: var(--color-dark-surface);
  color: var(--color-pure-white);
  border-left-color: var(--color-terracotta-brand);
  font-weight: var(--font-weight-medium);
}

.icon {
  font-size: 18px;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

/* ===== 主内容区域 ===== */
.main-content {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ===== 顶部导航栏 ===== */
.header {
  background-color: var(--color-ivory);
  padding: var(--space-lg) var(--space-xl);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border-cream);
  position: sticky;
  top: 0;
  z-index: 900;
  box-shadow: var(--shadow-level-1);
}

.header h3 {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-subheading-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

/* ===== 用户信息区域 ===== */
.user-profile {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  text-decoration: none;
  cursor: pointer;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-generous);
  transition: all 0.2s ease;
  background-color: var(--color-warm-sand);
  border: 1px solid var(--color-border-warm);
}

.user-profile:hover {
  background-color: var(--color-border-warm);
  box-shadow: var(--shadow-ring-warm);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--color-terracotta-brand);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--color-ivory);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-terracotta-brand), var(--color-coral-accent));
  color: var(--color-ivory);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-semibold);
}

.user-info {
  color: var(--color-text-primary);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-medium);
}

/* ===== 退出按钮 ===== */
.btn-logout {
  background-color: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-cream);
  padding: var(--space-xs) var(--space-md);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body-sm);
  border-radius: var(--radius-comfortable);
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background-color: var(--color-error-crimson);
  color: var(--color-ivory);
  border-color: var(--color-error-crimson);
}

/* ===== 产品线切换器 ===== */
.product-line-switcher {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.pl-label {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-caption);
  color: var(--color-text-secondary);
  white-space: nowrap;
  font-weight: var(--font-weight-medium);
}

.pl-dropdown {
  position: relative;
}

.pl-current {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border: 1.5px solid var(--color-border-cream);
  border-radius: var(--radius-generous);
  background-color: var(--color-ivory);
  cursor: pointer;
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  transition: all 0.15s ease;
  white-space: nowrap;
  min-width: 140px;
  box-shadow: var(--shadow-ring-subtle);
}

.pl-current:hover {
  border-color: var(--color-terracotta-brand);
  background-color: var(--color-warm-sand);
  box-shadow: var(--shadow-ring-warm);
}

.pl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-success);
  flex-shrink: 0;
}

.pl-name {
  flex: 1;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pl-arrow {
  font-size: 11px;
  color: var(--color-text-tertiary);
  transition: transform 0.2s ease;
}

.pl-dropdown.open .pl-arrow {
  transform: rotate(180deg);
}

/* ===== 响应式设计 ===== */
@media (max-width: 991px) {
  .sidebar {
    width: 220px;
  }

  .main-content {
    margin-left: 220px;
  }

  .header {
    padding: var(--space-md) var(--space-lg);
  }
}

@media (max-width: 767px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    width: 280px;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .main-content {
    margin-left: 0;
  }

  .header {
    padding: var(--space-sm) var(--space-md);
  }

  .header-right {
    gap: var(--space-md);
  }

  .pl-label {
    display: none;
  }

  .pl-current {
    min-width: 100px;
  }
}

/* ===== 内容区域 ===== */
.content {
  flex: 1;
  padding: var(--space-xl);
  background-color: var(--color-parchment);
}

@media (max-width: 991px) {
  .content {
    padding: var(--space-lg);
  }
}

@media (max-width: 767px) {
  .content {
    padding: var(--space-md);
  }
}
.pl-menu {
  display: none;
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  min-width: 160px;
  background: white;
  border: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,.12);
  list-style: none;
  padding: 6px 0;
  z-index: 999;
  animation: fadeIn .15s ease;
}
.pl-dropdown:hover .pl-menu,
.pl-dropdown:focus-within .pl-menu {
  display: block;
}
.pl-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  font-size: 13px;
  cursor: pointer;
  color: var(--text);
  transition: background .1s;
}
.pl-menu-item:hover { background: #f5f9ff; }
.pl-menu-item.active { color: var(--accent); font-weight: 600; background: #e8f4fd; }
.pl-item-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #bbb;
  flex-shrink: 0;
}
.pl-menu-item.active .pl-item-dot { background: var(--accent); }
.pl-check { margin-left: auto; color: var(--accent); font-size: 12px; }
@keyframes fadeIn { from { opacity:0; transform:translateY(-4px); } to { opacity:1; transform:translateY(0); } }

.content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
