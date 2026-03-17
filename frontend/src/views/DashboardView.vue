<template>
  <div class="dashboard">
    <div class="stats-grid">
      <div class="stat-card" @click="$router.push('/projects')">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">📁</div>
        <div class="stat-info">
          <h3>{{ stats.projects }}</h3>
          <p>项目总数</p>
        </div>
      </div>
      
      <div class="stat-card" @click="$router.push('/endpoints')">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">🔗</div>
        <div class="stat-info">
          <h3>{{ stats.endpoints }}</h3>
          <p>接口总数</p>
        </div>
      </div>
      
      <div class="stat-card" @click="$router.push('/cases')">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">📝</div>
        <div class="stat-info">
          <h3>{{ stats.cases }}</h3>
          <p>用例总数</p>
        </div>
      </div>
      
      <div class="stat-card" @click="$router.push('/suites')">
        <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">📦</div>
        <div class="stat-info">
          <h3>{{ stats.suites }}</h3>
          <p>测试套件</p>
        </div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-card">
        <h3>最近执行记录</h3>
        <div class="recent-runs">
          <div v-for="result in recentResults" :key="result.id" class="run-item" @click="viewResult(result.id)">
            <div class="run-info">
              <span class="run-suite">{{ result.suite_name || `套件 #${result.suite}` }}</span>
              <span class="run-time">{{ formatDate(result.created_at) }}</span>
            </div>
            <div class="run-status" :class="getStatusClass(result.status)">
              {{ getStatusText(result.status) }}
            </div>
          </div>
          <div v-if="!recentResults.length" class="empty-state">暂无执行记录</div>
        </div>
      </div>

      <div class="chart-card">
        <h3>快速操作</h3>
        <div class="quick-actions">
          <button @click="$router.push('/projects')" class="action-btn">
            <span class="action-icon">➕</span>
            <span>新建项目</span>
          </button>
          <button @click="$router.push('/endpoints')" class="action-btn">
            <span class="action-icon">🔗</span>
            <span>新建接口</span>
          </button>
          <button @click="$router.push('/cases')" class="action-btn">
            <span class="action-icon">📝</span>
            <span>新建用例</span>
          </button>
          <button @click="$router.push('/suites')" class="action-btn">
            <span class="action-icon">📦</span>
            <span>新建套件</span>
          </button>
        </div>
      </div>
    </div>
    
    <div class="welcome-section">
      <h2>欢迎使用 Tesla 测试平台</h2>
      <p>一个简洁高效的接口自动化测试管理系统</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects } from '@/api/project'
import { getEndpoints, getCases } from '@/api/case'
import { getSuites, getRunResults } from '@/api/suite'

const router = useRouter()

const stats = ref({
  projects: 0,
  endpoints: 0,
  cases: 0,
  suites: 0
})

const recentResults = ref([])

const loadStats = async () => {
  try {
    const [projects, endpoints, cases, suites] = await Promise.all([
      getProjects({ page_size: 1 }),
      getEndpoints({ page_size: 1 }),
      getCases({ page_size: 1 }),
      getSuites({ page_size: 1 })
    ])
    
    stats.value = {
      projects: projects.result?.itemCount || 0,
      endpoints: endpoints.result?.itemCount || 0,
      cases: cases.result?.itemCount || 0,
      suites: suites.result?.itemCount || 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadRecentResults = async () => {
  try {
    const res = await getRunResults({ page_size: 5, ordering: '-id' })
    recentResults.value = res.result?.list || []
  } catch (error) {
    console.error('加载执行记录失败:', error)
  }
}

const viewResult = (id) => {
  router.push(`/results?id=${id}`)
}

const getStatusClass = (status) => {
  const statusMap = {
    0: 'status-init',
    1: 'status-ready',
    2: 'status-running',
    3: 'status-reporting',
    4: 'status-done',
    '-1': 'status-error'
  }
  return statusMap[status] || 'status-init'
}

const getStatusText = (status) => {
  const statusMap = {
    0: '初始化',
    1: '准备开始',
    2: '正在执行',
    3: '生成报告',
    4: '执行完毕',
    '-1': '执行出错'
  }
  return statusMap[status] || '未知'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadStats()
  loadRecentResults()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 12px var(--shadow);
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px var(--shadow-hover);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.stat-info h3 {
  font-size: 32px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.stat-info p {
  color: var(--text-light);
  font-size: 14px;
}

.welcome-section {
  background: white;
  border-radius: 16px;
  padding: 64px 48px;
  text-align: center;
  box-shadow: 0 2px 12px var(--shadow);
}

.welcome-section h2 {
  font-size: 36px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 16px;
}

.welcome-section p {
  font-size: 18px;
  color: var(--text-light);
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px var(--shadow);
}

.chart-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text);
}

.recent-runs {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.run-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--bg);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.run-item:hover {
  background: #e8f4f8;
  transform: translateX(4px);
}

.run-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.run-suite {
  font-weight: 500;
  color: var(--text);
}

.run-time {
  font-size: 12px;
  color: var(--text-light);
}

.run-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-init, .status-ready {
  background: #e3f2fd;
  color: #1976d2;
}

.status-running, .status-reporting {
  background: #fff3e0;
  color: #f57c00;
}

.status-done {
  background: #e8f5e9;
  color: #388e3c;
}

.status-error {
  background: #ffebee;
  color: #d32f2f;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: var(--bg);
  border: 2px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
}

.action-btn:hover {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  transform: translateY(-2px);
}

.action-icon {
  font-size: 20px;
}

.empty-state {
  text-align: center;
  padding: 32px;
  color: var(--text-light);
}
</style>
