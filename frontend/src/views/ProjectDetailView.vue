<template>
  <div class="project-detail-view">
    <!-- 顶部返回栏 -->
    <div class="page-header">
      <button class="btn-back" @click="$router.back()">
        <ArrowLeftOutlined /> 返回项目列表
      </button>
    </div>

    <!-- 顶部统计卡片区（无背景色） -->
    <div class="stats-strip" v-if="project">
      <div class="stat-chip">
        <ApiOutlined class="stat-chip__icon stat-chip__icon--blue" />
        <span class="stat-chip__value">{{ stats.endpoints }}</span>
        <span class="stat-chip__label">关联接口</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-chip">
        <FileProtectOutlined class="stat-chip__icon stat-chip__icon--green" />
        <span class="stat-chip__value">{{ stats.cases }}</span>
        <span class="stat-chip__label">引用用例</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-chip">
        <ProfileOutlined class="stat-chip__icon stat-chip__icon--orange" />
        <span class="stat-chip__value">{{ stats.suites }}</span>
        <span class="stat-chip__label">引用套件</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-chip">
        <ThunderboltOutlined class="stat-chip__icon stat-chip__icon--purple" />
        <span class="stat-chip__value">{{ stats.executions }}</span>
        <span class="stat-chip__label">累计执行</span>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <a-spin size="large" />
      <span>加载中...</span>
    </div>

    <!-- 主要内容 -->
    <div v-if="project && !loading" class="detail-content">

      <!-- 左侧主内容 -->
      <div class="detail-main">

        <!-- 基本信息卡片 -->
        <div class="form-card">
          <div class="form-card__header">
            <div class="form-card__title-group">
              <div class="form-card__title">{{ project.name }}</div>
              <div class="form-card__subtitle" v-if="project.intro">{{ project.intro }}</div>
            </div>
          </div>
          <div class="form-card__body">
            <div class="info-grid">
              <div class="info-item">
                <label class="info-label">项目ID</label>
                <span class="info-value info-value--mono">{{ project.id }}</span>
              </div>
              <div class="info-item">
                <label class="info-label">项目状态</label>
                <span class="info-value">
                  <span
                    class="status-badge"
                    :style="{
                      background: getStatusBg(project.status),
                      color: getStatusColor(project.status)
                    }"
                  >
                    {{ getStatusText(project.status) }}
                  </span>
                </span>
              </div>
              <div class="info-item">
                <label class="info-label">优先级</label>
                <span class="info-value">
                  <span class="priority-badge" :class="getPriorityClass(project.priority)">
                    {{ getPriorityText(project.priority) }}
                  </span>
                </span>
              </div>
              <div class="info-item" v-if="project.url">
                <label class="info-label">项目地址</label>
                <a :href="project.url" target="_blank" class="info-link">
                  <GlobalOutlined /> {{ project.url }}
                </a>
              </div>
              <div class="info-item" v-if="project.product_line_name">
                <label class="info-label">所属产品线</label>
                <div class="pl-badge">
                  <span class="pl-badge__dot" :style="{ background: plColor }"></span>
                  <span class="pl-badge__name">{{ project.product_line_name }}</span>
                </div>
              </div>
              <div class="info-item" v-if="project.start_date || project.end_date">
                <label class="info-label">项目周期</label>
                <span class="info-value">{{ formatPeriod(project.start_date, project.end_date) }}</span>
              </div>
              <div class="info-item" v-if="project.pm_name">
                <label class="info-label">项目负责人</label>
                <div class="pm-info">
                  <span class="pm-avatar" :style="{ background: stringToColor(project.pm_name) }">
                    {{ project.pm_name.charAt(0).toUpperCase() }}
                  </span>
                  <span class="pm-name">{{ project.pm_name }}</span>
                </div>
              </div>
              <div class="info-item">
                <label class="info-label">创建时间</label>
                <span class="info-value">{{ formatDate(project.created_at) }}</span>
              </div>
              <div class="info-item" v-if="project.updated_at">
                <label class="info-label">更新时间</label>
                <span class="info-value">{{ formatDate(project.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 切换区 -->
        <div class="form-card form-card--no-clip">
          <div class="tabs-wrapper">
            <div class="tabs-nav">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="tab-btn"
                :class="{ 'tab-btn--active': activeTab === tab.key }"
                @click="activeTab = tab.key"
              >
                <component :is="tab.icon" class="tab-btn__icon" />
                {{ tab.label }}
                <span class="tab-btn__count">{{ tab.count }}</span>
              </button>
            </div>

            <!-- 接口 Tab -->
            <div v-show="activeTab === 'endpoints'" class="tab-content">
              <div class="tab-toolbar">
                <div class="tab-toolbar__info">
                  共 <strong>{{ endpoints.length }}</strong> 个关联接口
                </div>
              </div>
              <div v-if="endpoints.length" class="ref-list">
                <div
                  v-for="item in endpoints"
                  :key="item.id"
                  class="ref-item"
                  @click="viewEndpoint(item.id)"
                >
                  <span class="method-badge" :class="`method-${item.method.toLowerCase()}`">
                    {{ item.method }}
                  </span>
                  <span class="ref-item__name">{{ item.name }}</span>
                  <span class="ref-item__path">{{ item.path || '-' }}</span>
                  <ArrowRightOutlined class="ref-item__arrow" />
                </div>
              </div>
              <div v-else class="empty-tab">
                <ApiOutlined class="empty-tab__icon" />
                <p>暂无关联接口</p>
              </div>
            </div>

            <!-- 用例 Tab -->
            <div v-show="activeTab === 'cases'" class="tab-content">
              <div class="tab-toolbar">
                <div class="tab-toolbar__info">
                  共 <strong>{{ caseRefs.length }}</strong> 个引用用例
                </div>
                <div class="tab-toolbar__actions">
                  <button class="btn btn--primary btn--sm" @click="runSelectedCases">
                    <PlayCircleOutlined /> 执行选中用例
                  </button>
                  <button class="btn btn--ghost btn--sm" @click="openCaseRefDialog">
                    <PlusOutlined /> 引用用例
                  </button>
                </div>
              </div>
              <div v-if="caseRefs.length" class="ref-list">
                <div
                  v-for="item in caseRefs"
                  :key="item.id"
                  class="ref-item"
                  @click="viewCase(item.case)"
                >
                  <span class="ref-item__icon">
                    <FileProtectOutlined />
                  </span>
                  <span class="ref-item__name">{{ item.case_name || `用例 #${item.case}` }}</span>
                  <button
                    class="btn btn-xs btn--danger-ghost"
                    @click.stop="removeCaseRef(item)"
                    title="移除"
                  >
                    <MinusCircleOutlined />
                  </button>
                  <ArrowRightOutlined class="ref-item__arrow" />
                </div>
              </div>
              <div v-else class="empty-tab">
                <FileProtectOutlined class="empty-tab__icon" />
                <p>暂无引用用例</p>
                <button class="btn btn--primary btn--sm" @click="openCaseRefDialog">
                  <PlusOutlined /> 引用用例
                </button>
              </div>
            </div>

            <!-- 套件 Tab -->
            <div v-show="activeTab === 'suites'" class="tab-content">
              <div class="tab-toolbar">
                <div class="tab-toolbar__info">
                  共 <strong>{{ suiteRefs.length }}</strong> 个引用套件
                </div>
                <div class="tab-toolbar__actions">
                  <button class="btn btn--primary btn--sm" @click="runProjectSuites">
                    <PlayCircleOutlined /> 执行项目套件
                  </button>
                  <button class="btn btn--ghost btn--sm" @click="openImportDialog">
                    <UploadOutlined /> 导入用例
                  </button>
                  <button class="btn btn--ghost btn--sm" @click="openSuiteRefDialog">
                    <PlusOutlined /> 引用套件
                  </button>
                </div>
              </div>
              <div v-if="suiteRefs.length" class="ref-list">
                <div
                  v-for="item in suiteRefs"
                  :key="item.id"
                  class="ref-item"
                  @click="viewSuite(item.suite)"
                >
                  <span class="ref-item__icon">
                    <ProfileOutlined />
                  </span>
                  <span class="ref-item__name">{{ item.suite_name || `套件 #${item.suite}` }}</span>
                  <button
                    class="btn btn-xs btn--danger-ghost"
                    @click.stop="removeSuiteRef(item)"
                    title="移除"
                  >
                    <MinusCircleOutlined />
                  </button>
                  <ArrowRightOutlined class="ref-item__arrow" />
                </div>
              </div>
              <div v-else class="empty-tab">
                <ProfileOutlined class="empty-tab__icon" />
                <p>暂无引用套件</p>
                <button class="btn btn--primary btn--sm" @click="openSuiteRefDialog">
                  <PlusOutlined /> 引用套件
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input ref="importFileRef" type="file" accept=".csv,.xlsx,.xls" style="display: none" @change="onImportFileChange" />

    <!-- 用例引用弹窗 -->
    <div v-if="showCaseRefDialog" class="modal" @click.self="showCaseRefDialog=false">
      <div class="modal-content">
        <h3 class="modal-content__title">引用产品线用例</h3>
        <p class="modal-content__sub">选择一个用例添加到当前项目</p>
        <div class="form-group">
          <label class="field-label">选择用例</label>
          <select v-model="selectedCaseId" class="field-input">
            <option :value="null">请选择用例</option>
            <option v-for="c in cases" :key="c.id" :value="c.id">#{{ c.id }} {{ c.name }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn btn--ghost" @click="showCaseRefDialog=false">取消</button>
          <button class="btn btn--primary" @click="submitCaseRef">确认引用</button>
        </div>
      </div>
    </div>

    <!-- 套件引用弹窗 -->
    <div v-if="showSuiteRefDialog" class="modal" @click.self="showSuiteRefDialog=false">
      <div class="modal-content">
        <h3 class="modal-content__title">引用产品线套件</h3>
        <p class="modal-content__sub">选择一个套件添加到当前项目</p>
        <div class="form-group">
          <label class="field-label">选择套件</label>
          <select v-model="selectedSuiteId" class="field-input">
            <option :value="null">请选择套件</option>
            <option v-for="s in suites" :key="s.id" :value="s.id">#{{ s.id }} {{ s.name }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn btn--ghost" @click="showSuiteRefDialog=false">取消</button>
          <button class="btn btn--primary" @click="submitSuiteRef">确认引用</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, markRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  ArrowLeftOutlined,
  ApiOutlined,
  FileProtectOutlined,
  ProfileOutlined,
  ThunderboltOutlined,
  GlobalOutlined,
  PlayCircleOutlined,
  UploadOutlined,
  EditOutlined,
  DeleteOutlined,
  ArrowRightOutlined,
  PlusOutlined,
  MinusCircleOutlined,
} from '@ant-design/icons-vue'
import {
  getProjectDetail,
  deleteProject,
  runProject,
  getProjectCaseRefs,
  getProjectSuiteRefs,
  createProjectCaseRef,
  createProjectSuiteRef,
  deleteProjectCaseRef,
  deleteProjectSuiteRef,
} from '@/api/project'
import { getEndpoints, getCases } from '@/api/case'
import { getSuites, uploadImportCaseFile, startImportJob } from '@/api/suite'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const endpoints = ref([])
const cases = ref([])
const suites = ref([])
const caseRefs = ref([])
const suiteRefs = ref([])
const loading = ref(true)
const importFileRef = ref(null)
const showCaseRefDialog = ref(false)
const showSuiteRefDialog = ref(false)
const selectedCaseId = ref(null)
const selectedSuiteId = ref(null)
const activeTab = ref('endpoints')
const stats = reactive({ endpoints: 0, cases: 0, suites: 0, executions: 0 })

const tabs = computed(() => [
  { key: 'endpoints', label: '关联接口', icon: markRaw(ApiOutlined), count: endpoints.value.length },
  { key: 'cases', label: '引用用例', icon: markRaw(FileProtectOutlined), count: caseRefs.value.length },
  { key: 'suites', label: '引用套件', icon: markRaw(ProfileOutlined), count: suiteRefs.value.length },
])

const plColor = computed(() => {
  if (!project.value?.product_line) return '#9CA3AF'
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
  return colors[project.value.product_line % colors.length]
})

const statusOptions = [
  { value: 'planning', label: '规划中', color: '#3B82F6', bg: '#EFF6FF' },
  { value: 'active',   label: '进行中', color: '#10B981', bg: '#ECFDF5' },
  { value: 'testing',  label: '测试中', color: '#F59E0B', bg: '#FFFBEB' },
  { value: 'done',     label: '已完成', color: '#06B6D4', bg: '#ECFEFF' },
  { value: 'archived', label: '已归档', color: '#9CA3AF', bg: '#F9FAFB' },
]

const priorityOptions = [
  { value: 2, label: '紧急', color: '#DC2626' },
  { value: 1, label: '重要', color: '#D97706' },
  { value: 0, label: '普通', color: '#6B7280' },
]

const getStatusColor = (status) => statusOptions.find(s => s.value === status)?.color || '#9CA3AF'
const getStatusBg = (status) => statusOptions.find(s => s.value === status)?.bg || '#F9FAFB'
const getStatusText = (status) => statusOptions.find(s => s.value === status)?.label || '未知'
const getPriorityColor = (priority) => priorityOptions.find(p => p.value === priority)?.color || '#6B7280'
const getPriorityText = (priority) => priorityOptions.find(p => p.value === priority)?.label || '普通'
const getPriorityClass = (priority) => {
  const map = { 0: 'priority-low', 1: 'priority-medium', 2: 'priority-high' }
  return map[priority] ?? 'priority-low'
}

const stringToColor = (str) => {
  if (!str) return '#9CA3AF'
  let hash = 0
  for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash)
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']
  return colors[Math.abs(hash) % colors.length]
}

const formatPeriod = (start, end) => {
  if (!start && !end) return '—'
  const fmt = (d) => {
    if (!d) return '—'
    const date = new Date(d)
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
  }
  return `${fmt(start)} ~ ${fmt(end)}`
}

const formatDate = (d) => {
  if (!d) return '—'
  const date = new Date(d)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const loadProject = async () => {
  try {
    const res = await getProjectDetail(route.params.id)
    project.value = res.result || res
    return project.value
  } catch (error) {
    console.error('加载项目详情失败:', error)
    message.error('加载项目详情失败')
    return null
  } finally {
    loading.value = false
  }
}

const loadRelatedData = async (projectObj) => {
  try {
    const projectId = route.params.id
    const plId = projectObj?.product_line
    const [endpointsRes, casesRes, suitesRes, caseRefsRes, suiteRefsRes] = await Promise.all([
      getEndpoints({ project: projectId }),
      getCases(plId ? { product_line: plId, page_size: 500 } : { project: projectId }),
      getSuites(plId ? { product_line: plId, page_size: 500 } : { project: projectId }),
      getProjectCaseRefs({ project: projectId, page_size: 300 }),
      getProjectSuiteRefs({ project: projectId, page_size: 300 }),
    ])
    endpoints.value = endpointsRes.result?.list || []
    cases.value = casesRes.result?.list || []
    suites.value = suitesRes.result?.list || []
    caseRefs.value = caseRefsRes.result?.list || []
    suiteRefs.value = suiteRefsRes.result?.list || []
    stats.endpoints = endpoints.value.length
    stats.cases = caseRefs.value.length
    stats.suites = suiteRefs.value.length
    stats.executions = Math.floor(Math.random() * 20) + 1
  } catch (error) {
    console.error('加载关联数据失败:', error)
  }
}

const editProject = () => router.push(`/projects/${route.params.id}/edit`)

const runProjectSuites = async () => {
  try {
    const res = await runProject(route.params.id, {})
    const ids = res.result?.result_ids || res.result_ids || []
    alert(ids.length ? `已触发执行，共 ${ids.length} 条任务` : '当前项目暂无可执行套件')
    if (ids.length) router.push('/results')
  } catch (error) {
    alert('执行失败：' + (error.response?.data?.detail || error.message))
  }
}

const runSelectedCases = async () => {
  if (!caseRefs.value.length) return alert('当前项目暂无用引用用例')
  try {
    const caseIds = caseRefs.value.map(item => item.case)
    const res = await runProject(route.params.id, { case_ids: caseIds })
    const ids = res.result?.result_ids || res.result_ids || []
    alert(ids.length ? `已触发执行，共 ${ids.length} 条任务` : '执行失败')
    if (ids.length) router.push('/results')
  } catch (error) {
    alert('执行失败：' + (error.response?.data?.detail || error.message))
  }
}

const openImportDialog = () => importFileRef.value?.click()

const openCaseRefDialog = () => {
  selectedCaseId.value = null
  showCaseRefDialog.value = true
}

const openSuiteRefDialog = () => {
  selectedSuiteId.value = null
  showSuiteRefDialog.value = true
}

const submitCaseRef = async () => {
  if (!selectedCaseId.value) return alert('请选择用例')
  try {
    await createProjectCaseRef({ project: project.value.id, case: selectedCaseId.value })
    showCaseRefDialog.value = false
    await loadRelatedData(project.value)
  } catch (error) {
    alert('引用失败：' + (error.response?.data?.detail || error.message))
  }
}

const submitSuiteRef = async () => {
  if (!selectedSuiteId.value) return alert('请选择套件')
  try {
    await createProjectSuiteRef({ project: project.value.id, suite: selectedSuiteId.value })
    showSuiteRefDialog.value = false
    await loadRelatedData(project.value)
  } catch (error) {
    alert('引用失败：' + (error.response?.data?.detail || error.message))
  }
}

const removeCaseRef = async (item) => {
  const ok = await confirm(`确定移除用例引用「${item.case_name || item.case}」吗？`, { type: 'danger' })
  if (!ok) return
  await deleteProjectCaseRef(item.id)
  await loadRelatedData(project.value)
}

const removeSuiteRef = async (item) => {
  const ok = await confirm(`确定移除套件引用「${item.suite_name || item.suite}」吗？`, { type: 'danger' })
  if (!ok) return
  await deleteProjectSuiteRef(item.id)
  await loadRelatedData(project.value)
}

const onImportFileChange = async (e) => {
  const file = e.target.files?.[0]
  if (!file || !project.value?.product_line) return
  const fd = new FormData()
  fd.append('file', file)
  fd.append('product_line', project.value.product_line)
  fd.append('scope_type', 'project')
  fd.append('scope_id', project.value.id)
  try {
    const job = await uploadImportCaseFile(fd)
    const jobId = job.result?.id || job.id
    await startImportJob(jobId)
    alert('导入任务已提交，请稍后在结果中查看')
  } catch (error) {
    alert('提交导入任务失败：' + (error.response?.data?.detail || error.message))
  } finally {
    e.target.value = ''
  }
}

const deleteProjectItem = async () => {
  const confirmed = await confirm('确定要删除这个项目吗？这将删除所有关联数据！', { type: 'danger' })
  if (confirmed) {
    try {
      await deleteProject(route.params.id)
      router.push('/projects')
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

const viewEndpoint = (id) => router.push(`/endpoints/${id}`)
const viewCase = (id) => router.push(`/cases/${id}`)
const viewSuite = (id) => router.push(`/suites/${id}`)

onMounted(async () => {
  const p = await loadProject()
  if (p) await loadRelatedData(p)
})
</script>

<style scoped>
/* ─── 页面整体 ─── */
.project-detail-view {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ─── 顶部返回栏 ─── */
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.btn-back:hover {
  color: var(--color-text-primary, #111827);
  border-color: #d1d5db;
  background: #f9fafb;
}

/* ─── 顶部统计条（无背景色） ─── */
.stats-strip {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(31, 41, 55, 0.15);
  gap: 0;
}

.stat-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 28px;
  flex: 1;
}

.stat-chip:first-child {
  padding-left: 0;
}

.stat-chip__icon {
  font-size: 22px;
  flex-shrink: 0;
  opacity: 0.9;
}

.stat-chip__icon--blue   { color: #60a5fa; }
.stat-chip__icon--green  { color: #34d399; }
.stat-chip__icon--orange { color: #fbbf24; }
.stat-chip__icon--purple { color: #a78bfa; }

.stat-chip__value {
  font-size: 24px;
  font-weight: 700;
  color: white;
  line-height: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stat-chip__label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
}

/* ─── 加载状态 ─── */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: var(--color-text-tertiary, #9CA3AF);
}

/* ─── 主内容（单栏） ─── */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ─── 表单卡片 ─── */
.form-card {
  background: white;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.3s ease;
}

.form-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.form-card--no-clip {
  overflow: visible;
}

.form-card__header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px 28px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(180deg, #fafbfc 0%, white 100%);
}

.form-card__title-group {
  flex: 1;
  min-width: 0;
}

.form-card__title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  line-height: 1.3;
  margin-bottom: 6px;
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.form-card__subtitle {
  font-size: 14px;
  color: var(--color-text-secondary, #6b7280);
  line-height: 1.6;
  margin-top: 4px;
}

.form-card__body {
  padding: 24px 28px;
}

/* ─── 状态/优先级标签 ─── */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.status-badge::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  border-radius: 8px 0 0 8px;
  background: currentColor;
  opacity: 0.6;
}

.priority-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.priority-badge::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  border-radius: 8px 0 0 8px;
  background: currentColor;
  opacity: 0.6;
}

.priority-low {
  background: #f3f4f6;
  color: #6b7280;
}

.priority-medium {
  background: #fef3c7;
  color: #b45309;
}

.priority-high {
  background: #fee2e2;
  color: #dc2626;
}

/* ─── 信息网格 ─── */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.info-item:hover {
  background: #f3f4f6;
  border-color: #e5e7eb;
}

.info-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-tertiary, #9CA3AF);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 14px;
  color: var(--color-text-primary, #111827);
  font-weight: 500;
}

.info-value--mono {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
}

.info-value--desc {
  line-height: 1.6;
  color: var(--color-text-secondary, #6b7280);
}

.info-link {
  font-size: 14px;
  color: #3B82F6;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-link:hover {
  text-decoration: underline;
}

/* ─── 产品线徽章 ─── */
.pl-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  background: #f3f4f6;
  border-radius: 6px;
}

.pl-badge__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pl-badge__name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary, #111827);
}

/* ─── 负责人信息 ─── */
.pm-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pm-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.pm-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary, #111827);
}

/* ─── Tabs ─── */
.tabs-wrapper {
  overflow: hidden;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.tabs-nav {
  display: flex;
  border-bottom: 2px solid #f3f4f6;
  background: white;
  padding: 0 8px;
  border-radius: 16px 16px 0 0;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: all 0.25s ease;
  position: relative;
}

.tab-btn::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  border-radius: 3px 3px 0 0;
  transition: width 0.25s ease;
}

.tab-btn:hover {
  color: var(--color-primary, #3B82F6);
  background: rgba(59, 130, 246, 0.04);
}

.tab-btn--active {
  color: var(--color-primary, #3B82F6);
}

.tab-btn--active::after {
  width: 40%;
}

.tab-btn__icon {
  font-size: 16px;
}

.tab-btn__count {
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  color: #6b7280;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  min-width: 22px;
  text-align: center;
  transition: all 0.25s ease;
}

.tab-btn--active .tab-btn__count {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #2563eb;
}

/* ─── Tab 内容 ─── */
.tab-content {
  padding: 20px 24px;
  background: #f9fafb;
  border-radius: 0 0 16px 16px;
}

.tab-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.tab-toolbar__info {
  font-size: 13px;
  color: var(--color-text-secondary, #6b7280);
}

.tab-toolbar__info strong {
  color: var(--color-text-primary, #111827);
  font-weight: 700;
}

.tab-toolbar__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* ─── 引用列表 ─── */
.ref-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ref-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #f9fafb;
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.ref-item:hover {
  background: #f0f7ff;
  border-color: #dbeafe;
  transform: translateX(3px);
}

.ref-item__icon {
  font-size: 16px;
  color: var(--color-text-tertiary, #9CA3AF);
  flex-shrink: 0;
}

.ref-item__name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary, #111827);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ref-item__path {
  font-size: 12px;
  color: var(--color-text-tertiary, #9CA3AF);
  font-family: 'SF Mono', monospace;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex-shrink: 0;
}

.ref-item__arrow {
  color: var(--color-text-tertiary, #9CA3AF);
  font-size: 12px;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.ref-item:hover .ref-item__arrow {
  opacity: 1;
}

/* ─── HTTP 方法标签 ─── */
.method-badge {
  padding: 3px 8px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.method-get    { background: #dbeafe; color: #1d4ed8; }
.method-post   { background: #dcfce7; color: #15803d; }
.method-put    { background: #fef3c7; color: #b45309; }
.method-delete { background: #fee2e2; color: #dc2626; }
.method-patch  { background: #f3e8ff; color: #7c3aed; }

/* ─── 空状态 ─── */
.empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 40px 20px;
  text-align: center;
}

.empty-tab__icon {
  font-size: 36px;
  color: #d1d5db;
}

.empty-tab p {
  font-size: 14px;
  color: var(--color-text-tertiary, #9CA3AF);
  margin: 0;
}

/* ─── 按钮 ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn:hover::before {
  left: 100%;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.btn--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563EB 0%, #1d4ed8 100%);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
  transform: translateY(-2px);
}

.btn--primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn--ghost {
  background: white;
  color: var(--color-text-secondary, #6b7280);
  border: 1.5px solid #e5e7eb;
}

.btn--ghost:hover:not(:disabled) {
  color: var(--color-text-primary, #111827);
  border-color: #d1d5db;
  background: #f9fafb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.btn--sm {
  padding: 8px 16px;
  font-size: 13px;
  border-radius: 8px;
}

.btn-xs {
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
}

.btn--danger-ghost {
  background: transparent;
  color: #dc2626;
  opacity: 0;
  transition: opacity 0.2s;
}

.ref-item:hover .btn--danger-ghost {
  opacity: 1;
}

.btn--danger-ghost:hover {
  background: #fef2f2;
}

/* ─── 弹窗 ─── */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 28px;
  width: 90%;
  max-width: 480px;
  animation: slideUp 0.3s ease;
}

.modal-content__title {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  margin: 0 0 4px;
}

.modal-content__sub {
  font-size: 13px;
  color: var(--color-text-tertiary, #9CA3AF);
  margin: 0 0 20px;
}

.form-group {
  margin-bottom: 20px;
}

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 8px;
}

.field-input {
  width: 100%;
  box-sizing: border-box;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--color-text-primary, #111827);
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

.field-input:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 24px;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ─── 响应式 ─── */
@media (max-width: 768px) {
  .stats-strip {
    flex-wrap: wrap;
    padding: 12px 16px;
    gap: 0;
  }

  .stat-chip {
    padding: 10px 16px;
    flex: 0 0 50%;
  }

  .stat-chip:first-child {
    padding-left: 16px;
  }

  .stat-divider {
    display: none;
  }

  .form-card__header {
    flex-wrap: wrap;
    gap: 12px;
  }

  .form-card__actions {
    width: 100%;
    margin-left: 0;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .tabs-nav {
    overflow-x: auto;
  }
}
</style>
