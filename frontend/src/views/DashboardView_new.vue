<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <a-card class="welcome-card" :bordered="false">
      <div class="welcome-content">
        <div class="welcome-left">
          <h1 class="welcome-title">{{ greeting }}，{{ username }} 👋</h1>
          <p class="welcome-sub">今天是 {{ todayStr }}，一切就绪，开始测试吧。</p>
          <div class="quick-stats">
            <div class="stat-item">
              <div class="stat-label">今日执行</div>
              <div class="stat-value">12</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">通过率</div>
              <div class="stat-value">95%</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">活跃项目</div>
              <div class="stat-value">8</div>
            </div>
          </div>
        </div>
        <div class="welcome-right">
          <div class="welcome-badge">
            <a-tag color="blue">⚡ 鱼小七测试平台</a-tag>
          </div>
          <a-button type="primary" size="large" @click="$router.push('/cases')">
            开始测试
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 核心功能卡片 -->
    <div class="section-header">
      <h2 class="section-title">核心功能</h2>
      <div class="section-sub">快速访问平台核心功能模块</div>
    </div>

    <a-row :gutter="[24, 24]" class="feature-grid">
      <a-col :xs="24" :sm="12" :lg="8" v-for="feature in features" :key="feature.key">
        <a-card 
          class="feature-card" 
          hoverable
          @click="$router.push(feature.path)"
        >
          <div class="feature-content">
            <div class="feature-icon">
              <component :is="feature.icon" />
            </div>
            <div class="feature-body">
              <h3 class="feature-title">{{ feature.title }}</h3>
              <p class="feature-desc">{{ feature.desc }}</p>
            </div>
            <div class="feature-arrow">
              <RightOutlined />
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 快速开始指南 -->
    <div class="section-header">
      <h2 class="section-title">快速上手</h2>
      <div class="section-sub">按照以下步骤快速开始使用平台</div>
    </div>

    <a-card class="guide-card" :bordered="false">
      <a-steps :current="2" size="small" class="guide-steps">
        <a-step v-for="(step, index) in steps" :key="index" :title="step.title" :description="step.desc" />
      </a-steps>
    </a-card>

    <!-- 最近活动 - 终极简单版本 -->
    <div class="ultimate-container" ref="containerRef">
      <!-- 左侧固定列 -->
      <div class="ultimate-left-column" ref="leftColumnRef">
        <a-card title="最近执行" :bordered="false" class="ultimate-left-card">
          <template #extra>
            <a href="javascript:;">查看全部</a>
          </template>
          <a-list :data-source="recentActivities" size="small">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: item.color }">
                      <template #icon>
                        <component :is="item.icon" />
                      </template>
                    </a-avatar>
                  </template>
                  <template #title>
                    <span>{{ item.title }}</span>
                    <a-tag :color="item.statusColor" size="small">{{ item.status }}</a-tag>
                  </template>
                  <template #description>
                    {{ item.time }} · {{ item.project }}
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </div>
      
      <!-- 右侧滚动内容 -->
      <div class="ultimate-right-column">
        <a-card title="统计数据" :bordered="false">
          <div class="stats-content">
            <div class="stat-card" v-for="stat in stats" :key="stat.title">
              <div class="stat-icon" :style="{ color: stat.color }">
                <component :is="stat.icon" />
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-title">{{ stat.title }}</div>
              </div>
            </div>
          </div>
        </a-card>
        
        <a-card title="平台公告" :bordered="false" class="mt-4">
          <div class="announcement-list">
            <div class="announcement-item">
              <div class="announcement-title">系统维护通知</div>
              <div class="announcement-date">2024-04-15</div>
              <div class="announcement-content">本周六凌晨2:00-4:00进行系统维护，期间服务将不可用。</div>
            </div>
            <div class="announcement-item">
              <div class="announcement-title">新功能上线</div>
              <div class="announcement-date">2024-04-10</div>
              <div class="announcement-content">新增批量执行功能，支持同时运行多个测试套件。</div>
            </div>
            <div class="announcement-item">
              <div class="announcement-title">性能优化</div>
              <div class="announcement-date">2024-04-05</div>
              <div class="announcement-content">优化了测试报告生成速度，提升用户体验。</div>
            </div>
          </div>
        </a-card>
        
        <a-card title="使用指南" :bordered="false" class="mt-4">
          <div class="guide-list">
            <div class="guide-item">
              <div class="guide-title">如何创建测试用例？</div>
              <div class="guide-desc">在接口管理页面选择接口，点击"创建用例"按钮。</div>
            </div>
            <div class="guide-item">
              <div class="guide-title">如何查看测试报告？</div>
              <div class="guide-desc">在执行结果页面可以查看详细的测试报告和日志。</div>
            </div>
            <div class="guide-item">
              <div class="guide-title">如何管理项目成员？</div>
              <div class="guide-desc">在项目管理页面可以添加或移除项目成员。</div>
            </div>
          </div>
        </a-card>
        
        <!-- 添加大量额外内容确保页面足够长 -->
        <div class="extra-long-content">
          <div v-for="n in 20" :key="n" class="extra-item">
            额外内容 {{ n }} - 确保页面足够长以产生滚动
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  RightOutlined,
  LinkOutlined,
  FileTextOutlined,
  AppstoreAddOutlined,
  GlobalOutlined,
  BarChartOutlined,
  FolderOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  PlayCircleOutlined,
  ClockCircleOutlined,
  UserOutlined
} from '@ant-design/icons-vue'

const userStore = useUserStore()

const username = computed(() => {
  const u = userStore.userInfo
  return u?.nickname || u?.username || u?.userInfo?.username || '测试员'
})

const now = new Date()
const h = now.getHours()
const greeting = h < 6 ? '凌晨好' : h < 12 ? '早上好' : h < 14 ? '中午好' : h < 18 ? '下午好' : '晚上好'
const todayStr = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

// 左侧固定功能
const isLeftColumnFixed = ref(false)
const leftColumnRef = ref(null)
const originalLeftColumnStyle = ref({})

const handleScroll = () => {
  if (!leftColumnRef.value) return
  
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const activityContainer = document.querySelector('.activity-container')
  
  if (!activityContainer) return
  
  const containerRect = activityContainer.getBoundingClientRect()
  const containerTop = containerRect.top + scrollTop
  
  // 当滚动到活动容器时，固定左侧列
  if (scrollTop > containerTop - 20) {
    if (!isLeftColumnFixed.value) {
      // 保存原始样式
      const leftColumn = leftColumnRef.value
      originalLeftColumnStyle.value = {
        width: leftColumn.offsetWidth + 'px',
        top: '20px'
      }
      isLeftColumnFixed.value = true
    }
  } else {
    isLeftColumnFixed.value = false
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  // 初始计算
  setTimeout(handleScroll, 100)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const features = ref([
  {
    key: 'endpoints',
    title: '接口管理',
    desc: '统一维护项目下的 HTTP 接口，配置请求头、参数、Body',
    path: '/endpoints',
    icon: LinkOutlined
  },
  {
    key: 'cases',
    title: '用例管理',
    desc: '基于接口创建测试用例，配置断言与变量提取规则',
    path: '/cases',
    icon: FileTextOutlined
  },
  {
    key: 'suites',
    title: '套件管理',
    desc: '将多个用例编排成测试套件，支持跨用例变量传递',
    path: '/suites',
    icon: AppstoreAddOutlined
  },
  {
    key: 'environments',
    title: '环境管理',
    desc: '配置测试/生产环境，管理服务域名和全局变量',
    path: '/environments',
    icon: GlobalOutlined
  },
  {
    key: 'results',
    title: '执行结果',
    desc: '查看详细报告，包含用例通过率、断言明细、错误日志',
    path: '/results',
    icon: BarChartOutlined
  },
  {
    key: 'projects',
    title: '项目管理',
    desc: '按项目隔离接口与用例，支持多项目并行协作',
    path: '/projects',
    icon: FolderOutlined
  },
])

const steps = ref([
  { title: '创建项目', desc: '在「项目管理」中新建项目' },
  { title: '定义接口', desc: '在「接口管理」中录入接口' },
  { title: '编写用例', desc: '基于接口创建用例' },
  { title: '组装套件', desc: '将用例加入套件编排顺序' },
  { title: '配置环境', desc: '配置域名与全局变量' },
  { title: '运行查看', desc: '一键运行套件查看报告' },
])

const recentActivities = ref([
  {
    title: '用户登录模块测试',
    status: '成功',
    statusColor: 'green',
    time: '5分钟前',
    project: '用户中心项目',
    icon: CheckCircleOutlined,
    color: '#52c41a'
  },
  {
    title: '订单创建流程',
    status: '进行中',
    statusColor: 'blue',
    time: '15分钟前',
    project: '电商平台',
    icon: PlayCircleOutlined,
    color: '#1890ff'
  },
  {
    title: '支付接口验证',
    status: '失败',
    statusColor: 'red',
    time: '30分钟前',
    project: '支付系统',
    icon: ClockCircleOutlined,
    color: '#ff4d4f'
  },
  {
    title: '性能压力测试',
    status: '成功',
    statusColor: 'green',
    time: '2小时前',
    project: '核心服务',
    icon: ThunderboltOutlined,
    color: '#722ed1'
  },
  {
    title: '用户权限检查',
    status: '成功',
    statusColor: 'green',
    time: '3小时前',
    project: '用户中心项目',
    icon: UserOutlined,
    color: '#fa8c16'
  }
])

const stats = ref([
  {
    title: '总用例数',
    value: '1,248',
    color: '#1890ff',
    icon: FileTextOutlined
  },
  {
    title: '总接口数',
    value: '356',
    color: '#52c41a',
    icon: LinkOutlined
  },
  {
    title: '总套件数',
    value: '89',
    color: '#722ed1',
    icon: AppstoreAddOutlined
  },
  {
    title: '总项目数',
    value: '23',
    color: '#fa8c16',
    icon: FolderOutlined
  }
])
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 欢迎卡片 */
.welcome-card {
  background: linear-gradient(135deg, #1890ff 0%, #52c41a 100%);
  color: white;
  border-radius: 12px;
}

.welcome-card :deep(.ant-card-body) {
  padding: 40px !important;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 40px;
}

.welcome-left {
  flex: 1;
}

.welcome-title {
  font-size: 32px;
  font-weight: 600;
  color: white;
  margin: 0 0 12px 0;
}

.welcome-sub {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0 0 24px 0;
}

.quick-stats {
  display: flex;
  gap: 32px;
  margin-top: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: white;
}

.welcome-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 16px;
  flex-shrink: 0;
}

.welcome-badge :deep(.ant-tag) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 20px;
}

/* 章节标题 */
.section-header {
  margin: 24px 0 16px 0;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
}

.section-sub {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

/* 功能卡片 */
.feature-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.feature-card :deep(.ant-card-body) {
  padding: 24px !important;
}

.feature-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #e6f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #1890ff;
  font-size: 20px;
}

.feature-icon[data-key="cases"] {
  background: #f6ffed;
  color: #52c41a;
}

.feature-icon[data-key="suites"] {
  background: #f9f0ff;
  color: #722ed1;
}

.feature-icon[data-key="environments"] {
  background: #fff7e6;
  color: #fa8c16;
}

.feature-icon[data-key="results"] {
  background: #fff1f0;
  color: #ff4d4f;
}

.feature-icon[data-key="projects"] {
  background: #f6ffed;
  color: #52c41a;
}

.feature-body {
  flex: 1;
  min-width: 0;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 8px 0;
}

.feature-desc {
  font-size: 14px;
  color: #595959;
  line-height: 1.5;
  margin: 0;
}

.feature-arrow {
  color: #bfbfbf;
  font-size: 16px;
  align-self: center;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-arrow {
  color: #1890ff;
  transform: translateX(4px);
}

/* 快速开始指南 */
.guide-card {
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

.guide-card :deep(.ant-card-body) {
  padding: 32px !important;
}

.guide-steps :deep(.ant-steps-item-title) {
  font-weight: 500;
}

.guide-steps :deep(.ant-steps-item-description) {
  color: #8c8c8c;
}

/* 最近活动网格布局 */
.activity-grid {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  align-items: start;
}

/* 左侧固定侧边栏 */
.activity-left-sticky {
  position: sticky;
  top: 20px;
  align-self: flex-start;
  max-height: calc(100vh - 40px);
}

.sticky-sidebar {
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.sticky-sidebar :deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 0 24px;
  flex-shrink: 0;
}

.sticky-sidebar :deep(.ant-card-body) {
  padding: 24px !important;
  flex: 1;
  overflow-y: auto;
  max-height: calc(100vh - 120px);
}

.sticky-sidebar :deep(.ant-card-body)::-webkit-scrollbar {
  width: 6px;
}

.sticky-sidebar :deep(.ant-card-body)::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.sticky-sidebar :deep(.ant-card-body)::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.sticky-sidebar :deep(.ant-card-body)::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 右侧内容区域 */
.activity-right-content {
  position: relative;
}

.activity-right-content :deep(.ant-card) {
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

.activity-right-content :deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 0 24px;
}

.activity-right-content :deep(.ant-card-body) {
  padding: 24px !important;
}

/* 统计数据 */
.stats-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: #f5f5f5;
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
}

.stat-title {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

/* 额外内容样式 */
.extra-content {
  margin-top: 24px;
}

.mt-4 {
  margin-top: 16px;
}

.announcement-list,
.guide-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.announcement-item,
.guide-item {
  padding: 12px;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.announcement-item:hover,
.guide-item:hover {
  background: #f5f5f5;
  transform: translateY(-1px);
}

.announcement-title,
.guide-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 4px 0;
}

.announcement-date {
  font-size: 12px;
  color: #8c8c8c;
  margin: 0 0 8px 0;
}

.announcement-content,
.guide-desc {
  font-size: 13px;
  color: #595959;
  line-height: 1.5;
  margin: 0;
}

/* 最简单的活动容器 - 确保一定能工作 */
.simple-activity-container {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  align-items: start;
  min-height: 800px; /* 确保容器有足够高度 */
}

/* 左侧固定列 - 最简单的实现 */
.simple-left-sticky {
  position: sticky;
  top: 20px;
  align-self: start;
}

.simple-sticky-card {
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

.simple-sticky-card :deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 0 24px;
}

.simple-sticky-card :deep(.ant-card-body) {
  padding: 24px !important;
}

/* 右侧滚动列 */
.simple-right-scroll {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 响应式设计 - 移动设备 */
@media (max-width: 768px) {
  .simple-activity-container {
    grid-template-columns: 1fr;
    gap: 16px;
    min-height: auto;
  }
  
  .simple-left-sticky {
    position: static; /* 移动设备上取消固定 */
  }
}

/* 其他响应式设计保持不变 */
@media (max-width: 1200px) {
  .welcome-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 24px;
  }
  
  .welcome-right {
    align-items: flex-start;
  }
}

@media (max-width: 992px) {
  .feature-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .feature-icon {
    align-self: flex-start;
  }
  
  .feature-arrow {
    align-self: flex-end;
    margin-top: 8px;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .welcome-card :deep(.ant-card-body) {
    padding: 24px !important;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-sub {
    font-size: 14px;
  }
  
  .quick-stats {
    gap: 24px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .guide-card :deep(.ant-card-body) {
    padding: 24px !important;
  }
  
  .guide-steps :deep(.ant-steps) {
    flex-direction: column;
  }
}

@media (max-width: 576px) {
  .feature-content {
    flex-direction: row;
  }
  
  .quick-stats {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .stat-item {
    flex: 0 0 calc(50% - 8px);
  }
}

/* 终极简单版本 - 保证能工作 */
.ultimate-container {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  align-items: start;
  min-height: 1500px; /* 确保容器有足够高度产生滚动 */
}

.ultimate-left-column {
  position: sticky;
  top: 20px;
  align-self: start;
}

.ultimate-left-card {
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

.ultimate-left-card :deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  padding: 0 24px;
}

.ultimate-left-card :deep(.ant-card-body) {
  padding: 24px !important;
}

.ultimate-right-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.extra-long-content {
  margin-top: 24px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

.extra-item {
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border-radius: 4px;
  border: 1px solid #eee;
  font-size: 14px;
  color: #666;
}

/* 移动设备响应式 */
@media (max-width: 768px) {
  .ultimate-container {
    grid-template-columns: 1fr;
    min-height: auto;
  }
  
  .ultimate-left-column {
    position: static; /* 移动设备上取消固定 */
  }
}
</style>