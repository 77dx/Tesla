<template>
  <div class="project-detail">
    <div class="detail-header">
      <button @click="$router.back()" class="btn btn-back">← 返回</button>
      <div class="header-actions">
        <button @click="editProject" class="btn btn-primary">编辑项目</button>
        <button @click="deleteProjectItem" class="btn btn-danger">删除项目</button>
      </div>
    </div>

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
          <h3>关联用例 ({{ cases.length }})</h3>
          <div class="list-items">
            <div v-for="item in cases" :key="item.id" class="list-item" @click="viewCase(item.id)">
              <span class="item-name">{{ item.name }}</span>
            </div>
            <div v-if="!cases.length" class="empty-state">暂无关联用例</div>
          </div>
        </div>

        <div class="section-card card">
          <h3>测试套件 ({{ suites.length }})</h3>
          <div class="list-items">
            <div v-for="item in suites" :key="item.id" class="list-item" @click="viewSuite(item.id)">
              <span class="item-name">{{ item.name }}</span>
              <span class="item-desc">{{ item.description || '-' }}</span>
            </div>
            <div v-if="!suites.length" class="empty-state">暂无测试套件</div>
          </div>
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
import { getProjectDetail, updateProject, deleteProject } from '@/api/project'
import { getEndpoints, getCases } from '@/api/case'
import { getSuites } from '@/api/suite'
import { confirm } from '@/composables/useConfirm'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const endpoints = ref([])
const cases = ref([])
const suites = ref([])
const showEditDialog = ref(false)
const errors = ref({ name: '' })
const formData = ref({ name: '', intro: '', url: '' })

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
    }
  } catch (error) {
    console.error('加载项目详情失败:', error)
  }
}

const loadRelatedData = async () => {
  try {
    const projectId = route.params.id
    const [endpointsRes, casesRes, suitesRes] = await Promise.all([
      getEndpoints({ project: projectId }),
      getCases({ project: projectId }),
      getSuites({ project: projectId })
    ])
    endpoints.value = endpointsRes.result?.list || []
    cases.value = casesRes.result?.list || []
    suites.value = suitesRes.result?.list || []
  } catch (error) {
    console.error('加载关联数据失败:', error)
  }
}

const editProject = () => {
  showEditDialog.value = true
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

onMounted(() => {
  loadProject()
  loadRelatedData()
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

.required {
  color: var(--danger, #e74c3c);
  margin-left: 2px;
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
