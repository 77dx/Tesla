<template>
  <div class="dashboard-design">
    <!-- 英雄区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-left">
          <h1 class="hero-title">
            <span class="hero-greeting">{{ greeting }}，</span>
            <span class="hero-name">{{ username }}</span>
            <span class="hero-emoji">👋</span>
          </h1>
          <p class="hero-subtitle">欢迎使用 Tesla 自动化测试平台</p>
          <p class="hero-description">
            专业的测试管理解决方案，覆盖接口测试、UI测试、自动化测试全流程，<br>
            提供多租户支持、异步执行、实时报告等核心功能。
          </p>
          <div class="hero-actions">
            <a-button type="primary" size="large" @click="$router.push('/cases')" class="hero-btn-primary">
              <template #icon><ThunderboltOutlined /></template>
              开始测试
            </a-button>
            <a-button size="large" @click="$router.push('/projects')" class="hero-btn-secondary">
              <template #icon><FolderOutlined /></template>
              查看项目
            </a-button>
          </div>
        </div>
        <div class="hero-right">
          <div class="hero-stats">
            <div class="stat-card">
              <div class="stat-icon">
                <CheckCircleOutlined />
              </div>
              <div class="stat-content">
                <div class="stat-value">95.8%</div>
                <div class="stat-label">平均通过率</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <ClockCircleOutlined />
              </div>
              <div class="stat-content">
                <div class="stat-value">248</div>
                <div class="stat-label">今日执行</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <RocketOutlined />
              </div>
              <div class="stat-content">
                <div class="stat-value">12s</div>
                <div class="stat-label">平均执行时间</div>
              </div>
            </div>
          </div>
          <div class="hero-badge">
            <a-tag color="blue" class="platform-badge">
              <template #icon><RocketOutlined /></template>
              ⚡ Tesla 测试平台 v1.0
            </a-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心功能展示 -->
    <div class="section features-section">
      <div class="section-header">
        <h2 class="section-title">核心功能模块</h2>
        <p class="section-description">一站式自动化测试管理平台，覆盖测试全生命周期</p>
      </div>
      
      <a-row :gutter="[24, 24]" class="features-grid">
        <a-col :xs="24" :sm="12" :lg="8" v-for="feature in features" :key="feature.key">
          <div class="feature-card" @click="$router.push(feature.path)">
            <div class="feature-card-inner">
              <div class="feature-icon-wrapper" :style="{ background: feature.gradient }">
                <component :is="feature.icon" class="feature-icon" />
              </div>
              <div class="feature-content">
                <h3 class="feature-title">{{ feature.title }}</h3>
                <p class="feature-description">{{ feature.desc }}</p>
              </div>
              <div class="feature-footer">
                <span class="feature-action">立即使用 <RightOutlined /></span>
              </div>
            </div>
          </div>
        </a-col>
      </a-row>
    </div>

    <!-- 平台特色优势 -->
    <div class="section advantages-section">
      <div class="section-header">
        <h2 class="section-title">平台特色优势</h2>
        <p class="section-description">Tesla 平台的核心技术优势，为高效测试管理保驾护航</p>
      </div>
      
      <a-row :gutter="[24, 24]" class="advantages-grid">
        <a-col :xs="24" :sm="12" :lg="6" v-for="advantage in advantages" :key="advantage.title">
          <a-card class="advantage-card" :bordered="false">
            <template #cover>
              <div class="advantage-cover" :style="{ background: advantage.color }">
                <component :is="advantage.icon" class="advantage-icon" />
              </div>
            </template>
            <a-card-meta :title="advantage.title" :description="advantage.description" />
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 快速开始指南 -->
    <div class="section quickstart-section">
      <div class="section-header">
        <h2 class="section-title">快速开始指南</h2>
        <p class="section-description">只需六步，即可开始使用 Tesla 平台进行自动化测试</p>
      </div>
      
      <a-steps :current="3" class="quickstart-steps">
        <a-step v-for="(step, index) in steps" :key="index" 
                :title="step.title" 
                :description="step.desc" 
                :icon="step.icon" />
      </a-steps>
      
      <div class="quickstart-actions">
        <a-button type="primary" size="large" @click="$router.push('/projects')">
          创建我的第一个项目
        </a-button>
        <a-button size="large" @click="$router.push('/docs')">
          查看详细文档
        </a-button>
      </div>
    </div>

    <!-- 最近活动与统计 -->
    <div class="section stats-section">
      <a-row :gutter="[24, 24]">
        <a-col :xs="24" :lg="16">
          <a-card title="最近执行记录" class="recent-card">
            <template #extra>
              <a @click="$router.push('/results')">查看全部</a>
            </template>
            <a-table :dataSource="recentActivities" :columns="activityColumns" :pagination="false" size="small">
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'status'">
                  <a-tag :color="record.statusColor">{{ record.status }}</a-tag>
                </template>
                <template v-if="column.key === 'action'">
                  <a-button type="link" size="small" @click="$router.push(`/results/${record.id}`)">
                    查看详情
                  </a-button>
                </template>
              </template>
            </a-table>
          </a-card>
        </a-col>
        
        <a-col :xs="24" :lg="8">
          <a-card title="平台统计数据" class="stats-card">
            <div class="stats-list">
              <div class="stat-item" v-for="stat in stats" :key="stat.title">
                <div class="stat-icon-wrapper" :style="{ color: stat.color }">
                  <component :is="stat.icon" />
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ stat.value }}</div>
                  <div class="stat-title">{{ stat.title }}</div>
                </div>
                <a-progress 
                  :percent="stat.percent" 
                  :stroke-color="stat.color"
                  :show-info="false"
                  size="small"
                  class="stat-progress" />
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 用户反馈 -->
    <div class="section feedback-section">
      <a-card class="feedback-card" :bordered="false">
        <div class="feedback-content">
          <div class="feedback-text">
            <h3 class="feedback-title">用户体验反馈</h3>
            <p class="feedback-quote">"Tesla 平台大幅提升了我们的测试效率，接口测试执行时间缩短了 70%，团队协作更加顺畅。"</p>
            <div class="feedback-author">
              <div class="author-info">
                <div class="author-name">张工程师</div>
                <div class="author-title">某互联网公司测试负责人</div>
              </div>
            </div>
          </div>
          <div class="feedback-actions">
            <a-button type="primary" ghost @click="$router.push('/contact')">联系我们</a-button>
            <a-button @click="$router.push('/cases')">试用平台</a-button>
          </div>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  ThunderboltOutlined,
  FolderOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  RocketOutlined,
  RightOutlined,
  LinkOutlined,
  FileTextOutlined,
  AppstoreAddOutlined,
  GlobalOutlined,
  BarChartOutlined,
  TeamOutlined,
  SyncOutlined,
  SafetyCertificateOutlined,
  CloudServerOutlined,
  UserOutlined,
  PlayCircleOutlined,
  CodeOutlined,
  DatabaseOutlined
} from '@ant-design/icons-vue'

const userStore = useUserStore()

const username = computed(() => {
  const u = userStore.userInfo
  return u?.nickname || u?.username || u?.userInfo?.username || '测试工程师'
})

const now = new Date()
const h = now.getHours()
const greeting = h < 6 ? '凌晨好' : h < 12 ? '早上好' : h < 14 ? '中午好' : h < 18 ? '下午好' : '晚上好'

const features = ref([
  {
    key: 'endpoints',
    title: '接口管理',
    desc: '统一维护项目下的 HTTP 接口，配置请求头、参数、Body，一处定义全局复用',
    path: '/endpoints',
    icon: LinkOutlined,
    gradient: 'linear-gradient(135deg, #1890ff 0%, #36cfc9 100%)'
  },
  {
    key: 'cases',
    title: '用例管理',
    desc: '基于接口创建测试用例，配置前后置脚本、动态变量提取与多维度断言规则',
    path: '/cases',
    icon: FileTextOutlined,
    gradient: 'linear-gradient(135deg, #52c41a 0%, #bae637 100%)'
  },
  {
    key: 'suites',
    title: '套件管理',
    desc: '将多个用例编排成测试套件，按角色分组、顺序执行，支持跨用例变量传递',
    path: '/suites',
    icon: AppstoreAddOutlined,
    gradient: 'linear-gradient(135deg, #722ed1 0%, #eb2f96 100%)'
  },
  {
    key: 'environments',
    title: '环境管理',
    desc: '配置测试/生产等多套环境，管理服务域名映射、全局变量和请求头',
    path: '/environments',
    icon: GlobalOutlined,
    gradient: 'linear-gradient(135deg, #fa8c16 0%, #ffd666 100%)'
  },
  {
    key: 'results',
    title: '执行结果',
    desc: '查看每次套件执行的详细报告，包含用例通过率、断言明细、错误日志',
    path: '/results',
    icon: BarChartOutlined,
    gradient: 'linear-gradient(135deg, #f5222d 0%, #ff7a45 100%)'
  },
  {
    key: 'projects',
    title: '项目管理',
    desc: '按项目隔离接口与用例，支持多项目并行，成员权限精细控制',
    path: '/projects',
    icon: FolderOutlined,
    gradient: 'linear-gradient(135deg, #13c2c2 0%, #87e8de 100%)'
  },
])

const advantages = ref([
  {
    title: '多租户架构',
    description: '基于产品线的多租户设计，支持多团队并行协作，数据安全隔离',
    icon: TeamOutlined,
    color: '#1890ff'
  },
  {
    title: '异步执行',
    description: '基于 Celery + Redis 的高性能异步任务处理，支持高并发测试执行',
    icon: SyncOutlined,
    color: '#52c41a'
  },
  {
    title: 'DAG 驱动执行',
    description: '依赖驱动的有向无环图执行模式，支持复杂业务场景测试',
    icon: CodeOutlined,
    color: '#722ed1'
  },
  {
    title: '企业级安全',
    description: 'JWT 认证、RBAC 权限控制、数据加密传输，保障企业数据安全',
    icon: SafetyCertificateOutlined,
    color: '#fa8c16'
  },
])

const steps = ref([
  { title: '创建项目', desc: '在「项目管理」中新建项目，邀请团队成员', icon: FolderOutlined },
  { title: '定义接口', desc: '在「接口管理」中录入接口 URL、方法与默认参数', icon: LinkOutlined },
  { title: '编写用例', desc: '基于接口创建用例，配置断言与变量提取规则', icon: FileTextOutlined },
  { title: '组装套件', desc: '将用例加入套件，编排执行顺序与角色分组', icon: AppstoreAddOutlined },
  { title: '配置环境', desc: '在「环境管理」中配置域名与全局变量', icon: GlobalOutlined },
  { title: '运行查看', desc: '选择环境一键运行套件，在「执行结果」查看报告', icon: PlayCircleOutlined },
])

const recentActivities = ref([
  {
    id: 1,
    title: '用户登录模块测试',
    status: '成功',
    statusColor: 'green',
    time: '5分钟前',
    project: '用户中心项目',
    duration: '12s'
  },
  {
    id: 2,
    title: '订单创建流程测试',
    status: '进行中',
    statusColor: 'blue',
    time: '15分钟前',
    project: '电商平台',
    duration: '45s'
  },
  {
    id: 3,
    title: '支付接口验证',
    status: '失败',
    statusColor: 'red',
    time: '30分钟前',
    project: '支付系统',
    duration: '8s'
  },
  {
    id: 4,
    title: '性能压力测试',
    status: '成功',
    statusColor: 'green',
    time: '2小时前',
    project: '核心服务',
    duration: '3m'
  },
  {
    id: 5,
    title: '用户权限检查',
    status: '成功',
    statusColor: 'green',
    time: '3小时前',
    project: '用户中心项目',
    duration: '15s'
  }
])

const activityColumns = ref([
  { title: '测试名称', dataIndex: 'title', key: 'title' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '项目', dataIndex: 'project', key: 'project' },
  { title: '耗时', dataIndex: 'duration', key: 'duration' },
  { title: '操作', key: 'action' }
])

const stats = ref([
  {
    title: '总用例数',
    value: '1,248',
    percent: 85,
    color: '#1890ff',
    icon: FileTextOutlined
  },
  {
    title: '总接口数',
    value: '356',
    percent: 65,
    color: '#52c41a',
    icon: LinkOutlined
  },
  {
    title: '总套件数',
    value: '89',
    percent: 45,
    color: '#722ed1',
    icon: AppstoreAddOutlined
  },
  {
    title: '总项目数',
    value: '23',
    percent: 75,
    color: '#fa8c16',
    icon: FolderOutlined
  }
])
</script>

<style scoped>
.dashboard-design {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f5ff 0%, #ffffff 100%);
}

/* 英雄区域 */
.hero-section {
  padding: 80px 0;
  background: linear-gradient(135deg, #1677ff 0%, #597ef7 100%);
  color: white;
  border-radius: 0 0 40px 40px;
  margin-bottom: 60px;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 80px;
}

.hero-left {
  flex: 1;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 16px 0;
}

.hero-greeting {
  opacity: 0.9;
}

.hero-name {
  font-weight: 800;
}

.hero-emoji {
  margin-left: 8px;
}

.hero-subtitle {
  font-size: 20px;
  font-weight: 500;
  opacity: 0.9;
  margin: 0 0 24px 0;
}

.hero-description {
  font-size: 16px;
  opacity: 0.8;
  line-height: 1.6;
  margin: 0 0 40px 0;
}

.hero-actions {
  display: flex;
  gap: 16px;
}

.hero-btn-primary {
  background: white;
  color: #1677ff;
  border: none;
  height: 56px;
  padding: 0 32px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 12px;
}

.hero-btn-primary:hover {
  background: #f0f5ff;
  transform: translateY(-2px);
}

.hero-btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  height: 56px;
  padding: 0 32px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 12px;
}

.hero-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: white;
  transform: translateY(-2px);
}

.hero-right {
  flex-shrink: 0;
}

.hero-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.hero-badge {
  text-align: center;
}

.platform-badge {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 20px;
}

/* 通用章节样式 */
.section {
  max-width: 1200px;
  margin: 0 auto 80px;
  padding: 0 40px;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-title {
  font-size: 36px;
  font-weight: 700;
  color: #1f1f1f;
  margin: 0 0 12px 0;
}

.section-description {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 功能卡片 */
.features-grid {
  margin-bottom: 32px;
}

.feature-card {
  cursor: pointer;
  height: 100%;
}

.feature-card-inner {
  height: 100%;
  padding: 32px;
  background: white;
  border-radius: 20px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.feature-card-inner:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12);
  border-color: transparent;
}

.feature-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.feature-icon {
  font-size: 28px;
  color: white;
}

.feature-content {
  flex: 1;
  margin-bottom: 24px;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f1f1f;
  margin: 0 0 12px 0;
}

.feature-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.feature-footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 20px;
}

.feature-action {
  font-size: 14px;
  font-weight: 500;
  color: #1677ff;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.feature-card-inner:hover .feature-action {
  color: #0958d9;
  transform: translateX(4px);
}

/* 优势卡片 */
.advantages-grid {
  margin-bottom: 32px;
}

.advantage-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.advantage-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.advantage-cover {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.advantage-icon {
  font-size: 48px;
  color: white;
}

/* 快速开始 */
.quickstart-steps {
  margin-bottom: 48px;
}

.quickstart-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

/* 统计卡片 */
.recent-card,
.stats-card {
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  height: 100%;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: #f5f5f5;
}

.stat-icon-wrapper {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1f1f1f;
  margin-bottom: 2px;
}

.stat-title {
  font-size: 14px;
  color: #666;
}

.stat-progress {
  width: 80px;
  flex-shrink: 0;
}

/* 用户反馈 */
.feedback-card {
  background: linear-gradient(135deg, #f6ffed 0%, #e6fffb 100%);
  border-radius: 24px;
  padding: 40px;
}

.feedback-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 60px;
}

.feedback-text {
  flex: 1;
}

.feedback-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f1f1f;
  margin: 0 0 16px 0;
}

.feedback-quote {
  font-size: 18px;
  color: #333;
  line-height: 1.6;
  font-style: italic;
  margin: 0 0 24px 0;
}

.feedback-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-info {
  flex: 1;
}

.author-name {
  font-weight: 600;
  color: #1f1f1f;
  margin-bottom: 2px;
}

.author-title {
  font-size: 14px;
  color: #666;
}

.feedback-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .hero-content {
    gap: 40px;
  }
  
  .hero-title {
    font-size: 48px;
  }
}

@media (max-width: 992px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
  }
  
  .hero-stats {
    flex-direction: row;
    justify-content: center;
  }
  
  .feedback-content {
    flex-direction: column;
    text-align: center;
  }
  
  .quickstart-steps {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .section,
  .hero-content {
    padding: 0 24px;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 18px;
  }
  
  .section-title {
    font-size: 28px;
  }
  
  .hero-actions {
    flex-direction: column;
  }
  
  .hero-stats {
    flex-direction: column;
  }
  
  .features-grid,
  .advantages-grid {
    gap: 16px;
  }
  
  .feature-card-inner {
    padding: 24px;
  }
}

@media (max-width: 576px) {
  .hero-section {
    padding: 60px 0;
    border-radius: 0 0 24px 24px;
  }
  
  .hero-title {
    font-size: 28px;
  }
  
  .hero-description {
    font-size: 14px;
  }
  
  .section {
    margin-bottom: 60px;
  }
  
  .section-title {
    font-size: 24px;
  }
  
  .quickstart-actions {
    flex-direction: column;
  }
}
</style>