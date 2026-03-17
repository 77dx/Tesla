<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">
        <h2>⚡ Tesla</h2>
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
        <router-link v-if="hasPermission('endpoint:list')" to="/endpoints" class="nav-item">
          <span class="icon">🔗</span>
          <span>接口管理</span>
        </router-link>
        <router-link v-if="hasPermission('case:list')" to="/cases" class="nav-item">
          <span class="icon">📝</span>
          <span>用例管理</span>
        </router-link>
        <router-link v-if="hasPermission('suite:list')" to="/suites" class="nav-item">
          <span class="icon">📦</span>
          <span>套件管理</span>
        </router-link>
        <router-link v-if="hasPermission('environment:list')" to="/environments" class="nav-item">
          <span class="icon">🌐</span>
          <span>环境管理</span>
        </router-link>
        <router-link v-if="hasPermission('result:list')" to="/results" class="nav-item">
          <span class="icon">📈</span>
          <span>执行结果</span>
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
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
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
    endpoints: '接口管理',
    cases: '用例管理',
    suites: '套件管理',
    environments: '环境管理',
    results: '执行结果',
    account: '个人信息',
    system: '系统管理',
    'product-lines': '产品线管理',
  }
  return titles[route.name] || 'Tesla 测试平台'
})

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const handleSwitchProductLine = async (pl) => {
  await userStore.switchProductLine(pl)
  // 切换后刷新当前页
  router.go(0)
}

// 获取用户信息和产品线
onMounted(async () => {
  if (userStore.token) {
    if (!userStore.userInfo) await userStore.fetchUserInfo()
    if (!userStore.productLines.length) await userStore.fetchProductLines()
  }
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: var(--primary);
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
}

.logo {
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  font-size: 24px;
  font-weight: 700;
}

.nav-menu {
  flex: 1;
  padding: 16px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border-left-color: #3498db;
}

.icon {
  font-size: 20px;
}

.main-content {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  padding: 20px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px var(--shadow);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.user-profile:hover {
  background: rgba(0, 0, 0, 0.05);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--accent-light);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #f0f0f0;
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
  background: linear-gradient(135deg, var(--accent), #3498db);
  color: white;
  font-size: 14px;
  font-weight: 600;
}

.user-info {
  color: var(--text-light);
  font-size: 14px;
  font-weight: 500;
}

.btn-logout {
  background: transparent;
  color: var(--text-light);
  border: 1px solid var(--border);
  padding: 8px 16px;
  font-size: 14px;
}

.btn-logout:hover {
  background: var(--danger);
  color: white;
  border-color: var(--danger);
}

/* 产品线切换器 */
.product-line-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
}
.pl-label {
  font-size: 12px;
  color: var(--text-light);
  white-space: nowrap;
}
.pl-dropdown {
  position: relative;
}
.pl-current {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1.5px solid var(--border);
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  transition: all .15s;
  white-space: nowrap;
  min-width: 120px;
}
.pl-current:hover {
  border-color: var(--accent);
  background: #f0f8ff;
}
.pl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #27ae60;
  flex-shrink: 0;
}
.pl-name {
  flex: 1;
  text-align: left;
}
.pl-arrow {
  font-size: 11px;
  color: var(--text-light);
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
}
</style>
