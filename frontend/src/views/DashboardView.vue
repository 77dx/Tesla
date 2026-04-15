<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-header__left">
        <div class="greeting-block">
          <h1 class="greeting">{{ greeting }}，{{ username }}</h1>
          <p class="greeting-sub">这是你的测试工作台，今天有 {{ todayRuns }} 条执行记录</p>
        </div>
      </div>
      <div class="page-header__right">
        <button class="btn btn--ghost" @click="refresh" :disabled="loading">
          <span class="btn__icon" :class="{ 'btn__icon--spin': loading }">&#8635;</span>
          刷新数据
        </button>
        <button class="btn btn--primary" @click="$router.push('/suites/new')">
          <span class="btn__icon">+</span>
          新建套件
        </button>
      </div>
    </div>

    <!-- 关键指标区 -->
    <div class="metrics-grid">
      <div
        v-for="metric in metrics"
        :key="metric.label"
        class="metric-card"
        :class="`metric-card--${metric.type}`"
      >
        <div class="metric-card__header">
          <span class="metric-card__label">{{ metric.label }}</span>
          <div class="metric-card__icon" :style="{ background: metric.iconBg }">
            <component :is="metric.icon" :style="{ color: metric.color }" />
          </div>
        </div>
        <div class="metric-card__body">
          <div class="metric-card__value">{{ metric.value }}</div>
          <div class="metric-card__trend" :class="`trend--${metric.trend}`">
            <component :is="metric.trendIcon" />
            <span>{{ metric.trendValue }}</span>
          </div>
        </div>
        <div class="metric-card__footer">
          <div class="metric-card__progress">
            <div class="progress-track">
              <div
                class="progress-fill"
                :style="{
                  width: metric.progress + '%',
                  background: metric.color
                }"
              />
            </div>
          </div>
          <span class="metric-card__progress-text">{{ metric.progress }}%</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="main-grid">
      <!-- 左侧：执行概览 -->
      <div class="panel panel--wide">
        <div class="panel__header">
          <div class="panel__title">
            <LineChartOutlined class="panel__icon" />
            <span>最近执行</span>
          </div>
          <div class="panel__actions">
            <div class="tab-group">
              <button
                v-for="tab in execTabs"
                :key="tab.key"
                class="tab-btn"
                :class="{ 'tab-btn--active': execTab === tab.key }"
                @click="execTab = tab.key"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>
        </div>
        <div class="panel__body">
          <div v-if="filteredExecutions.length === 0" class="empty-state">
            <RocketOutlined class="empty-icon" />
            <p>暂无执行记录</p>
            <button class="btn btn--primary btn--sm" @click="$router.push('/suites')">去创建套件</button>
          </div>
          <div v-else class="exec-list">
            <div
              v-for="exec in filteredExecutions"
              :key="exec.id"
              class="exec-item"
              @click="$router.push(`/results/${exec.id}`)"
            >
              <div class="exec-item__left">
                <div class="exec-item__status">
                  <span
                    class="status-dot"
                    :class="`status-dot--${exec.statusType}`"
                  />
                </div>
                <div class="exec-item__info">
                  <div class="exec-item__name">{{ exec.name }}</div>
                  <div class="exec-item__meta">
                    <span class="exec-item__project">{{ exec.project }}</span>
                    <span class="exec-item__dot">·</span>
                    <span class="exec-item__time">{{ exec.time }}</span>
                  </div>
                </div>
              </div>
              <div class="exec-item__right">
                <div class="exec-item__stats">
                  <div class="exec-stat exec-stat--pass">
                    <CheckCircleOutlined />
                    <span>{{ exec.pass }}</span>
                  </div>
                  <div class="exec-stat exec-stat--fail" v-if="exec.fail > 0">
                    <CloseCircleOutlined />
                    <span>{{ exec.fail }}</span>
                  </div>
                  <div class="exec-stat exec-stat--skip" v-if="exec.skip > 0">
                    <MinusCircleOutlined />
                    <span>{{ exec.skip }}</span>
                  </div>
                </div>
                <div class="exec-item__duration">{{ exec.duration }}</div>
              </div>
            </div>
          </div>
        </div>
        <div class="panel__footer">
          <a @click="$router.push('/results')" class="view-more">
            查看全部执行记录
            <RightOutlined />
          </a>
        </div>
      </div>

      <!-- 右侧：快捷入口 -->
      <div class="panel-stack">
        <!-- 快捷操作 -->
        <div class="panel">
          <div class="panel__header">
            <div class="panel__title">
              <ThunderboltOutlined class="panel__icon" />
              <span>快捷操作</span>
            </div>
          </div>
          <div class="panel__body">
            <div class="quick-actions">
              <div
                v-for="action in quickActions"
                :key="action.key"
                class="quick-action"
                @click="$router.push(action.path)"
              >
                <div class="quick-action__icon" :style="{ background: action.bg }">
                  <component :is="action.icon" :style="{ color: action.color }" />
                </div>
                <span class="quick-action__label">{{ action.label }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 活跃项目 -->
        <div class="panel">
          <div class="panel__header">
            <div class="panel__title">
              <FolderOutlined class="panel__icon" />
              <span>活跃项目</span>
            </div>
            <a @click="$router.push('/projects')" class="panel__link">全部</a>
          </div>
          <div class="panel__body">
            <div class="project-list">
              <div
                v-for="project in activeProjects"
                :key="project.id"
                class="project-item"
                @click="$router.push(`/projects/${project.id}`)"
              >
                <div class="project-item__avatar" :style="{ background: project.color }">
                  {{ project.name.charAt(0) }}
                </div>
                <div class="project-item__info">
                  <div class="project-item__name">{{ project.name }}</div>
                  <div class="project-item__meta">
                    {{ project.cases }} 个用例 · {{ project.executions }} 次执行
                  </div>
                </div>
                <div class="project-item__rate" :class="`rate--${project.rateType}`">
                  {{ project.passRate }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：测试覆盖概览 -->
    <div class="coverage-section">
      <div class="panel">
        <div class="panel__header">
          <div class="panel__title">
            <SafetyCertificateOutlined class="panel__icon" />
            <span>测试覆盖概览</span>
          </div>
        </div>
        <div class="panel__body">
          <div class="coverage-grid">
            <div
              v-for="item in coverageData"
              :key="item.label"
              class="coverage-item"
            >
              <div class="coverage-item__header">
                <span class="coverage-item__label">{{ item.label }}</span>
                <span class="coverage-item__count">{{ item.count }}</span>
              </div>
              <div class="progress-track progress-track--sm">
                <div
                  class="progress-fill"
                  :style="{
                    width: (item.count / maxCoverage * 100) + '%',
                    background: item.color
                  }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  LineChartOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  MinusCircleOutlined,
  RightOutlined,
  ThunderboltOutlined,
  FolderOutlined,
  SafetyCertificateOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  FileTextOutlined,
  AppstoreAddOutlined,
  GlobalOutlined,
  TeamOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons-vue'

const userStore = useUserStore()
const loading = ref(false)
const execTab = ref('all')
const execTabs = [
  { key: 'all', label: '全部' },
  { key: 'success', label: '成功' },
  { key: 'failed', label: '失败' },
  { key: 'running', label: '运行中' },
]

// 用户信息
const username = computed(() => {
  const u = userStore.userInfo
  return u?.nickname || u?.username || u?.userInfo?.username || '工程师'
})

// 问候语
const now = new Date()
const h = now.getHours()
const greeting = h < 6 ? '凌晨好' : h < 11 ? '早上好' : h < 13 ? '中午好' : h < 18 ? '下午好' : '晚上好'

// 今日执行数（模拟）
const todayRuns = ref(0)

// 关键指标
const metrics = ref([
  {
    label: '总用例数',
    value: '1,248',
    progress: 82,
    color: '#3B82F6',
    iconBg: '#EFF6FF',
    icon: FileTextOutlined,
    trend: 'up',
    trendValue: '+12%',
    trendIcon: ArrowUpOutlined,
    type: 'primary',
  },
  {
    label: '接口总数',
    value: '356',
    progress: 65,
    color: '#10B981',
    iconBg: '#ECFDF5',
    icon: GlobalOutlined,
    trend: 'up',
    trendValue: '+5%',
    trendIcon: ArrowUpOutlined,
    type: 'success',
  },
  {
    label: '本周执行',
    value: '248',
    progress: 71,
    color: '#8B5CF6',
    iconBg: '#F5F3FF',
    icon: ThunderboltOutlined,
    trend: 'up',
    trendValue: '+23%',
    trendIcon: ArrowUpOutlined,
    type: 'purple',
  },
  {
    label: '通过率',
    value: '95.8%',
    progress: 95.8,
    color: '#10B981',
    iconBg: '#ECFDF5',
    icon: CheckCircleOutlined,
    trend: 'up',
    trendValue: '+2.1%',
    trendIcon: ArrowUpOutlined,
    type: 'success',
  },
])

// 最近执行
const executions = ref([
  {
    id: 1,
    name: '用户登录模块测试',
    project: '用户中心',
    time: '5 分钟前',
    duration: '12s',
    pass: 24,
    fail: 0,
    skip: 1,
    status: 'success',
    statusType: 'success',
  },
  {
    id: 2,
    name: '订单创建流程测试',
    project: '电商平台',
    time: '15 分钟前',
    duration: '45s',
    pass: 38,
    fail: 2,
    skip: 0,
    status: 'failed',
    statusType: 'error',
  },
  {
    id: 3,
    name: '支付接口验证',
    project: '支付系统',
    time: '30 分钟前',
    duration: '8s',
    pass: 0,
    fail: 5,
    skip: 0,
    status: 'failed',
    statusType: 'error',
  },
  {
    id: 4,
    name: '性能压力测试',
    project: '核心服务',
    time: '2 小时前',
    duration: '3m',
    pass: 100,
    fail: 0,
    skip: 0,
    status: 'success',
    statusType: 'success',
  },
  {
    id: 5,
    name: '用户权限检查',
    project: '用户中心',
    time: '3 小时前',
    duration: '15s',
    pass: 18,
    fail: 0,
    skip: 2,
    status: 'success',
    statusType: 'success',
  },
])

const filteredExecutions = computed(() => {
  if (execTab.value === 'all') return executions.value
  if (execTab.value === 'success') return executions.value.filter(e => e.status === 'success')
  if (execTab.value === 'failed') return executions.value.filter(e => e.status === 'failed')
  if (execTab.value === 'running') return executions.value.filter(e => e.status === 'running')
  return executions.value
})

// 快捷操作
const quickActions = ref([
  { key: 'cases', label: '新建用例', icon: FileTextOutlined, path: '/cases', bg: '#EFF6FF', color: '#3B82F6' },
  { key: 'suites', label: '创建套件', icon: AppstoreAddOutlined, path: '/suites/new', bg: '#F5F3FF', color: '#8B5CF6' },
  { key: 'endpoints', label: '添加接口', icon: GlobalOutlined, path: '/endpoints', bg: '#ECFDF5', color: '#10B981' },
  { key: 'environments', label: '环境配置', icon: ExclamationCircleOutlined, path: '/environments', bg: '#FFFBEB', color: '#F59E0B' },
])

// 活跃项目
const activeProjects = ref([
  { id: 1, name: '用户中心', cases: 128, executions: 456, passRate: '98.2%', rateType: 'high', color: '#3B82F6' },
  { id: 2, name: '电商平台', cases: 89, executions: 234, passRate: '94.5%', rateType: 'medium', color: '#8B5CF6' },
  { id: 3, name: '支付系统', cases: 56, executions: 123, passRate: '91.2%', rateType: 'medium', color: '#10B981' },
  { id: 4, name: '核心服务', cases: 203, executions: 890, passRate: '99.1%', rateType: 'high', color: '#F59E0B' },
])

// 覆盖数据
const coverageData = ref([
  { label: '项目管理', count: 23, color: '#3B82F6' },
  { label: '迭代管理', count: 45, color: '#8B5CF6' },
  { label: '接口管理', count: 356, color: '#10B981' },
  { label: '用例管理', count: 1248, color: '#F59E0B' },
  { label: '套件管理', count: 89, color: '#EF4444' },
  { label: '环境配置', count: 12, color: '#06B6D4' },
])

const maxCoverage = computed(() => Math.max(...coverageData.value.map(c => c.count)))

// 刷新
const refresh = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

onMounted(() => {
  todayRuns.value = executions.value.filter(e => {
    const execTime = new Date()
    execTime.setMinutes(execTime.getMinutes() - 5)
    return true
  }).length || 5
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

/* ─── 按钮系统 ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  outline: none;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--primary {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.btn--primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

.btn--ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}

.btn--ghost:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: rgba(233, 84, 74, 0.05);
}

.btn--sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn__icon {
  font-size: 16px;
  line-height: 1;
}

.btn__icon--spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ─── Tab 切换 ─── */
.tab-group {
  display: flex;
  gap: 4px;
  background: var(--color-bg-layout);
  padding: 4px;
  border-radius: 8px;
}

.tab-btn {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-card);
}

.tab-btn--active {
  color: var(--color-primary);
  background: var(--color-bg-card);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* ─── 页面标题 ─── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-8);
  gap: var(--space-6);
}

.greeting-block {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.greeting {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: var(--tracking-tight);
}

.greeting-sub {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

.page-header__right {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  flex-shrink: 0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

/* ─── 指标网格 ─── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-5);
  margin-bottom: var(--space-8);
}

.metric-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  transition: all var(--transition-base);
}

.metric-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.metric-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}

.metric-card__label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

.metric-card__icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.metric-card__body {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.metric-card__value {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  letter-spacing: var(--tracking-tight);
  line-height: 1;
}

.metric-card__trend {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  padding: 2px 6px;
  border-radius: var(--radius-full);
}

.trend--up {
  color: var(--color-success);
  background: var(--color-success-bg);
}

.trend--down {
  color: var(--color-error);
  background: var(--color-error-bg);
}

.metric-card__footer {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.metric-card__progress {
  flex: 1;
}

.metric-card__progress-text {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

/* ─── 进度条 ─── */
.progress-track {
  height: 4px;
  background: var(--color-gray-200);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-track--sm {
  height: 3px;
}

.progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--transition-slow) var(--ease-out);
}

/* ─── 状态点 ─── */
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot--success { background: var(--color-success); }
.status-dot--error   { background: var(--color-error); }
.status-dot--warning { background: var(--color-warning); }
.status-dot--running {
  background: var(--color-primary);
  animation: pulse-ring 1.5s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

/* ─── 主要网格 ─── */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: var(--space-6);
  margin-bottom: var(--space-6);
}

.panel {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.panel--wide {
  grid-column: 1;
}

.panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-gray-50);
}

.panel__title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.panel__icon {
  font-size: 16px;
  color: var(--color-primary);
}

.panel__actions {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.panel__link {
  font-size: var(--text-sm);
  color: var(--color-primary);
  cursor: pointer;
}

.panel__link:hover {
  color: var(--color-primary-hover);
}

.panel__body {
  padding: 0;
}

.panel__footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border);
  background: var(--color-gray-50);
}

.view-more {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: var(--space-1);
  cursor: pointer;
}

.view-more:hover {
  color: var(--color-primary);
}

/* ─── 执行列表 ─── */
.exec-tabs {
  margin-bottom: 0;
}

.exec-tabs :deep(.ant-tabs-nav) {
  margin-bottom: 0;
}

.exec-tabs :deep(.ant-tabs-tab) {
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-3);
  margin: 0;
}

.exec-list {
  display: flex;
  flex-direction: column;
}

.exec-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.exec-item:last-child {
  border-bottom: none;
}

.exec-item:hover {
  background: var(--color-bg-hover);
}

.exec-item__left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex: 1;
  min-width: 0;
}

.exec-item__status {
  flex-shrink: 0;
  padding-top: 2px;
}

.exec-item__info {
  min-width: 0;
  flex: 1;
}

.exec-item__name {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 2px;
}

.exec-item__meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.exec-item__dot {
  color: var(--color-gray-300);
}

.exec-item__right {
  display: flex;
  align-items: center;
  gap: var(--space-6);
  flex-shrink: 0;
}

.exec-item__stats {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.exec-stat {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.exec-stat--pass { color: var(--color-success); }
.exec-stat--fail { color: var(--color-error); }
.exec-stat--skip { color: var(--color-text-tertiary); }

.exec-item__duration {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  font-family: var(--font-mono);
  min-width: 36px;
  text-align: right;
}

/* ─── 面板栈 ─── */
.panel-stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.panel-stack .panel {
  flex: 1;
}

/* ─── 快捷操作 ─── */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  padding: var(--space-5) var(--space-6);
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
}

.quick-action:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.quick-action__icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.quick-action__label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
}

/* ─── 项目列表 ─── */
.project-list {
  display: flex;
  flex-direction: column;
  padding: 0;
}

.project-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.project-item:last-child {
  border-bottom: none;
}

.project-item:hover {
  background: var(--color-bg-hover);
}

.project-item__avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: white;
  flex-shrink: 0;
}

.project-item__info {
  flex: 1;
  min-width: 0;
}

.project-item__name {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 2px;
}

.project-item__meta {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.project-item__rate {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.rate--high {
  color: var(--color-success);
  background: var(--color-success-bg);
}

.rate--medium {
  color: var(--color-warning);
  background: var(--color-warning-bg);
}

.rate--low {
  color: var(--color-error);
  background: var(--color-error-bg);
}

/* ─── 覆盖概览 ─── */
.coverage-section {
  margin-bottom: 0;
}

.coverage-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--space-6);
  padding: var(--space-6);
}

.coverage-item__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-3);
}

.coverage-item__label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.coverage-item__count {
  font-size: var(--text-base);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
}

/* ─── 空状态 ─── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  gap: var(--space-4);
  color: var(--color-text-tertiary);
}

.empty-icon {
  font-size: 40px;
  opacity: 0.4;
}

.empty-state p {
  font-size: var(--text-sm);
  margin: 0;
}

/* ─── 响应式 ─── */
@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-grid {
    grid-template-columns: 1fr;
  }

  .panel--wide {
    grid-column: 1;
  }

  .panel-stack {
    flex-direction: row;
  }

  .panel-stack .panel {
    flex: 1;
  }

  .coverage-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-4);
  }

  .page-header__right {
    justify-content: flex-end;
  }

  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
  }

  .metric-card {
    padding: var(--space-5);
  }

  .metric-card__value {
    font-size: var(--text-2xl);
  }

  .panel-stack {
    flex-direction: column;
  }

  .coverage-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .exec-item__stats {
    display: none;
  }
}

@media (max-width: 480px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
