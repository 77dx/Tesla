<template>
  <div class="project-detail">
    <div class="detail-header">
      <button @click="$router.back()" class="btn btn-back">← 返回</button>
      <div class="header-actions">
        <button @click="runProjectSuites" class="btn btn-success">执行项目套件</button>
        <button @click="openImportDialog" class="btn btn-secondary">异步导入用例</button>
        <button @click="editProject" class="btn btn-primary">编辑项目</button>
        <button @click="deleteProjectItem" class="btn btn-danger">删除项目</button>
      </div>
    </div>

    <input ref="importFileRef" type="file" accept=".csv,.xlsx,.xls" style="display: none" @change="onImportFileChange" />

    <div v-if="project" class="detail-content">
      <div class="info-card card">
        <h2>{{ project.name }}</h2>
        <div class="info-grid">
          <div class="info-item">
            <label>项目ID</label>
            <span>{{ project.id }}</span>
          </div>
          <div class="info-item">
            <label>项目简介</label>
            <span>{{ project.intro || '-' }}</span>
          </div>
          <div class="info-item">
            <label>项目地址</label>
            <span>{{ project.url || '-' }}</span>
          </div>
          <div class="info-item">
            <label>项目负责人</label>
            <span v-if="project.pm_name" class="pm-tag">
              <span class="pm-avatar">{{ project.pm_name.charAt(0).toUpperCase() }}</span>
              {{ project.pm_name }}
            </span>
            <span v-else>-</span>
          </div>
          <div class="info-item">
            <label>创建时间</label>
            <span>{{ formatDate(project.created_at) }}</span>
          </div>
        </div>
      </div>

      <div class="related-section">
        <div class="section-card card">
          <h3>关联接口 ({{ endpoints.length }})</h3>
          <div class="list-items">
            <div v-for="item in endpoints" :key="item.id" class="list-item" @click="viewEndpoint(item.id)">
              <span class="item-name">{{ item.name }}</span>
              <span class="item-method" :class="`method-${item.method.toLowerCase()}`">{{ item.method }}</span>
            </div>
            <div v-if="!endpoints.length" class="empty-state">暂无关联接口</div>
          </div>
        </div>

        <div class="section-card card">
          <h3>项目引用用例 ({{ caseRefs.length }})</h3>
          <div class="section-actions">
            <button class="btn btn-sm btn-primary" @click="openCaseRefDialog">+ 引用用例</button>
          </div>
          <div class="list-items">
            <div v-for="item in caseRefs" :key="item.id" class="list-item" @click="viewCase(item.case)">
              <span class="item-name">{{ item.case_name || `用例 #${item.case}` }}</span>
              <button class="btn btn-xs btn-danger" @click.stop="removeCaseRef(item)">移除</button>
            </div>
            <div v-if="!caseRefs.length" class="empty-state">暂无引用用例</div>
          </div>
        </div>

        <div class="section-card card">
          <h3>项目引用套件 ({{ suiteRefs.length }})</h3>
          <div class="section-actions">
            <button class="btn btn-sm btn-primary" @click="openSuiteRefDialog">+ 引用套件</button>
          </div>
          <div class="list-items">
            <div v-for="item in suiteRefs" :key="item.id" class="list-item" @click="viewSuite(item.suite)">
              <span class="item-name">{{ item.suite_name || `套件 #${item.suite}` }}</span>
              <button class="btn btn-xs btn-danger" @click.stop="removeSuiteRef(item)">移除</button>
            </div>
            <div v-if="!suiteRefs.length" class="empty-state">暂无引用套件</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCaseRefDialog" class="modal" @click.self="showCaseRefDialog=false">
      <div class="modal-content">
        <h3>引用产品线用例到项目</h3>
        <div class="form-group">
          <label>用例</label>
          <select v-model="selectedCaseId">
            <option :value="null">请选择用例</option>
            <option v-for="c in cases" :key="c.id" :value="c.id">#{{ c.id }} {{ c.name }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="showCaseRefDialog=false">取消</button>
          <button class="btn btn-primary" @click="submitCaseRef">确认</button>
        </div>
      </div>
    </div>

    <div v-if="showSuiteRefDialog" class="modal" @click.self="showSuiteRefDialog=false">
      <div class="modal-content">
        <h3>引用产品线套件到项目</h3>
        <div class="form-group">
          <label>套件</label>
          <select v-model="selectedSuiteId">
            <option :value="null">请选择套件</option>
            <option v-for="s in suites" :key="s.id" :value="s.id">#{{ s.id }} {{ s.name }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="showSuiteRefDialog=false">取消</button>
          <button class="btn btn-primary" @click="submitSuiteRef">确认</button>
        </div>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <div v-if="showEditDialog" class="modal" @click.self="closeDialog">
      <div class="modal-content">
        <h3>编辑项目</h3>
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="form-group">
            <label>项目名称 <span class="required">*</span></label>
            <input v-model="formData.name" :class="{ 'input-error': errors.name }" @input="errors.name = ''"/>
            <span v-if="errors.name" class="error-tip">{{ errors.name }}</span>
          </div>
          <div class="form-group">
            <label>项目简介</label>
            <textarea v-model="formData.intro" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>项目地址</label>
            <input v-model="formData.url" placeholder="http://example.com" />
          </div>
          <div class="form-group">
            <label>项目负责人</label>
            <select v-model="formData.pm">
              <option :value="null">请选择负责人</option>
              <option v-for="u in userList" :key="u.id" :value="u.id">{{ u.profile?.nickname || u.username }}</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProjectDetail, updateProject, deleteProject, runProject, getProjectCaseRefs, getProjectSuiteRefs, createProjectCaseRef, createProjectSuiteRef, deleteProjectCaseRef, deleteProjectSuiteRef } from '@/api/project'
import { getEndpoints, getCases } from '@/api/case'
import { getSuites, uploadImportCaseFile, startImportJob } from '@/api/suite'
import { getAllUsers } from '@/api/account'
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
const importFileRef = ref(null)
const userList = ref([])
const showEditDialog = ref(false)
const showCaseRefDialog = ref(false)
const showSuiteRefDialog = ref(false)
const selectedCaseId = ref(null)
const selectedSuiteId = ref(null)
const errors = ref({ name: '' })
const formData = ref({ name: '', intro: '', url: '', pm: null })

const validate = () => {
  let valid = true
  errors.value = { name: '' }
  if (!formData.value.name.trim()) { errors.value.name = '项目名称不能为空'; valid = false }
  return valid
}

const loadProject = async () => {
  try {
    const res = await getProjectDetail(route.params.id)
    project.value = res.result || res
    formData.value = {
      name: project.value.name,
      intro: project.value.intro || '',
      url: project.value.url || '',
      pm: project.value.pm || null,
    }
    return project.value
  } catch (error) {
    console.error('加载项目详情失败:', error)
    return null
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
      getProjectSuiteRefs({ project: projectId, page_size: 300 })
    ])
    endpoints.value = endpointsRes.result?.list || []
    cases.value = casesRes.result?.list || []
    suites.value = suitesRes.result?.list || []
    caseRefs.value = caseRefsRes.result?.list || []
    suiteRefs.value = suiteRefsRes.result?.list || []
  } catch (error) {
    console.error('加载关联数据失败:', error)
  }
}

const editProject = () => {
  showEditDialog.value = true
}

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

const openImportDialog = () => {
  importFileRef.value?.click()
}

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

const handleSubmit = async () => {
  if (!validate()) return
  try {
    await updateProject(route.params.id, formData.value)
    closeDialog()
    loadProject()
  } catch (error) {
    const data = error.response?.data
    if (data) {
      if (data.name) errors.value.name = Array.isArray(data.name) ? data.name[0] : data.name
      if (data.url) errors.value.url = Array.isArray(data.url) ? data.url[0] : data.url
      if (!data.name && !data.url) {
        const msg = data.message || data.detail || data.msg || JSON.stringify(data)
        alert('保存失败：' + msg)
      }
    }
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

const closeDialog = () => {
  showEditDialog.value = false
  errors.value = { name: '', url: '' }
}

const viewEndpoint = (id) => {
  router.push(`/endpoints/${id}`)
}

const viewCase = (id) => {
  router.push(`/cases/${id}`)
}

const viewSuite = (id) => {
  router.push(`/suites/${id}`)
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(async () => {
  const p = await loadProject()
  if (p) await loadRelatedData(p)
  try {
    const res = await getAllUsers()
    userList.value = res.result || res || []
  } catch (e) { console.error('加载用户列表失败:', e) }
})
</script>

<style scoped>
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.btn-back {
  background: white;
  border: 1px solid var(--border);
  color: var(--text);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.info-card {
  margin-bottom: 32px;
}

.info-card h2 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--primary);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item label {
  font-size: 13px;
  color: var(--text-light);
  font-weight: 500;
}

.info-item span {
  font-size: 15px;
  color: var(--text);
}

.related-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.section-card h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text);
}

.section-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.list-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-item {
  padding: 12px;
  background: var(--bg);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-item:hover {
  background: #e8f4f8;
  transform: translateX(4px);
}

.item-name {
  font-weight: 500;
  color: var(--text);
}

.item-desc {
  font-size: 13px;
  color: var(--text-light);
}

.item-method {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.method-get {
  background: #e3f2fd;
  color: #1976d2;
}

.method-post {
  background: #e8f5e9;
  color: #388e3c;
}

.method-put {
  background: #fff3e0;
  color: #f57c00;
}

.method-delete {
  background: #ffebee;
  color: #d32f2f;
}

.empty-state {
  text-align: center;
  padding: 24px;
  color: var(--text-light);
}

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
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  width: 90%;
  max-width: 500px;
  animation: slideUp 0.3s ease;
}

.modal-content h3 {
  margin-bottom: 24px;
  font-size: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pm-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #e8f4fd;
  color: #1565c0;
  padding: 3px 10px 3px 4px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}
.pm-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #1565c0;
  color: white;
  font-size: 11px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.input-error {
  border-color: var(--danger, #e74c3c) !important;
}

.error-tip {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--danger, #e74c3c);
}
</style>
