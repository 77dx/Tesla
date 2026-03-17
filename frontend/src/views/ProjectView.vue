<template>
  <div class="project-view">
    <div class="toolbar">
      <button @click="showCreateDialog = true" class="btn btn-primary">
        ➕ 新建项目
      </button>
      <button @click="loadProjects(1)" class="btn btn-refresh">↻ 刷新</button>
      <button @click="batchDelete" :disabled="!selectedIds.length" class="btn btn-batch-delete">
        🗑 删除选中 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
      </button>
    </div>

    <div class="filter-bar card">
      <div class="filter-input-wrap">
        <span class="filter-icon">🔍</span>
        <input v-model="searchText" class="filter-input" placeholder="搜索项目名称或ID..." @keyup.enter="handleSearch" />
      </div>
      <button @click="handleSearch" class="btn btn-primary btn-sm">搜索</button>
      <button @click="resetFilter" class="btn btn-sm">重置</button>
    </div>
    
    <div class="table-container card">
      <table class="table">
        <thead>
          <tr>
            <th style="width:40px"><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th>
            <th>ID</th>
            <th>项目名称</th>
            <th>描述</th>
            <th>负责人</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in projects" :key="item.id">
            <td><input type="checkbox" :value="item.id" v-model="selectedIds" /></td>
            <td class="cell-sm">{{ item.id }}</td>
            <td class="cell-md" :title="item.name">
              <a @click.prevent="viewDetail(item.id)" class="link-text">{{ item.name }}</a>
            </td>
            <td class="cell-lg" :title="item.intro || ''">{{ item.intro || '-' }}</td>
            <td class="cell-sm">
              <span v-if="item.pm_name" class="pm-tag">
                <span class="pm-avatar">{{ item.pm_name.charAt(0).toUpperCase() }}</span>
                {{ item.pm_name }}
              </span>
              <span v-else>-</span>
            </td>
            <td class="cell-md">{{ formatDate(item.created_at) }}</td>
            <td>
              <button @click="editProject(item)" class="btn-action">编辑</button>
              <button @click="viewDetail(item.id)" class="btn-action btn-info">详情</button>
              <button @click="deleteProjectItem(item.id)" class="btn-action btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="!projects.length" class="empty-state">
        暂无数据
      </div>

      <!-- 分页 -->
      <div v-if="pagination.pageCount > 1" class="pagination">
        <span class="pagination-info">共 {{ pagination.itemCount }} 条</span>
        <button class="page-btn" :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)">‹</button>
        <button v-for="p in pagination.pageCount" :key="p"
          class="page-btn" :class="{ active: p === pagination.page }"
          @click="changePage(p)">{{ p }}</button>
        <button class="page-btn" :disabled="pagination.page >= pagination.pageCount" @click="changePage(pagination.page + 1)">›</button>
      </div>
    </div>
    
    <!-- 创建/编辑对话框 -->
    <div v-if="showCreateDialog" class="modal" @click.self="closeDialog">
      <div class="modal-content">
        <h3>{{ editingItem ? '编辑项目' : '新建项目' }}</h3>
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="form-group">
            <label>项目名称 <span class="required">*</span></label>
            <input v-model="formData.name" :class="{ 'input-error': errors.name }" @input="errors.name = ''"/>
            <span v-if="errors.name" class="error-tip">{{ errors.name }}</span>
          </div>
          <div class="form-group">
            <label>项目简介</label>
            <textarea v-model="formData.intro" rows="4"></textarea>
          </div>
          <div class="form-group">
            <label>项目地址</label>
            <input v-model="formData.url" placeholder="http://example.com" />
          </div>
          <div class="form-group">
            <label>项目负责人</label>
            <select v-model="formData.pm">
              <option :value="null">请选择负责人</option>
              <option v-for="u in userList" :key="u.user_id" :value="u.user_id">{{ u.nickname || u.username }}</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">确定</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects, createProject, updateProject, deleteProject } from '@/api/project'
import { getAllUsers } from '@/api/account'
import { confirm } from '@/composables/useConfirm'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const router = useRouter()
const projects = ref([])
const userList = ref([])
const showCreateDialog = ref(false)
const editingItem = ref(null)
const formData = ref({ name: '', intro: '', url: '', pm: null, product_line: userStore.currentProductLine?.id || null })
const errors = ref({ name: '' })
const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })

const searchText = ref('')

const validate = () => {
  let valid = true
  errors.value = { name: '' }
  if (!formData.value.name.trim()) {
    errors.value.name = '项目名称不能为空'
    valid = false
  }
  return valid
}

const loadProjects = async (page = 1) => {
  try {
    const params = { page, page_size: 10 }
    if (searchText.value) params.search = searchText.value
    if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id
    const res = await getProjects(params)
    projects.value = res.result?.list || []
    pagination.value = {
      page: res.result?.page || 1,
      pageCount: res.result?.pageCount || 1,
      itemCount: res.result?.itemCount || 0,
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

const handleSearch = () => loadProjects(1)
const resetFilter = () => { searchText.value = ''; loadProjects(1) }

const changePage = (page) => { selectedIds.value = []; loadProjects(page) }

const selectedIds = ref([])
const allSelected = computed(() => projects.value.length > 0 && projects.value.every(i => selectedIds.value.includes(i.id)))
const toggleAll = (e) => { selectedIds.value = e.target.checked ? projects.value.map(i => i.id) : [] }
const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const confirmed = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条数据吗？`, { type: 'danger' })
  if (!confirmed) return
  try {
    await Promise.all(selectedIds.value.map(id => deleteProject(id)))
    projects.value = projects.value.filter(i => !selectedIds.value.includes(i.id))
    selectedIds.value = []
  } catch (error) {
    console.error('批量删除失败:', error)
  }
}

const viewDetail = (id) => {
  router.push(`/projects/${id}`)
}

const editProject = (item) => {
  editingItem.value = item
  formData.value = { ...item }
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  if (!validate()) return
  try {
    if (editingItem.value) {
      await updateProject(editingItem.value.id, formData.value)
    } else {
      await createProject(formData.value)
    }
    closeDialog()
    loadProjects()
  } catch (error) {
    const data = error.response?.data
    if (data) {
      // 后端字段级错误：{ name: ['...'], url: ['...'] } 或 { message: '...' }
      if (data.name) errors.value.name = Array.isArray(data.name) ? data.name[0] : data.name
      if (data.url) errors.value.url = Array.isArray(data.url) ? data.url[0] : data.url
      if (!data.name && !data.url) {
        const msg = data.message || data.detail || data.msg || JSON.stringify(data)
        alert('保存失败：' + msg)
      }
    }
  }
}

const deleteProjectItem = async (id) => {
  const confirmed = await confirm('确定要删除这个项目吗？', { type: 'danger' })
  if (confirmed) {
    try {
      await deleteProject(id)
      projects.value = projects.value.filter(p => p.id !== id)
    } catch (error) {
      console.error('删除失败:', error)
    }
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingItem.value = null
  formData.value = { name: '', intro: '', url: '', product_line: userStore.currentProductLine?.id || null }
  errors.value = { name: '', url: '' }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(async () => {
  loadProjects()
  try {
    const res = await getAllUsers()
    userList.value = res.result || res || []
  } catch (e) { console.error('加载用户列表失败:', e) }
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}
.filter-bar { display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px; flex-wrap:nowrap; }
.filter-input-wrap { display:flex; align-items:center; gap:5px; border:1px solid var(--border); border-radius:6px; padding:0 8px; background:white; width:200px; flex-shrink:0; }
.filter-icon { color:var(--text-light); font-size:13px; }
.filter-input { border:none; outline:none; padding:7px 0; font-size:13px; width:100%; background:transparent; }
.filter-select { border:1px solid var(--border); border-radius:6px; padding:7px 8px; font-size:13px; background:white; color:var(--text); outline:none; cursor:pointer; width:120px; flex-shrink:0; }
.filter-select:focus { border-color:var(--accent); }
.btn-sm { padding:7px 14px; font-size:13px; white-space:nowrap; }

.table-container {
  overflow-x: auto;
}

.btn-action {
  padding: 6px 12px;
  margin: 0 4px;
  border: none;
  background: var(--accent);
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.pm-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #e8f4fd;
  color: #1565c0;
  padding: 2px 8px 2px 3px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}
.pm-avatar {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #1565c0;
  color: white;
  font-size: 10px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.btn-action:hover {
  opacity: 0.8;
}

.btn-action.btn-danger {
  background: var(--danger);
}

.btn-action.btn-info {
  background: #3498db;
}

.link-text {
  color: var(--primary);
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
}

.link-text:hover {
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 48px;
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
